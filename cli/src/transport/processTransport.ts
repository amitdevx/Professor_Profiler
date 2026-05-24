import { spawn, ChildProcess } from 'child_process';
import { BaseTransport } from './baseTransport.js';
import * as readline from 'readline';

/**
 * ProcessTransport communicates with a local child process (e.g., Python backend).
 */
export class ProcessTransport extends BaseTransport {
  private child: ChildProcess | null = null;
  private command: string;
  
  constructor(command: string = 'python3') {
    super();
    this.command = command;
  }

  async connect(): Promise<void> {}
  async disconnect(): Promise<void> {
    if (this.child && !this.child.killed) {
      this.child.kill('SIGINT');
      this.child = null;
    }
  }

  async send(payload: { file: string, agentName?: string }, signal?: AbortSignal): Promise<string> {
    // Collect all streamed output and return it as a single string
    let result = '';
    for await (const chunk of this.stream(payload, signal)) {
      result += chunk + '\n';
    }
    return result;
  }

  async *stream(payload: { file: string, agentName?: string }, signal?: AbortSignal): AsyncGenerator<string> {
    const fs = await import('fs');
    const path = await import('path');
    const { fileURLToPath } = await import('url');
    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    const repoRoot = path.resolve(__dirname, '../../');
    const venvPython = path.resolve(repoRoot, '.venv/bin/python');
    const pythonExec = fs.existsSync(venvPython) ? venvPython : this.command;

    const chalk = (await import('chalk')).default;
    const pythonScript = `
import sys, asyncio
sys.path.insert(0, '${repoRoot}')
from run import run_analysis
asyncio.run(run_analysis(sys.argv[1], sys.argv[2]))
`;

    this.child = spawn(pythonExec, ['-c', pythonScript, payload.file, payload.agentName || 'all'], {
      env: { ...process.env, PYTHONUNBUFFERED: '1', PROF_OUTPUT_DIR: process.env.PROF_OUTPUT_DIR || process.cwd(), PROF_INPUT_DIR: process.cwd() },
      cwd: process.cwd()
    });

    if (this.child.stderr) {
      this.child.stderr.on('data', (data) => {
        const msg = data.toString().trim();
        if (msg) console.error(chalk.red(`[Backend Error] ${msg}`));
      });
    }

    if (signal) {
      signal.addEventListener('abort', () => {
        if (this.child && !this.child.killed) {
          this.child.kill('SIGINT');
        }
      });
    }

    if (!this.child.stdout) return;

    const rl = readline.createInterface({
      input: this.child.stdout,
      crlfDelay: Infinity
    });

    for await (const line of rl) {
      if (signal?.aborted) break;
      yield line;
    }
    
    this.child = null;
  }
}
