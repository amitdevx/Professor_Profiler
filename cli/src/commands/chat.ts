/**
 * @module commands/chat
 * @description The `prof chat` command — interactive AI REPL.
 * Provides a readline-based chat loop with slash command support
 * and simulated AI streaming responses.
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs-extra';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { fileService } from '../services/fileService.js';

import { customReplPrompt } from '../ui/components/repl.js';
import { pythonRunner } from '../services/pythonRunner.js';
import { renderMarkdown } from '../ui/renderers/markdownRenderer.js';
import type { StreamChunk } from '../types/index.js';

/**
 * Simulated AI response fragments for the mock provider.
 */
const MOCK_RESPONSES: string[] = [
  "Based on my analysis of past exam patterns, I can see that **Chapter 5: Thermodynamics** has been a consistently high-yield topic.\n\n### Key Focus Areas:\n\n1. **First Law of Thermodynamics** — appears in 78% of papers\n2. **Carnot Cycle** — frequently tested with numerical problems\n3. **Entropy** — conceptual questions are common\n\n> 💡 **Pro tip:** Focus on solving at least 15 numerical problems from this chapter to build speed.\n\nWould you like me to generate a detailed study plan for this topic?",
  "Here's a breakdown of the **question pattern distribution** I found:\n\n| Question Type | Frequency | Avg. Marks |\n|---|---|---|\n| Short Answer | 42% | 2-3 marks |\n| Long Answer | 28% | 8-10 marks |\n| Numerical | 20% | 5-6 marks |\n| MCQ | 10% | 1 mark |\n\nThe trend shows a **shift toward more numerical questions** in recent years. I'd recommend practicing timed problem-solving sessions.",
  "I've identified **3 recurring themes** across the last 5 exam papers:\n\n1. 🔬 **Practical applications** — 65% of long-answer questions require real-world examples\n2. 📐 **Derivations** — At least 2 derivation questions appear in every paper\n3. 🔗 **Inter-topic connections** — Questions often link concepts from different chapters\n\n### Recommended Strategy:\n- Create a **concept map** connecting related topics\n- Practice writing structured answers within time limits\n- Review all diagrams from the textbook",
];

/**
 * Generate a mock streaming response as an async generator.
 *
 * @param message - The user's input message (used to seed response selection).
 * @yields {@link StreamChunk} objects with character-by-character tokens.
 */
async function* mockStreamResponse(message: string): AsyncGenerator<StreamChunk, void, unknown> {
  // Pick a response based on message hash
  const hash = [...message].reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const response = MOCK_RESPONSES[hash % MOCK_RESPONSES.length]!;

  // Yield status chunk first
  yield { token: 'Thinking...', agentName: 'AI', timestamp: new Date(), type: 'status' as const };

  // Simulate processing delay
  await new Promise((r) => setTimeout(r, 500));

  // Stream the response word-by-word for natural feel
  const words = response.split(' ');
  for (let i = 0; i < words.length; i++) {
    const separator = i === 0 ? '' : ' ';
    yield {
      token: separator + words[i],
      agentName: 'AI',
      timestamp: new Date(),
      type: 'text' as const,
    };
    // Slight delay between words for natural pacing
    await new Promise((r) => setTimeout(r, 15 + Math.random() * 25));
  }
}

/**
 * Create and return the `chat` command.
 *
 * **Usage:** `prof chat`
 * **Alias:** `c`
 *
 * @returns A configured Commander {@link Command} object.
 */
