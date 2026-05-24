/**
 * @module container
 * @description Lightweight dependency injection container for the Professor Profiler CLI.
 * Provides lazy instantiation, type-safe resolution, and singleton management.
 */

import { logger } from '../utils/logger.js';

/**
 * A factory function that produces an instance of type T.
 */
type Factory<T> = () => T;

/**
 * A registry entry holding the factory and its cached instance.
 */
interface RegistryEntry<T = unknown> {
  /** Factory function to create the instance */
  factory: Factory<T>;
  /** Cached instance, populated on first resolve */
  instance?: T;
}

/**
 * Lightweight dependency injection container.
 *
 * Supports lazy instantiation — factories are only invoked on first `resolve()` call.
 * Instances are cached as singletons for the lifetime of the container.
 *
 * @example
 * ```typescript
 * import { container } from './container.js';
 *
 * container.register('configManager', () => new ConfigManager());
 * const config = container.resolve<ConfigManager>('configManager');
 * ```
 */
export class Container {
  /** Internal registry mapping keys to their factory entries */
  private registry: Map<string, RegistryEntry> = new Map();

  /**
   * Register a factory function under a given key.
   * If a factory is already registered under this key, it will be overwritten.
   *
   * @param key - Unique string identifier for the dependency
   * @param factory - Factory function that produces the dependency instance
   * @template T - The type of the dependency
   */
  register<T>(key: string, factory: Factory<T>): void {
    this.registry.set(key, { factory } as RegistryEntry);
    logger.debug(`[Container] Registered: ${key}`);
  }

  /**
   * Resolve a dependency by key. On first call, invokes the factory and caches the result.
   * Subsequent calls return the cached instance.
   *
   * @param key - The key under which the dependency was registered
   * @returns The resolved dependency instance
   * @throws {Error} If no factory is registered for the given key
   * @template T - The expected type of the dependency
   */
  resolve<T>(key: string): T {
    const entry = this.registry.get(key);

    if (!entry) {
      const msg = `[Container] No registration found for key: "${key}"`;
      logger.error(msg);
      throw new Error(msg);
    }

    if (entry.instance === undefined) {
      logger.debug(`[Container] Instantiating: ${key}`);
      entry.instance = entry.factory();
    }

    return entry.instance as T;
  }

  /**
   * Check whether a dependency has been registered under the given key.
   *
   * @param key - The key to check
   * @returns `true` if a factory is registered for this key
   */
  has(key: string): boolean {
    return this.registry.has(key);
  }

  /**
   * Reset the container by clearing all registrations and cached instances.
   * Primarily intended for use in test environments.
   */
  reset(): void {
    this.registry.clear();
    logger.debug('[Container] Reset — all registrations cleared');
  }

  /**
   * Get all registered keys.
   *
   * @returns An array of all registered dependency keys
   */
  keys(): string[] {
    return Array.from(this.registry.keys());
  }
}

/**
 * Global singleton container instance.
 * Use this throughout the application for dependency registration and resolution.
 */
export const container = new Container();
