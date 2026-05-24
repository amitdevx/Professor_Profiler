/**
 * @module hooks/telemetryHook
 * @description Telemetry lifecycle hook.
 * Tracks anonymized command usage metrics when telemetry is enabled.
 */

import fs from 'fs-extra';
import path from 'node:path';
import os from 'node:os';
import { logger } from '../utils/logger.js';
import type { HookContext } from '../types/index.js';

/**
 * Represents a single telemetry event record.
 */
interface TelemetryEvent {
  /** The command that was executed */
  command: string;
  /** ISO 8601 timestamp of execution */
  timestamp: string;
  /** Execution duration in milliseconds */
  duration: number;
  /** Whether the command succeeded */
  success: boolean;
  /** Active AI provider at time of execution */
  provider: string;
  /** Node.js version */
  nodeVersion: string;
  /** Operating system platform */
  platform: string;
}

/** Path to the local telemetry data file */
const TELEMETRY_DIR = path.join(os.homedir(), '.professor-profiler');
const TELEMETRY_FILE = path.join(TELEMETRY_DIR, 'telemetry.json');

/**
 * Telemetry lifecycle hook.
 *
 * Tracks anonymized command usage metrics when telemetry is enabled in the
 * CLI configuration. Data is stored locally in `~/.professor-profiler/telemetry.json`
 * and is never transmitted externally.
 *
 * @param context - The hook context for the executed command
 */
export async function telemetryHook(context: HookContext): Promise<void> {
  if (!context.config.telemetryEnabled) {
    logger.debug('Telemetry is disabled — skipping', 'hooks:telemetry');
    return;
  }

  const duration = Date.now() - context.startTime.getTime();

  const event: TelemetryEvent = {
    command: context.commandName,
    timestamp: new Date().toISOString(),
    duration,
    success: true,
    provider: context.config.provider,
    nodeVersion: process.version,
    platform: process.platform,
  };

  try {
    await fs.ensureDir(TELEMETRY_DIR);

    let events: TelemetryEvent[] = [];

    if (await fs.pathExists(TELEMETRY_FILE)) {
      const raw = await fs.readJson(TELEMETRY_FILE) as TelemetryEvent[];
      events = Array.isArray(raw) ? raw : [];
    }

    // Keep only the last 1000 events to prevent unbounded growth
    if (events.length >= 1000) {
      events = events.slice(-999);
    }

    events.push(event);
    await fs.writeJson(TELEMETRY_FILE, events, { spaces: 2 });

    logger.debug(
      `Telemetry event recorded for command: ${context.commandName}`,
      'hooks:telemetry',
    );
  } catch (err) {
    // Telemetry failures should never break the CLI
    logger.debug(
      `Telemetry write failed: ${err instanceof Error ? err.message : String(err)}`,
      'hooks:telemetry',
    );
  }
}
