/**
 * @module config/configManager
 * @description Configuration management for the Professor Profiler CLI.
 * Handles reading, validating, and persisting user configuration
 * with Zod schema validation and dotenv integration.
 */

import { z } from 'zod';
import fs from 'fs-extra';
import path from 'node:path';
import os from 'node:os';
import dotenv from 'dotenv';
import { logger } from '../utils/logger.js';
import type { CLIConfig } from '../types/index.js';

/**
 * Zod schema for validating the CLI configuration.
 * Provides runtime type safety and descriptive validation errors.
 */
const CLIConfigSchema = z.object({
  /** Active AI provider name */
  provider: z
    .string()
    .min(1, 'Provider name cannot be empty')
    .default('nim'),
  /** Model identifier for the active provider */
  model: z
    .string()
    .min(1, 'Model name cannot be empty')
    .default('meta/llama-3.1-70b-instruct'),
  /** UI theme name */
  theme: z.enum(['minimal', 'cyberpunk', 'hacker', 'ocean', 'sunset']).default('cyberpunk'),
  /** Map of provider names to API keys */
  apiKeys: z.record(z.string(), z.string()).default({}),
  /** Output directory for analysis results */
  outputDir: z.string().default('./output'),
  /** Whether anonymous telemetry collection is enabled */
  telemetryEnabled: z.boolean().default(true),
});

/** Path to the user's configuration file */
const CONFIG_DIR = path.join(os.homedir(), '.professor-profiler');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

/** Path to the parent project's .env file */
const PROJECT_ROOT = path.resolve(
  path.dirname(new URL(import.meta.url).pathname),
  '..', '..', '..',
);
const DOTENV_PATH = path.join(PROJECT_ROOT, '.env');

/**
 * Manages the CLI configuration lifecycle: loading, validation, mutation, and persistence.
 *
 * Configuration is stored at `~/.professor-profiler/config.json` and validated
 * against a Zod schema. Environment variables from the project root `.env` file
 * are also loaded into `process.env` on initialization.
 *
 * @example
 * ```typescript
 * import { configManager } from './configManager.js';
 *
 * await configManager.initialize();
 * const provider = configManager.get('provider');
 * configManager.set('model', 'gemini-2.0-flash');
 * await configManager.save();
 * ```
 */
export class ConfigManager {
  /** In-memory configuration state */
  private config: CLIConfig;

  /** Whether the manager has been initialized */
  private initialized = false;

  constructor() {
    this.config = CLIConfigSchema.parse({});
  }

  /**
   * Initialize the config manager: load .env, read or create config file.
   * Must be called before using get/set/save.
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    // Load environment variables from the project root .env file
    this.loadDotenv();

    // Load or create the config file
    await this.load();

    this.initialized = true;
    logger.debug('ConfigManager initialized', 'config');
  }

  /**
   * Get a specific configuration value by key.
   *
   * @param key - The configuration key to retrieve
   * @returns The value for the given key
   * @template K - A key of {@link CLIConfig}
   */
  get<K extends keyof CLIConfig>(key: K): CLIConfig[K] {
    return this.config[key];
  }

  /**
   * Set a specific configuration value by key.
   * Changes are held in memory until {@link save} is called.
   *
   * @param key - The configuration key to set
   * @param value - The new value
   * @template K - A key of {@link CLIConfig}
   */
  set<K extends keyof CLIConfig>(key: K, value: CLIConfig[K]): void {
    const original = this.config[key];
    try {
      this.config[key] = value;
      this.config = CLIConfigSchema.parse(this.config);
      logger.debug(`Config updated: ${String(key)} = ${JSON.stringify(value)}`, 'config');
    } catch (err: any) {
      this.config[key] = original;
      throw new Error(`Invalid configuration: ${err.message}`);
    }
  }

  /**
   * Get the full configuration object.
   *
   * @returns A shallow copy of the current configuration
   */
  getAll(): CLIConfig {
    return { ...this.config };
  }

  /**
   * Persist the current in-memory configuration to disk.
   * Creates the config directory if it doesn't exist.
   */
  async save(): Promise<void> {
    try {
      await fs.ensureDir(CONFIG_DIR);
      await fs.writeJson(CONFIG_FILE, this.config, { spaces: 2 });
      logger.debug(`Configuration saved to ${CONFIG_FILE}`, 'config');
    } catch (err) {
      logger.error(
        `Failed to save configuration: ${err instanceof Error ? err.message : String(err)}`,
        'config',
      );
      throw err;
    }
  }

  /**
   * Reset all configuration values to their defaults and persist to disk.
   */
  async reset(): Promise<void> {
    this.config = CLIConfigSchema.parse({});
    await this.save();
    logger.info('Configuration reset to defaults', 'config');
  }

  /**
   * Load configuration from the config file, or create a default one.
   * Validates the loaded data against the Zod schema.
   */
  private async load(): Promise<void> {
    try {
      if (await fs.pathExists(CONFIG_FILE)) {
        const raw = await fs.readJson(CONFIG_FILE);
        const parsed = CLIConfigSchema.safeParse(raw);

        if (parsed.success) {
          this.config = parsed.data;
          logger.debug(`Configuration loaded from ${CONFIG_FILE}`, 'config');
        } else {
          logger.warn(
            `Invalid config file, using defaults: ${parsed.error.message}`,
            'config',
          );
          this.config = CLIConfigSchema.parse({});
          await this.save();
        }
      } else {
        logger.debug('No config file found — creating with defaults', 'config');
        await this.save();
      }
    } catch (err) {
      logger.warn(
        `Failed to read config file, using defaults: ${err instanceof Error ? err.message : String(err)}`,
        'config',
      );
      this.config = CLIConfigSchema.parse({});
    }
  }

  /**
   * Load environment variables from the project's .env file.
   */
  private loadDotenv(): void {
    const result = dotenv.config({ path: DOTENV_PATH });

    if (result.error) {
      logger.debug(
        `No .env file loaded from ${DOTENV_PATH}: ${result.error.message}`,
        'config',
      );
    } else {
      logger.debug(`Environment variables loaded from ${DOTENV_PATH}`, 'config');
    }
  }
}

/**
 * Global singleton ConfigManager instance.
 * Call `configManager.initialize()` early in the CLI boot sequence.
 */
export const configManager = new ConfigManager();
