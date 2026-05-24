/**
 * @module hooks/postCommand
 * @description Post-command lifecycle hook.
 * Executes after every CLI command to log completion, calculate duration,
 * and emit the command:end event.
 */

import { logger } from '../utils/logger.js';
import { eventBus } from '../core/events.js';
import type { HookContext } from '../types/index.js';

/**
 * Post-command lifecycle hook.
 *
 * Called after a CLI command finishes execution. Calculates the total duration,
 * logs a completion message, and emits the `command:end` event.
 *
 * @param context - The hook context containing command name, args, config, and start time
 */
export async function postCommandHook(context: HookContext): Promise<void> {
  const endTime = Date.now();
  const duration = endTime - context.startTime.getTime();

  logger.debug(
    `Command "${context.commandName}" completed in ${duration}ms`,
    'hooks:post',
  );

  eventBus.emit('command:end', {
    commandName: context.commandName,
    duration,
    success: true,
  });
}
