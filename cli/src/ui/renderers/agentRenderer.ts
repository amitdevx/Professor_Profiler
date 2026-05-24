/**
 * @module ui/renderers/agentRenderer
 * @description Renders multi-agent workflow progress in the terminal.
 * Each agent gets a uniquely colored spinner and completion badge.
 */

import ora, { type Ora } from 'ora';
import chalk from 'chalk';

import type { AgentResult, AgentTask } from '../../types/index.js';

/**
 * Color map assigning a unique chalk color to each known agent.
 */
const AGENT_COLORS: Record<string, (text: string) => string> = {
  'Parser Agent': chalk.cyan,
  'Research Agent': chalk.yellow,
  'Analysis Agent': chalk.magenta,
  'Recommendation Agent': chalk.green,
  'Strategist': chalk.green,
};

/**
 * Emoji map for each agent.
 */
const AGENT_ICONS: Record<string, string> = {
  'Parser Agent': '📄',
  'Research Agent': '🔍',
  'Analysis Agent': '🧠',
  'Recommendation Agent': '✨',
  'Strategist': '🎯',
};

/**
 * Resolve a chalk color function for a given agent name.
 *
 * @param agentName - The agent's display name.
 * @returns A chalk color function.
 */
function colorFor(agentName: string): (text: string) => string {
  return AGENT_COLORS[agentName] ?? chalk.white;
}

/**
 * Resolve an icon for a given agent name.
 *
 * @param agentName - The agent's display name.
 * @returns An emoji icon string.
 */
function iconFor(agentName: string): string {
  return AGENT_ICONS[agentName] ?? '⚙';
}

/**
 * Renders agent lifecycle events (start, progress, complete) to the terminal.
 */
export class AgentRenderer {
  /** Active ora spinners keyed by agent name. */
  private spinners: Map<string, Ora> = new Map();

  /**
   * Show a spinner indicating an agent has started processing.
   *
   * @param agentName - The agent's display name.
   */
  renderAgentStart(agentName: string): void {
    const color = colorFor(agentName);
    const icon = iconFor(agentName);
    const spinner = ora({
      text: color(`${icon}  ${agentName} is processing...`),
      spinner: 'dots',
      color: 'cyan',
    }).start();

    this.spinners.set(agentName, spinner);
  }

  /**
   * Mark an agent as complete, replacing the spinner with a success or failure badge.
   *
   * @param agentName - The agent's display name.
   * @param result    - The {@link AgentResult} containing outcome details.
   */
  renderAgentComplete(agentName: string, result: AgentResult): void {
    const spinner = this.spinners.get(agentName);
    const color = colorFor(agentName);
    const icon = iconFor(agentName);
    const duration = result.duration ? chalk.dim(` (${result.duration}ms)`) : '';

    if (result.success) {
      const message = `${icon}  ${color(agentName)} ${chalk.green.bold('✔ DONE')}${duration}`;
      if (spinner) {
        spinner.succeed(message);
      } else {
        console.log(`  ${message}`);
      }

      // Show summary data if available
      if (result.data && typeof result.data === 'string') {
        console.log(chalk.dim(`     └─ ${result.data}`));
      }
    } else {
      const message = `${icon}  ${color(agentName)} ${chalk.red.bold('✖ FAILED')}${duration}`;
      if (spinner) {
        spinner.fail(message);
      } else {
        console.log(`  ${message}`);
      }

      if (result.error) {
        console.log(chalk.red(`     └─ ${result.error}`));
      }
    }

    this.spinners.delete(agentName);
  }

  /**
   * Render a summary table of all agent tasks and their current status.
   *
   * @param agents - Array of {@link AgentTask} objects to display.
   */
  renderAgentProgress(agents: AgentTask[]): void {
    console.log('');
    console.log(chalk.bold.white('  Agent Pipeline Status'));
    console.log(chalk.dim('  ─────────────────────────────────────'));

    for (const agent of agents) {
      const color = colorFor(agent.name);
      const icon = iconFor(agent.name);
      let statusBadge: string;

      switch (agent.status) {
        case 'running':
          statusBadge = chalk.bgCyan.black(' RUNNING ');
          break;
        case 'completed':
          statusBadge = chalk.bgGreen.black(' DONE ');
          break;
        case 'failed':
          statusBadge = chalk.bgRed.white(' FAILED ');
          break;
        case 'pending':
        default:
          statusBadge = chalk.bgGray.white(' PENDING ');
          break;
      }

      console.log(`  ${icon}  ${color(agent.name.padEnd(24))} ${statusBadge}`);
    }

    console.log('');
  }

  /**
   * Stop all active spinners (used during cleanup / abort).
   */
  stopAll(): void {
    for (const [name, spinner] of this.spinners) {
      spinner.stop();
      this.spinners.delete(name);
    }
  }
}

/**
 * Pre-instantiated singleton for convenience.
 */
export const agentRenderer = new AgentRenderer();
