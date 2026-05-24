/**
 * @module logger
 * @description Leveled logging utility for the Professor Profiler CLI.
 * Supports colored console output and optional file logging via fs-extra.
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'node:path';

/**
 * Available log severity levels, ordered from most to least verbose.
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/**
 * Numeric priority for each log level (lower = more verbose).
 */
const LOG_LEVEL_PRIORITY: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

/**
 * Chalk-colored prefix labels for each log level.
 */
const LOG_LEVEL_PREFIX: Record<LogLevel, string> = {
  debug: chalk.gray('▸ DEBUG'),
  info: chalk.cyan('ℹ INFO '),
  warn: chalk.yellow('⚠ WARN '),
  error: chalk.red('✖ ERROR'),
};

/**
 * Production-grade leveled logger with colored console output
 * and optional persistent file logging.
 *
 * @example
 * ```typescript
 * import { logger } from './logger.js';
 *
 * logger.setLevel('debug');
 * logger.info('Server started on port 3000');
 * logger.error('Failed to connect', 'db-module');
 * ```
 */
export class Logger {
  /** Current minimum log level threshold */
  private level: LogLevel = 'info';

  /** Optional file path for persistent log output */
  private logFilePath: string | null = null;

  /**
   * Set the minimum log level. Messages below this level are suppressed.
   *
   * @param level - The minimum severity level to output
   */
  setLevel(level: LogLevel): void {
    this.level = level;
  }

  /**
   * Get the current log level.
   *
   * @returns The current minimum log level
   */
  getLevel(): LogLevel {
    return this.level;
  }

  /**
   * Enable file logging by specifying an output path.
   * The file and its parent directories will be created if they don't exist.
   *
   * @param filePath - Absolute path to the log file
   */
  async setLogFile(filePath: string): Promise<void> {
    await fs.ensureDir(path.dirname(filePath));
    this.logFilePath = filePath;
    await this.appendToFile(`\n--- Log session started at ${new Date().toISOString()} ---\n`);
  }

  /**
   * Log a debug-level message.
   *
   * @param message - The message to log
   * @param context - Optional context label (e.g., module name)
   */
  debug(message: string, context?: string): void {
    this.log('debug', message, context);
  }

  /**
   * Log an info-level message.
   *
   * @param message - The message to log
   * @param context - Optional context label
   */
  info(message: string, context?: string): void {
    this.log('info', message, context);
  }

  /**
   * Log a warn-level message.
   *
   * @param message - The message to log
   * @param context - Optional context label
   */
  warn(message: string, context?: string): void {
    this.log('warn', message, context);
  }

  /**
   * Log an error-level message.
   *
   * @param message - The message to log
   * @param context - Optional context label
   */
  error(message: string, context?: string): void {
    this.log('error', message, context);
  }

  /**
   * Internal log dispatcher. Checks level threshold, formats the message,
   * writes to console and optionally to a log file.
   *
   * @param level - Severity level of this message
   * @param message - The message content
   * @param context - Optional context label
   */
  private log(level: LogLevel, message: string, context?: string): void {
    if (LOG_LEVEL_PRIORITY[level] < LOG_LEVEL_PRIORITY[this.level]) {
      return;
    }

    const timestamp = chalk.gray(new Date().toISOString());
    const prefix = LOG_LEVEL_PREFIX[level];
    const contextStr = context ? chalk.magenta(` [${context}]`) : '';
    const formatted = `${timestamp} ${prefix}${contextStr} ${message}`;

    if (level === 'error') {
      console.error(formatted);
    } else if (level === 'warn') {
      console.warn(formatted);
    } else {
      console.log(formatted);
    }

    // Fire-and-forget file append (non-blocking)
    if (this.logFilePath) {
      const plainLine = `${new Date().toISOString()} [${level.toUpperCase()}]${context ? ` [${context}]` : ''} ${message}\n`;
      this.appendToFile(plainLine).catch(() => {
        // Silently ignore file write failures to prevent cascading errors
      });
    }
  }

  /**
   * Append a line to the configured log file.
   *
   * @param content - The string content to append
   */
  private async appendToFile(content: string): Promise<void> {
    if (this.logFilePath) {
      await fs.appendFile(this.logFilePath, content, 'utf-8');
    }
  }
}

/**
 * Global singleton logger instance.
 * Use this throughout the application for consistent logging.
 */
export const logger = new Logger();
