import { CLIConfig, AgentTask } from '../types/index.js';

export interface AnalyzeOptions {
  force?: boolean;
}

export interface ProfSDK {
  analyze(filePath: string, options?: AnalyzeOptions): Promise<any>;
  chat(message: string): Promise<string>;
  getAgents(): AgentTask[];
  getConfig(): CLIConfig;
}
