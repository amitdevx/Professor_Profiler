/**
 * @module events
 * @description Typed event bus for the Professor Profiler CLI.
 * Built on Node.js EventEmitter with strongly-typed event definitions
 * for agent lifecycle, streaming, analysis, command, and file events.
 */

import { EventEmitter } from 'node:events';
import type { AgentResult, AgentTask, StreamChunk, FileInfo } from '../types/index.js';

/**
 * Map of all supported event names to their payload types.
 * This provides compile-time type safety for event emission and subscription.
 */
export interface EventMap {
  /** Fired when an agent begins processing a task */
  'agent:start': { task: AgentTask };
  /** Fired when an agent successfully completes a task */
  'agent:complete': { task: AgentTask; result: AgentResult };
  /** Fired when an agent encounters an error during execution */
  'agent:error': { task: AgentTask; error: Error };
  /** Fired for each streaming token received from an agent */
  'stream:token': StreamChunk;
  /** Fired when an agent's streaming output finishes */
  'stream:end': { agentName: string; totalTokens: number };
  /** Fired when a document analysis workflow begins */
  'analysis:start': { fileCount: number; sessionId: string };
  /** Fired when a document analysis workflow completes */
  'analysis:complete': { sessionId: string; duration: number; resultCount: number };
  /** Fired before a CLI command begins execution */
  'command:start': { commandName: string; args: string[]; timestamp: Date };
  /** Fired after a CLI command finishes execution */
  'command:end': { commandName: string; duration: number; success: boolean };
  /** Fired when a @file reference is successfully resolved */
  'file:resolved': FileInfo;
}

/**
 * Typed event bus extending Node.js EventEmitter.
 *
 * Provides type-safe `emit`, `on`, and `once` methods keyed by {@link EventMap}.
 * All cross-cutting event communication in the CLI should flow through this bus.
 *
 * @example
 * ```typescript
 * import { eventBus } from './events.js';
 *
 * eventBus.on('agent:start', ({ task }) => {
 *   console.log(`Agent started: ${task.name}`);
 * });
 *
 * eventBus.emit('agent:start', { task: myTask });
 * ```
 */
export class TypedEventBus extends EventEmitter {
  /**
   * Emit a typed event with its corresponding payload.
   *
   * @param event - The event name from {@link EventMap}
   * @param payload - The event payload matching the event type
   * @returns `true` if listeners were registered for this event
   */
  override emit<K extends keyof EventMap>(event: K, payload: EventMap[K]): boolean;
  override emit(event: string | symbol, ...args: unknown[]): boolean {
    return super.emit(event, ...args);
  }

  /**
   * Subscribe to a typed event.
   *
   * @param event - The event name from {@link EventMap}
   * @param listener - Callback invoked with the event payload
   * @returns This EventBus instance for chaining
   */
  override on<K extends keyof EventMap>(event: K, listener: (payload: EventMap[K]) => void): this;
  override on(event: string | symbol, listener: (...args: unknown[]) => void): this {
    return super.on(event, listener);
  }

  /**
   * Subscribe to a typed event for a single invocation.
   *
   * @param event - The event name from {@link EventMap}
   * @param listener - Callback invoked once with the event payload
   * @returns This EventBus instance for chaining
   */
  override once<K extends keyof EventMap>(event: K, listener: (payload: EventMap[K]) => void): this;
  override once(event: string | symbol, listener: (...args: unknown[]) => void): this {
    return super.once(event, listener);
  }
}

/**
 * Global singleton event bus instance.
 * Use this throughout the application for publishing and subscribing to events.
 */
export const eventBus = new TypedEventBus();
