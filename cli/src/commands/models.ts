import { Command } from 'commander';
import Table from 'cli-table3';
import chalk from 'chalk';
import { configManager } from '../config/configManager.js';

export function registerModelsCommand(): Command {
  const cmd = new Command('models');
  cmd.alias('m');
  cmd.description('List available AI models');

  cmd.action(() => {
    const config = configManager.getAll();
    const activeModel = config.model;

    const table = new Table({
      head: [chalk.cyan('Provider'), chalk.cyan('Model Name'), chalk.cyan('Type'), chalk.cyan('Status')],
      style: { head: [], border: [] }
    });

    const models = [
      { provider: 'NVIDIA NIM', name: 'meta/llama-3.1-70b-instruct', type: 'Classifier' },
      { provider: 'NVIDIA NIM', name: 'meta/llama-3.3-70b-instruct', type: 'Analyzer' },
      { provider: 'Google Gemini', name: 'gemini-2.0-flash-exp', type: 'Classifier (Fallback)' },
      { provider: 'Google Gemini', name: 'gemini-2.0-pro-exp', type: 'Analyzer (Fallback)' }
    ];

    models.forEach(m => {
      const isActive = m.name === activeModel || (m.provider.includes(config.provider.toUpperCase()));
      const status = isActive ? chalk.green('Active') : chalk.gray('Available');
      const name = isActive ? chalk.bold(m.name) : m.name;
      table.push([m.provider, name, m.type, status]);
    });

    console.log(`\n${chalk.bold('Available AI Models')}`);
    console.log(table.toString());
  });

  return cmd;
}
