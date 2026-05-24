import { Command } from 'commander';
import { createAnalyzeCommand } from './analyze.js';
import { createChatCommand } from './chat.js';
import { createAgentsCommand } from './agents.js';
import { createDoctorCommand } from './doctor.js';
import { registerSummarizeCommand } from './summarize.js';
import { registerConfigCommand } from './config.js';
import { registerHistoryCommand } from './history.js';
import { registerModelsCommand } from './models.js';

export function registerCommands(program: Command) {
  program.addCommand(createAnalyzeCommand());
  program.addCommand(createChatCommand());
  program.addCommand(createAgentsCommand());
  program.addCommand(createDoctorCommand());
  program.addCommand(registerSummarizeCommand());
  program.addCommand(registerConfigCommand());
  program.addCommand(registerHistoryCommand());
  program.addCommand(registerModelsCommand());
}
