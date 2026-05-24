import { Command } from 'commander';
import { stateManager } from '../state/stateManager.js';
import chalk from 'chalk';

export function registerHistoryCommand(): Command {
  const cmd = new Command('history');
  cmd.alias('h');
  cmd.description('Show session history');

  cmd.action(async () => {
    try {
      const fsExtra = await import('fs-extra');
      const fs = fsExtra.default || fsExtra;
      const path = await import('node:path');
      const os = await import('node:os');
      const Table = (await import('cli-table3')).default;
      const chalk = (await import('chalk')).default;

      const historyFile = path.join(os.homedir(), '.professor-profiler', 'history.json');
      if (!(await fs.pathExists(historyFile))) {
        console.log(chalk.dim('No history available.'));
        return;
      }
      
      const history: any[] = await fs.readJson(historyFile);
      if (history.length === 0) {
        console.log(chalk.dim('No history available.'));
        return;
      }

      console.log('');
      console.log(chalk.bold.white('  📚 Analysis History'));
      console.log(chalk.dim('  ───────────────────────────────────────────'));
      console.log('');

      const table = new Table({
        head: [chalk.cyan('Date'), chalk.cyan('Command'), chalk.cyan('Arguments'), chalk.cyan('Duration')],
        style: { head: [], border: [] }
      });

      history.slice(0, 10).forEach((entry) => {
        const date = new Date(entry.timestamp).toLocaleString();
        const durationStr = (entry.duration / 1000).toFixed(1) + 's';
        const argsStr = entry.args ? entry.args.join(' ') : '';
        table.push([date, entry.command, argsStr, durationStr]);
      });

      console.log(table.toString());
      console.log('');
    } catch (e) {
      console.error('Failed to load history:', e);
    }
  });

  cmd.command('clear')
    .description('Clear history')
    .action(async () => {
      const fsExtra = await import('fs-extra');
      const fs = fsExtra.default || fsExtra;
      const path = await import('node:path');
      const os = await import('node:os');
      const historyFile = path.join(os.homedir(), '.professor-profiler', 'history.json');
      if (await fs.pathExists(historyFile)) {
        await fs.remove(historyFile);
      }
      stateManager.clearHistory();
      console.log(chalk.green('✓ History cleared.'));
    });

  return cmd;
}
