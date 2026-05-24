/**
 * @module hooks
 * @description Re-exports all lifecycle hooks for the Professor Profiler CLI.
 * Import hooks from this barrel module for cleaner import paths.
 *
 * @example
 * ```typescript
 * import { preCommandHook, postCommandHook, errorHook, telemetryHook } from '../hooks/index.js';
 * ```
 */

export { preCommandHook } from './preCommand.js';
export { postCommandHook } from './postCommand.js';
export { errorHook } from './errorHook.js';
export { telemetryHook } from './telemetryHook.js';
