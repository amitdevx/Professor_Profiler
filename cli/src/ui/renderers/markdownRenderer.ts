/**
 * @module ui/renderers/markdownRenderer
 * @description Converts Markdown to beautifully styled terminal output
 * using `marked` and `marked-terminal`.
 */

import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';

import chalk from 'chalk';

// Force chalk to output colors even if it thinks it's not in a TTY
chalk.level = chalk.level || 1;

/**
 * Configure `marked` with the terminal renderer.
 * This must happen once before any rendering calls.
 */
marked.use(markedTerminal({
  // explicitly configure options to ensure bold/markdown formatting
  strong: chalk.bold,
  em: chalk.italic,
  firstHeading: chalk.bold.underline,
  heading: chalk.bold.cyan,
  code: chalk.yellow,
  link: chalk.blue,
  href: chalk.blue.underline
}) as any);

/**
 * Convert a Markdown string to styled terminal output.
 *
 * @param content - Raw Markdown content.
 * @returns Formatted string suitable for `console.log()`.
 *
 * @example
 * ```ts
 * console.log(renderMarkdown('# Hello World\n\n- Item 1\n- Item 2'));
 * ```
 */
export function renderMarkdown(content: string): string {
  // LLMs often output lists with 4 spaces of indentation, which standard Markdown 
  // interprets as a literal code block (ignoring bold/italic syntax).
  // This regex un-indents those list items so marked formats them properly.
  const cleanedContent = content.replace(/^ {1,4}([-*+]|\d+\.)/gm, '$1');

  // marked may return a string or Promise<string> depending on config.
  // With synchronous extensions only, it returns a string.
  const result = marked.parse(cleanedContent);

  if (typeof result === 'string') {
    return result;
  }

  // Fallback: if somehow async, return raw content
  return content;
}
