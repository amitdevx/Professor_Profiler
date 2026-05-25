import { Command } from 'commander';
import { fileService } from '../services/fileService.js';
import { renderMarkdown } from '../ui/renderers/markdownRenderer.js';
import { pythonRunner } from '../services/pythonRunner.js';
import chalk from 'chalk';
import boxen from 'boxen';
import fs from 'fs-extra';

export function registerSummarizeCommand(): Command {
  const cmd = new Command('summarize');
  cmd.alias('s');
  cmd.description('Summarize a document using AI');
  cmd.argument('<file>', 'File to summarize (use @ prefix for local files)');
  
  cmd.action(async (file: string) => {
    try {
      console.log(chalk.blue(`\nInitializing summarization for ${file}...`));
      const fileInfo = fileService.resolveFilePath(file);
      const validation = fileService.validateFile(fileInfo);
      
      if (!validation.valid) {
        console.error(chalk.red(`Error: ${validation.error}`));
        return;
      }
      
      console.log(chalk.yellow('Starting AI summarization...'));
      const content = await fileService.readFileText(fileInfo);
      const prompt = `Please summarize the following document:\n\n--- Contents of ${fileInfo.name} ---\n${content}`;
      await pythonRunner.runChatStream(prompt, 'summarizer');
    } catch (e: any) {
      console.error(chalk.red(`Failed to summarize: ${e.message}`));
    }
  });
  
  return cmd;
}
