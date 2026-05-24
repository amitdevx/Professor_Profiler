/**
 * @module hooks/preCommand
 * @description Pre-command lifecycle hook.
 * Executes before every CLI command to log the invocation and emit the command:start event.
 */

import { logger } from '../utils/logger.js';
import { eventBus } from '../core/events.js';
import type { HookContext } from '../types/index.js';

/**
 * Pre-command lifecycle hook.
 *
 * Called before a CLI command begins execution. Logs the command invocation
 * at debug level and emits the `command:start` event on the global event bus.
 *
 * @param context - The hook context containing command name, args, config, and start time
 */
export async function preCommandHook(context: HookContext): Promise<void> {
  logger.debug(`Executing command: ${context.commandName}`, 'hooks:pre');
  logger.debug(
    `Arguments: ${JSON.stringify(context.args, null, 2)}`,
    'hooks:pre',
  );

  eventBus.emit('command:start', {
    commandName: context.commandName,
    args: context.args,
    timestamp: context.startTime,
  });
}
