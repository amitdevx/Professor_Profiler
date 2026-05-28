import { stdin, stdout } from 'node:process';
import fs from 'fs-extra';
import path from 'node:path';
import chalk from 'chalk';

const SLASH_COMMANDS = ['/help', '/exit', '/quit', '/clear', '/history', '/q'];

export async function customReplPrompt(promptText: string): Promise<string | null> {
  return new Promise<string | null>((resolve) => {
    let line = '';
    let cursor = 0;
    let suggestions: string[] = [];
    let suggestionIndex = 0;
    let showingSuggestions = false;

    if (!stdin.isTTY) {
       let buffer = '';
       stdin.on('data', (d) => buffer += d.toString());
       stdin.on('end', () => resolve(buffer.trim()));
       return;
    }

    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding('utf8');

    const updateSuggestions = () => {
      const words = line.slice(0, cursor).split(' ');
      const lastWord = words[words.length - 1];
      suggestions = [];
      if (lastWord.startsWith('/')) {
        suggestions = SLASH_COMMANDS.filter((c) => c.startsWith(lastWord));
      } else if (lastWord.startsWith('@')) {
        const searchPath = lastWord.slice(1);
        const dir = path.dirname(searchPath) || '.';
        const base = path.basename(searchPath);
        const isDir = searchPath.endsWith('/');
        try {
          const targetDir = path.resolve(process.cwd(), isDir ? searchPath : dir);
          if (fs.existsSync(targetDir)) {
            const files = fs.readdirSync(targetDir);
            const matches = files.filter((f) => f.startsWith(isDir ? '' : base));
            suggestions = matches.map((f) => {
              const fullPath = path.join(targetDir, f);
              const isDirectory = fs.statSync(fullPath).isDirectory();
              const prefix = isDir ? searchPath : (dir === '.' ? '' : dir + '/');
              return '@' + prefix + f + (isDirectory ? '/' : '');
            });
          }
        } catch {
        }
      }
      showingSuggestions = suggestions.length > 0;
      suggestionIndex = 0;
    };

    const render = () => {
      stdout.write('\x1b[2K\x1b[0G');
      stdout.write(promptText + line);

      if (showingSuggestions && suggestions.length > 0) {
        stdout.write('\n');
        suggestions.forEach((s, i) => {
          if (i === suggestionIndex) {
            stdout.write(chalk.bgBlue.white(` ${s} `) + '\x1b[K\n');
          } else {
            stdout.write(chalk.dim(` ${s} `) + '\x1b[K\n');
          }
        });
        // We printed 1 newline, plus N newlines in the loop. Total down = N + 1.
        stdout.write(`\x1b[${suggestions.length + 1}A`);
      } else {
        stdout.write('\x1b[J');
      }

      // Reposition cursor
      const plainPrompt = promptText.replace(/\x1b\[[0-9;]*m/g, '');
      stdout.write(`\x1b[${plainPrompt.length + cursor + 1}G`);
    };

    const cleanup = () => {
      if (showingSuggestions) {
        stdout.write('\n\x1b[J\x1b[1A');
      }
    };

    const onData = (key: string) => {
      if (key === '\u0003') {
        // Ctrl+C
        cleanup();
        stdout.write('\n');
        stdin.setRawMode(false);
        stdin.pause();
        stdin.removeListener('data', onData);
        process.kill(process.pid, 'SIGINT');
        resolve(null);
      } else if (key === '\r') {
        // Enter
        if (showingSuggestions && suggestions.length > 0) {
          // Select suggestion instead of submitting
          const words = line.slice(0, cursor).split(' ');
          const lastWord = words[words.length - 1];
          const chosen = suggestions[suggestionIndex];
          const before = line.slice(0, cursor - lastWord.length);
          const after = line.slice(cursor);
          line = before + chosen + ' ' + after;
          cursor = before.length + chosen.length + 1;
          updateSuggestions();
          render();
        } else {
          // Submit prompt
          cleanup();
          stdout.write('\n');
          stdin.setRawMode(false);
          stdin.pause();
          stdin.removeListener('data', onData);
          resolve(line);
        }
      } else if (key === '\t') {
        // Tab
        if (showingSuggestions && suggestions.length > 0) {
          const words = line.slice(0, cursor).split(' ');
          const lastWord = words[words.length - 1];
          const chosen = suggestions[suggestionIndex];
          const before = line.slice(0, cursor - lastWord.length);
          const after = line.slice(cursor);
          line = before + chosen + (chosen.endsWith('/') ? '' : ' ') + after;
          cursor = before.length + chosen.length + (chosen.endsWith('/') ? 0 : 1);
          updateSuggestions();
          render();
        }
      } else if (key === '\x7f' || key === '\b') {
        // Backspace
        if (cursor > 0) {
          line = line.slice(0, cursor - 1) + line.slice(cursor);
          cursor--;
          updateSuggestions();
          render();
        }
      } else if (key === '\x17') {
        // Ctrl+W (Delete word)
        if (cursor > 0) {
          const before = line.slice(0, cursor);
          const match = before.match(/\s*\S+\s*$/);
          const deleteLen = match ? match[0].length : 1;
          line = line.slice(0, cursor - deleteLen) + line.slice(cursor);
          cursor -= deleteLen;
          updateSuggestions();
          render();
        }
      } else if (key === '\x15') {
        // Ctrl+U (Delete entire line)
        line = line.slice(cursor);
        cursor = 0;
        updateSuggestions();
        render();
      } else if (key === '\x1b[B') {
        // Arrow Down
        if (showingSuggestions && suggestions.length > 0) {
          suggestionIndex = (suggestionIndex + 1) % suggestions.length;
          render();
        }
      } else if (key === '\x1b[A') {
        // Arrow Up
        if (showingSuggestions && suggestions.length > 0) {
          suggestionIndex = (suggestionIndex - 1 + suggestions.length) % suggestions.length;
          render();
        }
      } else if (key === '\x1b[D') {
        // Arrow Left
        if (cursor > 0) {
          cursor--;
          updateSuggestions();
          render();
        }
      } else if (key === '\x1b[C') {
        // Arrow Right
        if (cursor < line.length) {
          cursor++;
          updateSuggestions();
          render();
        }
      } else if (key === '\x1b[H' || key === '\x1b[1~' || key === '\x1bOH') {
        // Home
        cursor = 0;
        updateSuggestions();
        render();
      } else if (key === '\x1b[F' || key === '\x1b[4~' || key === '\x1bOF') {
        cursor = line.length;
        updateSuggestions();
        render();
      } else if (key === '\x1bb') {
        // Alt+B
        const before = line.slice(0, cursor);
        const match = before.match(/\S+\s*$/);
        if (match) {
          cursor -= match[0].length;
          updateSuggestions();
          render();
        } else {
          cursor = 0;
          updateSuggestions();
          render();
        }
      } else if (key === '\x1bf') {
        // Alt+F
        const after = line.slice(cursor);
        const match = after.match(/^\s*\S+/);
        if (match) {
          cursor += match[0].length;
          updateSuggestions();
          render();
        } else {
          cursor = line.length;
          updateSuggestions();
          render();
        }
      } else if (key.startsWith('\x1b')) {
        // Ignore other unknown escape sequences (e.g. PgUp/PgDn)
      } else {
        // Standard typing
        line = line.slice(0, cursor) + key + line.slice(cursor);
        cursor += key.length;
        updateSuggestions();
        render();
      }
    };

    stdin.on('data', onData);
    render();
  });
}
