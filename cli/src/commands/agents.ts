/**
 * @module commands/agents
 * @description The `prof agents` command — displays a beautiful table of available agents.
 */

import { Command } from 'commander';
import Table from 'cli-table3';
import chalk from 'chalk';

import { getAgentDefinitions } from '../agents/index.js';

/**
 * Create and return the `agents` command.
 *
 * **Usage:** `prof agents`
 * **Alias:** `ag`
 *
 * @returns A configured Commander {@link Command} object.
 */
export function createAgentsCommand(): Command {
  const cmd = new Command('agents')
    .alias('ag')
    .description('List all available AI agents and their roles')
    .action(() => {
      const agents = getAgentDefinitions();

      console.log('');
      console.log(chalk.bold.white('  🤖 Available Agents'));
      console.log('');

      const table = new Table({
        head: [
          chalk.cyan.bold('Agent'),
          chalk.cyan.bold('Model'),
          chalk.cyan.bold('Role'),
          chalk.cyan.bold('Status'),
        ],
        style: {
          head: [],
          border: ['dim'],
          compact: false,
        },
        colWidths: [25, 28, 42, 12],
        wordWrap: true,
      });

      /**
       * Agent-specific colors for the name column.
       */
      const agentColors: Record<string, (text: string) => string> = {
        'Parser Agent': chalk.cyan,
        'Research Agent': chalk.yellow,
        'Analysis Agent': chalk.magenta,
        'Recommendation Agent': chalk.green,
      };

      for (const agent of agents) {
        const colorFn = agentColors[agent.name] ?? chalk.white;
        const statusBadge =
          agent.status === 'ready'
            ? chalk.bgGreen.black(' READY ')
            : chalk.bgYellow.black(' BUSY  ');

        table.push([
          colorFn(agent.name),
          chalk.dim(agent.model),
          chalk.white(agent.role),
          statusBadge,
        ]);
      }

      console.log(table.toString());
      console.log('');
      console.log(chalk.dim(`  Total: ${agents.length} agents registered`));
      console.log('');
    });

  return cmd;
}
