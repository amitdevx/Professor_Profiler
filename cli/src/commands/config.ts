import { Command } from 'commander';
import { configManager } from '../config/configManager.js';
import Table from 'cli-table3';
import chalk from 'chalk';

export function registerConfigCommand(): Command {
  const cmd = new Command('config');
  cmd.alias('cfg');
  cmd.description('Manage CLI configuration');

  cmd.command('list')
    .description('List current configuration')
    .action(() => {
      const config = configManager.getAll();
      const table = new Table({ 
        head: [chalk.cyan('Key'), chalk.cyan('Value')],
        style: { head: [], border: [] }
      });
      table.push(['Provider', config.provider]);
      table.push(['Model', config.model]);
      table.push(['Theme', config.theme]);
      table.push(['Output Dir', config.outputDir]);
      table.push(['Telemetry', config.telemetryEnabled ? 'Enabled' : 'Disabled']);
      console.log(table.toString());
    });

  cmd.command('set <key> <value>')
    .description('Set a configuration value')
    .action(async (key, value) => {
      if (key === 'telemetryEnabled') {
        configManager.set(key, value === 'true');
      } else {
        configManager.set(key as any, value);
      }
      await configManager.save();
      console.log(chalk.green(`✓ Set ${key} to ${value}`));
    });

  cmd.command('get <key>')
    .description('Get a configuration value')
    .action((key) => {
      const val = configManager.get(key as any);
      console.log(`${key}: ${val}`);
    });

  cmd.command('reset')
    .description('Reset configuration to defaults')
    .action(async () => {
      await configManager.reset();
      console.log(chalk.green('✓ Configuration reset to defaults'));
    });

  return cmd;
}