export function createChatCommand(): Command {
  const cmd = new Command('chat')
    .alias('c')
    .description('Start an interactive AI chat session')
    .action(async () => {
      const history: string[] = [];
      const responseTimes: number[] = [];

      console.log('');
      console.log(chalk.bold.hex('#4cc9f0')('  💬 Interactive Chat Mode'));
      console.log(chalk.dim('  ─────────────────────────────────────'));
      console.log(chalk.dim('  Commands: /exit, /clear, /history, /help'));
      console.log(chalk.dim('  Files:    Type @<filepath> to attach a file to your prompt.'));
      console.log(chalk.dim('  Type your question and press Enter.'));
      console.log('');

      const promptText = chalk.hex('#f72585').bold('  prof › ');

      // Main REPL loop
      let running = true;
      while (running) {
        const userInput = await customReplPrompt(promptText);

        if (userInput === null) {
          break;
        }

        const trimmed = userInput.trim();

        if (!trimmed) continue;

        // Handle slash commands
        if (trimmed.startsWith('/')) {
          switch (trimmed.toLowerCase()) {
            case '/exit':
            case '/quit':
            case '/q':
              console.log('');
              console.log(chalk.dim('  👋 Goodbye! Session ended.'));
              console.log('');
              running = false;
              continue;

            case '/clear':
              console.clear();
              console.log(chalk.dim('  🧹 Screen cleared.'));
              console.log('');
              continue;

            case '/history':
              if (history.length === 0) {
                console.log(chalk.dim('  📭 No messages in this session yet.'));
              } else {
                console.log('');
                console.log(chalk.bold.white('  Chat History'));
                console.log(chalk.dim('  ────────────'));
                history.forEach((msg, i) => {
                  console.log(chalk.dim(`  ${i + 1}.`) + ` ${chalk.white(msg)}`);
                });
              }
              console.log('');
              continue;

            case '/help':
              console.log('');
              console.log(chalk.bold.white('  Available Commands'));
              console.log(chalk.dim('  ──────────────────'));
              console.log(`  ${chalk.cyan('/exit')}     Exit the chat session`);
              console.log(`  ${chalk.cyan('/clear')}    Clear the screen`);
              console.log(`  ${chalk.cyan('/history')}  Show message history`);
              console.log(`  ${chalk.cyan('/help')}     Show this help`);
              console.log('');
              continue;

            default:
              console.log(chalk.yellow(`  Unknown command: ${trimmed}. Type /help for options.`));
              console.log('');
              continue;
          }
        }

        // Inline @file attachment parsing
        let finalPrompt = trimmed;
        let attachmentFailed = false;
        const fileMentions = trimmed.match(/@([^\s]+)/g);
        if (fileMentions) {
          console.log('');
          for (const mention of fileMentions) {
            try {
              const fileInfo = fileService.resolveFilePath(mention);
              const validation = fileService.validateFile(fileInfo);
              if (validation.valid) {
                const content = await fileService.readFileText(fileInfo);
                finalPrompt += `\n\n--- Contents of ${fileInfo.name} ---\n${content}\n`;
                console.log(chalk.dim(`  📎 Attached: ${chalk.white(fileInfo.name)}`));
              } else {
                console.log(chalk.yellow(`  ⚠️ Failed to attach ${mention}: ${validation.error}`));
                attachmentFailed = true;
              }
            } catch (e) {
              console.log(chalk.yellow(`  ⚠️ Failed to read ${mention}`));
              attachmentFailed = true;
            }
          }
        }

        if (attachmentFailed) {
          console.log('');
          continue;
        }

        // Do not record user prompt in history immediately.
        // We will record it alongside the AI's response to maintain perfect pairs.

        console.log('');
        const startTime = Date.now();
        const responseText = await pythonRunner.runChatStream(finalPrompt, 'chat', history);
        const elapsed = (Date.now() - startTime) / 1000;
        if (responseText) {
          // Push both user input and response to maintain context
          history.push(finalPrompt);
          history.push(responseText);
          responseTimes.push(elapsed);
          
          const avg = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
          console.log(chalk.dim.italic(`  ⏱️  AI Response Time: ${elapsed.toFixed(1)}s (Session Avg: ${avg.toFixed(1)}s)`));
        }
        console.log('');
      }
    });

  return cmd;
}
