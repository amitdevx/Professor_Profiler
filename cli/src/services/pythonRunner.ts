import fs from 'fs-extra';
import path from 'node:path';
import { spawn, ChildProcess } from 'node:child_process';
import chalk from 'chalk';
import ora from 'ora';
import { renderMarkdown } from '../ui/renderers/markdownRenderer.js';

export class PythonRunner {
  private childProcess: ChildProcess | null = null;
  private spinner: any;

  constructor() {
    this.spinner = ora({ text: chalk.cyan('Thinking...'), spinner: 'dots' });
  }

  async runChatStream(finalPrompt: string, agentName: 'root' | 'summarizer' | 'chat' = 'root', history: string[] = []): Promise<string> {
    this.spinner.start();

    try {
      const { fileURLToPath } = await import('node:url');
      const __dirname = path.dirname(fileURLToPath(import.meta.url));
      const repoRoot = path.resolve(__dirname, '../../');
      const envPath = path.resolve(repoRoot, '.env');
      
      if (fs.existsSync(envPath)) {
        const envContent = fs.readFileSync(envPath, 'utf-8');
        const hasNim = /NIM_API_KEY=\s*[^\s]+/.test(envContent);
        const hasGemini = /GEMINI_API_KEY=\s*[^\s]+/.test(envContent);
        if (!hasNim && !hasGemini) {
          this.spinner.fail(chalk.red('  ✖ API Key missing or empty. Please add a valid NIM_API_KEY or GEMINI_API_KEY to your .env file at the repository root.'));
          return '';
        }
      } else {
        this.spinner.fail(chalk.red('  ✖ No .env file found. Please create one with your API keys at the repository root.'));
        return '';
      }

      const venvPython = path.resolve(repoRoot, '.venv/bin/python');
      const pythonExec = fs.existsSync(venvPython) ? venvPython : 'python3';

      const pythonScript = `
import sys, asyncio, os, json, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
repo_root = Path('${repoRoot}').resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from dotenv import load_dotenv
load_dotenv(repo_root / '.env')

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from google.genai import types as genai_types

async def run_chat(query: str, agent_name: str, history: list):
    provider = os.getenv("LLM_PROVIDER", "nim").lower()
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="prof_cli", user_id="default_user", session_id="cli_chat")
    
    if agent_name == 'summarizer':
        from google.adk.agents import Agent
        agent = Agent(name="summarizer", model="meta/llama-3.1-8b-instruct", instructions="You are a helpful expert. Summarize the provided document concisely, extracting key concepts and actionable points.", tools=[])
    elif agent_name == 'chat':
        from google.adk.agents import Agent
        agent = Agent(name="chat_assistant", model="meta/llama-3.1-8b-instruct", instructions="You are an interactive AI assistant. Answer the user's questions contextually. Be concise and helpful.", tools=[])
    else:
        agent = root_agent

    # Reconstruct history
    for idx, msg in enumerate(history):
        role = "user" if idx % 2 == 0 else "model"
        await session_service.add_message(
            app_name="prof_cli",
            user_id="default_user",
            session_id="cli_chat",
            role=role,
            content=msg
        )

    runner = Runner(agent=agent, app_name="prof_cli", session_service=session_service, llm_provider=provider)
    
    final_response = ""
    async for event in runner.run_async("default_user", "cli_chat", genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=query)])):
        if type(event).__name__ == 'RunnerEvent':
             if not event.is_final_response():
                  print(json.dumps({"type": "status", "agent": getattr(event, 'agent_name', 'System'), "message": event.content.parts[0].text}), flush=True)
             else:
                  final_response = event.content.parts[0].text
            
    print("FINAL_RESPONSE_START")
    print(final_response)

import base64
history_b64 = "${Buffer.from(JSON.stringify(history)).toString('base64')}"
history_json = base64.b64decode(history_b64).decode('utf-8')
asyncio.run(run_chat(sys.argv[1], sys.argv[2], json.loads(history_json)))
`;
      this.childProcess = spawn(pythonExec, ['-c', pythonScript, finalPrompt, agentName], {
        env: { ...process.env, PYTHONUNBUFFERED: '1', PROF_OUTPUT_DIR: process.cwd(), PROF_INPUT_DIR: process.cwd() }
      });

      let output = '';
      let errorOutput = '';

      this.childProcess.stdout?.on('data', (data) => {
        const chunk = data.toString();
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('{') && line.includes('"type": "status"')) {
            try {
              const obj = JSON.parse(line);
              // Avoid ANSI color codes directly in spinner text to prevent terminal rendering bugs
              this.spinner.text = `[${obj.agent}] ${obj.message}`;
            } catch (e) {}
          }
        }
        output += chunk;
      });

      this.childProcess.stderr?.on('data', (data) => {
        errorOutput += data.toString();
      });

      const sigintHandler = () => {
        this.spinner.warn(chalk.yellow('  ⚠️ Generation interrupted by user.'));
        this.childProcess?.kill('SIGINT');
      };
      process.on('SIGINT', sigintHandler);

      await new Promise<void>((resolve, reject) => {
        this.childProcess?.on('close', (code) => {
          process.off('SIGINT', sigintHandler);
          if (code === 0 || code === 130) resolve();
          else reject(new Error(errorOutput || 'Python process exited with error'));
        });
      });

      this.spinner.stop();

      const splitOutput = output.split('FINAL_RESPONSE_START\n');
      if (splitOutput.length > 1) {
        let finalAnswer = splitOutput[1].trim();
        
        // Clean up ADK framework specific strings to make the output look like a normal AI response
        finalAnswer = finalAnswer.replace(/\[([a-zA-Z0-9_]+) (Initial )?Response\]\n?/g, '### $1\n');
        finalAnswer = finalAnswer.replace(/### [^\n]+\n+parts=None role=None\n?/g, '');
        finalAnswer = finalAnswer.trim();
        
        console.log(renderMarkdown(finalAnswer));
        return finalAnswer;
      } else {
        console.log(chalk.red('  ✖ Failed to get a valid response from the backend.'));
        if (errorOutput) console.log(chalk.dim(errorOutput));
        return '';
      }
    } catch (e) {
      this.spinner.fail(chalk.red('  ✖ Error communicating with AI backend.'));
      console.log(chalk.dim(String(e)));
      return '';
    }
  }
}

export const pythonRunner = new PythonRunner();
