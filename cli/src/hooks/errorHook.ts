/**
 * @module hooks/errorHook
 * @description Error lifecycle hook.
 * Renders unhandled command errors as styled terminal boxes using boxen.
 */

import chalk from 'chalk';
import boxen from 'boxen';
import { logger } from '../utils/logger.js';
import { eventBus } from '../core/events.js';
import type { HookContext } from '../types/index.js';

/**
 * Error lifecycle hook.
 *
 * Called when a CLI command throws an unhandled error. Renders the error
 * in a visually distinct boxen panel for clear terminal visibility, logs it
 * at error level, and emits the `command:end` event with `success: false`.
 *
 * @param error - The caught error object
 * @param context - The hook context for the failed command
 */
export async function errorHook(
  error: Error,
  context: HookContext,
): Promise<void> {
  const duration = Date.now() - context.startTime.getTime();

  const title = chalk.red.bold('  Error ');
  const errorName = chalk.red(`${error.name}: ${error.message}`);
  const commandInfo = chalk.gray(`Command: ${context.commandName}`);
  const durationInfo = chalk.gray(`Duration: ${duration}ms`);
  const stackTrace = error.stack
    ? chalk.gray(
        error.stack
          .split('\n')
          .slice(1, 5)
          .map((line) => `  ${line.trim()}`)
          .join('\n'),
      )
    : '';

  const content = [
    title,
    '',
    errorName,
    '',
    commandInfo,
    durationInfo,
    ...(stackTrace ? ['', chalk.gray('Stack trace:'), stackTrace] : []),
  ].join('\n');

  const box = boxen(content, {
    padding: 1,
    margin: { top: 1, bottom: 1, left: 0, right: 0 },
    borderStyle: 'round',
    borderColor: 'red',
    title: '✖ Command Failed',
    titleAlignment: 'left',
  });

  console.error(box);

  logger.error(
    `Command "${context.commandName}" failed: ${error.message}`,
    'hooks:error',
  );

  eventBus.emit('command:end', {
    commandName: context.commandName,
    duration,
    success: false,
  });
}
