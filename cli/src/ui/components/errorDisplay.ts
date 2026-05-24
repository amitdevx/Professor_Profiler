/**
 * @module ui/components/errorDisplay
 * @description Beautiful terminal error rendering with boxen cards.
 * Displays structured error information with title, message, and optional suggestion.
 */

import boxen from 'boxen';
import chalk from 'chalk';

/**
 * Render a beautifully formatted error card to stderr.
 *
 * Displays a red-bordered boxen card containing the error title,
 * descriptive message, and an optional suggestion for resolution.
 *
 * @param title      - Short error category (e.g. "File Not Found").
 * @param message    - Detailed error description.
 * @param suggestion - Optional actionable fix the user can try.
 *
 * @example
 * ```ts
 * showError(
 *   'Invalid File',
 *   'The file "exam.xlsx" is not a supported format.',
 *   'Supported formats: .pdf, .md, .txt, .docx'
 * );
 * ```
 */
export function showError(title: string, message: string, suggestion?: string): void {
  const icon = chalk.red.bold('✖');
  const titleLine = `${icon}  ${chalk.red.bold(title)}`;
  const messageLine = `   ${chalk.white(message)}`;

  const lines = ['', titleLine, '', messageLine, ''];

  if (suggestion) {
    const bulb = chalk.yellow('💡');
    lines.push(`   ${bulb}  ${chalk.yellow(suggestion)}`, '');
  }

  const card = boxen(lines.join('\n'), {
    padding: { top: 0, bottom: 0, left: 1, right: 1 },
    borderColor: 'red',
    borderStyle: 'round',
    title: ' Error ',
    titleAlignment: 'center',
  });

  console.error('');
  console.error(card);
  console.error('');
}

/**
 * Render a warning card (non-fatal).
 *
 * @param title   - Short warning category.
 * @param message - Warning details.
 */
export function showWarning(title: string, message: string): void {
  const icon = chalk.yellow.bold('⚠');
  const titleLine = `${icon}  ${chalk.yellow.bold(title)}`;
  const messageLine = `   ${chalk.white(message)}`;

  const card = boxen(['', titleLine, '', messageLine, ''].join('\n'), {
    padding: { top: 0, bottom: 0, left: 1, right: 1 },
    borderColor: 'yellow',
    borderStyle: 'round',
    title: ' Warning ',
    titleAlignment: 'center',
  });

  console.error('');
  console.error(card);
  console.error('');
}

/**
 * Render a success card.
 *
 * @param title   - Short success summary.
 * @param message - Success details.
 */
export function showSuccess(title: string, message: string): void {
  const icon = chalk.green.bold('✔');
  const titleLine = `${icon}  ${chalk.green.bold(title)}`;
  const messageLine = `   ${chalk.white(message)}`;

  const card = boxen(['', titleLine, '', messageLine, ''].join('\n'), {
    padding: { top: 0, bottom: 0, left: 1, right: 1 },
    borderColor: 'green',
    borderStyle: 'round',
    title: ' Success ',
    titleAlignment: 'center',
  });

  console.log('');
  console.log(card);
  console.log('');
}
