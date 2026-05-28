/**
 * @module commands/analyze
 * @description The `prof analyze` command — the primary analysis workflow.
 * Resolves an @file, validates it, copies it to the processing folder,
 * runs the simulated multi-agent pipeline, and displays a completion summary.
 */

import { Command } from 'commander';
import boxen from 'boxen';
import chalk from 'chalk';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../../');

import { fileService } from '../services/fileService.js';
import { runRealAgentWorkflow } from '../agents/index.js';
import { showError } from '../ui/components/errorDisplay.js';

/**
 * Create and return the `analyze` command.
 *
 * **Usage:** `prof analyze @exam.pdf`
 * **Alias:** `a`
 *
 * @returns A configured Commander {@link Command} object.
 */
export function createAnalyzeCommand(): Command {
  const cmd = new Command('analyze')
    .alias('a')
    .description('Analyze an exam paper using the multi-agent AI pipeline')
    .argument('<file>', 'Path to the file to analyze')
    .argument('[agent]', 'Optional agent to run directly (e.g. @taxonomist)')
    .option('-o, --output <dir>', 'Output directory for results', process.cwd())
    .action(async (fileArg: string, agentArg: string | undefined, options: { output: string; copy: boolean }) => {
      // If Commander places the options object in agentArg because it's missing, handle it
      if (agentArg && typeof agentArg === 'object') {
        options = agentArg;
        agentArg = undefined;
      }
      
      const agentName = agentArg ? (agentArg.startsWith('@') ? agentArg.slice(1) : agentArg) : 'all';
      try {
        const fileInfo = fileService.resolveFilePath(fileArg);
        console.log('');
        console.log(chalk.dim(`  📁 Resolved: ${chalk.white(fileInfo.path)}`));
        console.log(chalk.dim(`  📄 Type:     ${chalk.white(fileInfo.type)}`));

        const validation = fileService.validateFile(fileInfo);
        if (!validation.valid) {
          showError('Invalid File', validation.error!, 'Supported formats: .pdf, .md, .txt, .docx, .json');
          process.exitCode = 1;
          return;
        }

        const sizeKB = (fileInfo.size / 1024).toFixed(1);
        console.log(chalk.dim(`  📊 Size:     ${chalk.white(`${sizeKB} KB`)}`));
        console.log('');

        const outDir = path.resolve(options.output);
        fs.mkdirSync(outDir, { recursive: true });
        process.env.PROF_OUTPUT_DIR = outDir;

        const envPath = path.resolve(repoRoot, '.env');
        if (fs.existsSync(envPath)) {
          const envContent = fs.readFileSync(envPath, 'utf-8');
          const hasNim = /NIM_API_KEY=[^\r\n\s]+/.test(envContent);
          const hasGemini = /GEMINI_API_KEY=[^\r\n\s]+/.test(envContent) || /GOOGLE_API_KEY=[^\r\n\s]+/.test(envContent);
          if (!hasNim && !hasGemini) {
            showError('Configuration Error', 'API Key missing or empty. Please add a valid NIM_API_KEY or GEMINI_API_KEY to your .env file at the repository root.', 'Run `prof config` for help.');
            process.exitCode = 1;
            return;
          }
        } else {
          showError('Configuration Error', 'No .env file found. Please create one with your API keys at the repository root.', 'Required for AI analysis.');
          process.exitCode = 1;
          return;
        }

        const startTime = Date.now();
        const results = await runRealAgentWorkflow(fileInfo.path, agentName);
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

        const successCount = results.filter((r) => r.success).length;
        const failCount = results.filter((r) => !r.success).length;

        const summaryLines = [
          '',
          `  ${chalk.green.bold('✔  Analysis Complete')}`,
          '',
          `  ${chalk.dim('File:')}        ${chalk.white(fileInfo.name)}`,
          `  ${chalk.dim('Agents:')}      ${chalk.green(`${successCount} passed`)}${failCount > 0 ? chalk.red(`, ${failCount} failed`) : ''}`,
          `  ${chalk.dim('Duration:')}    ${chalk.white(`${elapsed}s`)}`,
          `  ${chalk.dim('Output:')}      ${chalk.cyan(path.resolve(options.output))}`,
          '',
          `  ${chalk.dim('View results:')} ${chalk.cyan('prof history')}`,
          '',
        ];

        const card = boxen(summaryLines.join('\n'), {
          padding: { top: 0, bottom: 0, left: 0, right: 1 },
          borderColor: 'green',
          borderStyle: 'round',
          title: ' Results ',
          titleAlignment: 'center',
        });

        console.log(card);

        try {
          const historyFile = path.join(os.homedir(), '.professor-profiler', 'history.json');
          const fsExtra = await import('fs-extra');
          let history: any[] = [];
          if (await fsExtra.default.pathExists(historyFile)) {
            history = await fsExtra.default.readJson(historyFile);
          }
          history.unshift({
            command: 'analyze',
            args: [fileArg],
            timestamp: new Date().toISOString(),
            duration: Date.now() - startTime,
            success: true
          });
          if (history.length > 50) history = history.slice(0, 50);
          await fsExtra.default.ensureDir(path.dirname(historyFile));
          await fsExtra.default.writeJson(historyFile, history, { spaces: 2 });
        } catch (e) {
          // Ignore history save errors
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        showError('Analysis Failed', message, 'Check the file path and try again.');
        process.exitCode = 1;
      }
    });

  return cmd;
}
