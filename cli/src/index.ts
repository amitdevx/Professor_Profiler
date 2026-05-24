import { Command } from 'commander';
import { registerCommands } from './commands/index.js';
import { showBanner } from './ui/components/banner.js';
import { configManager } from './config/configManager.js';
import { preCommandHook } from './hooks/preCommand.js';
import { postCommandHook } from './hooks/postCommand.js';
import { errorHook } from './hooks/errorHook.js';

async function bootstrap() {
  const program = new Command();

  program
    .name('prof')
    .version('1.0.0')
    .description('AI-Powered Exam Paper Analysis CLI');

  program.option('--no-banner', 'Skip the startup banner');
  program.option('--theme <name>', 'Set the UI theme');
  program.showHelpAfterError(true);

  // Register all dynamically loaded commands
  registerCommands(program);

  // Hook into command execution
  program.hook('preAction', async (thisCommand, actionCommand) => {
    const opts = program.opts();
    if (opts.theme) {
      configManager.set('theme', opts.theme);
    }
    
    // Show banner only for primary commands if not explicitly disabled
    if (opts.banner !== false && ['analyze', 'chat'].includes(actionCommand.name())) {
      await showBanner(configManager.get('theme'));
    }

    await preCommandHook({
      commandName: actionCommand.name(),
      args: actionCommand.args,
      startTime: new Date(),
      config: configManager.getAll()
    });
  });

  program.hook('postAction', async (thisCommand, actionCommand) => {
    await postCommandHook({
      commandName: actionCommand.name(),
      args: actionCommand.args,
      startTime: new Date(), // Real start time is handled internally in hook
      config: configManager.getAll()
    });
  });

  // Global error handling
  process.on('uncaughtException', async (error) => {
    await errorHook(error, { commandName: 'unknown', args: [], startTime: new Date(), config: configManager.getAll() });
    process.exit(1);
  });
  
  process.on('unhandledRejection', async (reason) => {
    await errorHook(reason as Error, { commandName: 'unknown', args: [], startTime: new Date(), config: configManager.getAll() });
    process.exit(1);
  });

  // Parse arguments
  if (process.argv.length <= 2) {
    await showBanner(configManager.get('theme'));
    program.help();
  } else {
    await program.parseAsync(process.argv);
  }
}

bootstrap().catch(console.error);
