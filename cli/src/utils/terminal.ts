/**
 * @module terminal
 * @description Terminal capability detection utilities for the Professor Profiler CLI.
 * Detects color support, Unicode rendering, TTY status, and terminal dimensions.
 */

import chalk from 'chalk';

/**
 * Describes the rendering capabilities of the current terminal environment.
 */
export interface TerminalCapabilities {
  /** Current terminal width in columns */
  width: number;
  /** Current terminal height in rows */
  height: number;
  /** Whether the terminal supports ANSI color codes */
  colorSupport: boolean;
  /** Whether the terminal can render Unicode characters */
  unicodeSupport: boolean;
  /** Whether stdout is connected to an interactive TTY */
  isTTY: boolean;
  /** Whether the terminal supports 256-color mode */
  color256: boolean;
  /** Whether the terminal supports true color (16 million colors) */
  trueColor: boolean;
}

/**
 * Get the current terminal width in columns.
 * Falls back to 80 columns if detection fails.
 *
 * @returns The terminal width in columns
 */
export function getTerminalWidth(): number {
  return process.stdout.columns ?? 80;
}

/**
 * Get the current terminal height in rows.
 * Falls back to 24 rows if detection fails.
 *
 * @returns The terminal height in rows
 */
export function getTerminalHeight(): number {
  return process.stdout.rows ?? 24;
}

/**
 * Check whether the terminal supports ANSI color output.
 * Uses chalk's internal detection level.
 *
 * @returns `true` if color is supported
 */
export function supportsColor(): boolean {
  return chalk.level > 0;
}

/**
 * Check whether the terminal environment is likely to support Unicode rendering.
 * Inspects the `LANG`, `LC_ALL`, and `LC_CTYPE` environment variables for UTF-8 indicators,
 * and also checks the `TERM_PROGRAM` for known Unicode-capable terminals.
 *
 * @returns `true` if Unicode is likely supported
 */
export function supportsUnicode(): boolean {
  const env = process.env;

  // Check locale environment variables for UTF-8 indicators
  const locale = (env['LANG'] ?? env['LC_ALL'] ?? env['LC_CTYPE'] ?? '').toLowerCase();
  if (locale.includes('utf-8') || locale.includes('utf8')) {
    return true;
  }

  // Check for known Unicode-capable terminal programs
  const termProgram = (env['TERM_PROGRAM'] ?? '').toLowerCase();
  const unicodeTerminals = ['iterm.app', 'hyper', 'warp', 'alacritty', 'kitty', 'wezterm'];
  if (unicodeTerminals.includes(termProgram)) {
    return true;
  }

  // Windows Terminal and VS Code integrated terminal
  if (env['WT_SESSION'] || env['TERM_PROGRAM'] === 'vscode') {
    return true;
  }

  return false;
}

/**
 * Check whether standard output is connected to an interactive TTY.
 *
 * @returns `true` if stdout is a TTY
 */
export function isTTY(): boolean {
  return process.stdout.isTTY === true;
}

/**
 * Check whether the terminal supports 256-color mode.
 *
 * @returns `true` if 256-color output is supported
 */
export function supportsColor256(): boolean {
  return chalk.level >= 2;
}

/**
 * Check whether the terminal supports true color (24-bit / 16 million colors).
 *
 * @returns `true` if true color output is supported
 */
export function supportsTrueColor(): boolean {
  return chalk.level >= 3;
}

/**
 * Detect all terminal capabilities and return them as a structured object.
 *
 * @returns A {@link TerminalCapabilities} object describing the current terminal
 */
export function detectCapabilities(): TerminalCapabilities {
  return {
    width: getTerminalWidth(),
    height: getTerminalHeight(),
    colorSupport: supportsColor(),
    unicodeSupport: supportsUnicode(),
    isTTY: isTTY(),
    color256: supportsColor256(),
    trueColor: supportsTrueColor(),
  };
}
