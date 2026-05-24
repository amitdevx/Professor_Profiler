/**
 * @module agents
 * @description Multi-agent workflow simulation for Professor Profiler.
 * Defines the four processing agents and orchestrates their sequential execution
 * with realistic delays, spinners, and event bus integration.
 */

import chalk from 'chalk';
import ora from 'ora';
import path from 'node:path';

import { eventBus } from '../core/events.js';
import type { AgentResult, AgentTask } from '../types/index.js';
import { agentRenderer } from '../ui/renderers/agentRenderer.js';

/**
 * Delay helper that resolves after `ms` milliseconds.
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Definition of a single simulated agent step.
 */
interface AgentDef {
  /** Display name of the agent. */
  name: string;
  /** Short description of what this agent does. */
  role: string;
  /** Simulated processing time range [min, max] in ms. */
  delayRange: [number, number];
  /** Summary message template (receives the file base name). */
  summaryTemplate: (fileName: string) => string;
}

/**
 * The four agents in the analysis pipeline.
 */
const AGENT_PIPELINE: AgentDef[] = [
  {
    name: 'Parser Agent',
    role: 'Document extraction & structure analysis',
    delayRange: [800, 1500],
    summaryTemplate: (f) => `Extracted structure from "${f}" — 12 sections, 48 questions identified`,
  },
  {
    name: 'Research Agent',
    role: 'Topic classification & syllabus mapping',
    delayRange: [1200, 2200],
    summaryTemplate: (f) => `Mapped 6 topic clusters across 3 difficulty tiers for "${f}"`,
  },
  {
    name: 'Analysis Agent',
    role: 'Deep pattern recognition & trend analysis',
    delayRange: [1500, 2800],
    summaryTemplate: (f) => `Identified 8 recurring patterns and 4 high-frequency topics in "${f}"`,
  },
  {
    name: 'Recommendation Agent',
    role: 'Study plan generation & priority ranking',
    delayRange: [1000, 1800],
    summaryTemplate: (f) => `Generated personalized study plan with 12 prioritized focus areas`,
  },
];

/**
 * Return a random integer in [min, max] (inclusive).
 */
function randomInRange(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Run the simulated multi-agent analysis workflow.
 *
 * Each agent executes sequentially:
 * 1. Spinner starts with the agent's name.
 * 2. A realistic delay simulates processing.
 * 3. The spinner resolves with a success badge and summary.
 * 4. Events are emitted on the {@link eventBus} for each lifecycle step.
 *
 * @param filePath - Absolute or relative path to the file being analyzed.
 * @returns An array of {@link AgentResult} objects for each agent.
 *
 * @example
 * ```ts
 * const results = await simulateAgentWorkflow('/path/to/exam.pdf');
 * ```
 */
export async function simulateAgentWorkflow(filePath: string): Promise<AgentResult[]> {
  const fileName = path.basename(filePath);
  const results: AgentResult[] = [];

  // Build initial task list for progress display
  const tasks: AgentTask[] = AGENT_PIPELINE.map((a, i) => ({
    id: `agent-${i}`,
    name: a.name,
    status: 'pending' as const,
    startTime: new Date(),
    endTime: undefined,
    result: undefined,
  }));

  console.log('');
  console.log(chalk.bold.white('  🚀 Starting Multi-Agent Analysis Pipeline'));
  console.log(chalk.dim('  ─────────────────────────────────────────────'));
  console.log('');

  for (let i = 0; i < AGENT_PIPELINE.length; i++) {
    const agentDef = AGENT_PIPELINE[i]!;
    const task = tasks[i]!;

    // Mark as running
    task.status = 'running';
    task.startTime = new Date();

    // Emit start event
    eventBus.emit('agent:start', { agentName: agentDef.name, filePath } as any);

    // Show spinner
    agentRenderer.renderAgentStart(agentDef.name);

    // Simulate processing
    const processingTime = randomInRange(...agentDef.delayRange);
    await delay(processingTime);

    // Build result
    const result: AgentResult = {
      agentName: agentDef.name,
      success: true,
      data: agentDef.summaryTemplate(fileName),
      error: null,
      duration: processingTime,
    };

    // Mark as completed
    task.status = 'completed';
    task.endTime = new Date();
    task.result = result;

    // Show completion
    agentRenderer.renderAgentComplete(agentDef.name, result);

    // Emit complete event
    eventBus.emit('agent:complete', {
      agentName: agentDef.name,
      result,
      filePath,
    } as any);

    results.push(result);
  }

  console.log('');
  return results;
}

/**
 * Get metadata for all agents in the pipeline.
 *
 * @returns An array of objects with agent `name`, `role`, and default `model`.
 */
export function getAgentDefinitions(): Array<{ name: string; role: string; model: string; status: string }> {
  return AGENT_PIPELINE.map((a) => ({
    name: a.name,
    role: a.role,
    model: 'meta/llama-3.1-70b-instruct',
    status: 'ready',
  }));
}

import { ProcessTransport } from '../transport/processTransport.js';

export async function runRealAgentWorkflow(filePath: string, agentName: string = 'all'): Promise<AgentResult[]> {
  const fileName = path.basename(filePath);
  const results: AgentResult[] = [];
  const tasks: AgentTask[] = [];
  
  console.log('');
  console.log(chalk.bold.white('  🚀 Starting Multi-Agent Analysis Pipeline'));
  console.log(chalk.dim('  ─────────────────────────────────────────────'));
  console.log('');

  const transport = new ProcessTransport('python3');
  const controller = new AbortController();
  
  // Handle SIGINT gracefully during analysis
  const sigintHandler = () => {
    controller.abort();
  };
  process.on('SIGINT', sigintHandler);

  let currentAgent = '';
  let startTime = Date.now();
  let fullOutput = '';

  try {
    for await (const line of transport.stream({ file: filePath, agentName }, controller.signal)) {
      fullOutput += line + '\n';
      
      // Look for agent processing logs: "[Research Agent] processing..."
      const match = line.match(/^\[(.*?)\] processing/);
      if (match && match[1]) {
        const agentName = match[1];
        if (currentAgent !== agentName) {
          if (currentAgent !== '') {
            agentRenderer.renderAgentComplete(currentAgent, {
              agentName: currentAgent, success: true, duration: Date.now() - startTime, data: ''
            });
            results.push({ agentName: currentAgent, success: true, duration: Date.now() - startTime, data: '' });
          }
          currentAgent = agentName;
          startTime = Date.now();
          agentRenderer.renderAgentStart(currentAgent);
        }
      }
      
      // Look for final report start
      if (line.includes('ANALYSIS REPORT GENERATED SUCCESSFULLY')) {
        if (currentAgent !== '') {
           agentRenderer.renderAgentComplete(currentAgent, {
              agentName: currentAgent, success: true, duration: Date.now() - startTime, data: ''
            });
           results.push({ agentName: currentAgent, success: true, duration: Date.now() - startTime, data: '' });
           currentAgent = '';
        }
      }
    }
  } catch (e) {
    if (currentAgent !== '') {
      agentRenderer.renderAgentComplete(currentAgent, {
         agentName: currentAgent, success: false, duration: Date.now() - startTime, error: String(e), data: ''
      });
    }
  } finally {
    process.removeListener('SIGINT', sigintHandler);
    if (currentAgent !== '') {
       agentRenderer.renderAgentComplete(currentAgent, {
          agentName: currentAgent, success: true, duration: Date.now() - startTime, data: ''
       });
       results.push({ agentName: currentAgent, success: true, duration: Date.now() - startTime, data: '' });
    }
  }
  
  console.log('');
  return results;
}
