/**
 * @module ui/renderers/streamRenderer
 * @description Renders streaming AI tokens to stdout with a smooth typing effect.
 * Supports abort signals and handles text / status / error chunk types.
 */

import chalk from 'chalk';

import type { StreamChunk } from '../../types/index.js';

/**
 * Delay execution for the specified number of milliseconds.
 *
 * @param ms - Milliseconds to wait.
 * @returns A promise that resolves after the delay.
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Renders an async stream of {@link StreamChunk} objects to the terminal
 * with a smooth character-by-character typing animation.
 */
export class StreamRenderer {
  /** Per-character delay in ms for the typing effect. */
  private readonly charDelay: number;

  /**
   * @param charDelay - Milliseconds between each rendered character (default 8).
   */
  constructor(charDelay = 8) {
    this.charDelay = charDelay;
  }

  /**
   * Consume an async generator of stream chunks and render them in real time.
   *
   * - `text` chunks are typed character-by-character.
   * - `status` chunks are shown as dimmed status lines.
   * - `error` chunks are highlighted in red.
   *
   * @param stream  - The async chunk generator to consume.
   * @param signal  - Optional `AbortSignal` to cancel rendering.
   *
   * @example
   * ```ts
   * const controller = new AbortController();
   * await streamRenderer.render(myStream(), controller.signal);
   * ```
   */
  async render(
    stream: AsyncGenerator<StreamChunk, void, unknown>,
    signal?: AbortSignal,
  ): Promise<void> {
    try {
      for await (const chunk of stream) {
        if (signal?.aborted) {
          process.stdout.write(chalk.dim('\n\n⏹  Stream stopped.\n'));
          return;
        }

        switch (chunk.type) {
          case 'text':
            await this.renderText(chunk.token, signal);
            break;

          case 'status':
            this.renderStatus(chunk.token);
            break;

          case 'error':
            this.renderError(chunk.token);
            break;

          default:
            await this.renderText(chunk.token, signal);
        }
      }

      // Final newline after stream completes
      process.stdout.write('\n');
    } catch (err) {
      if (signal?.aborted) {
        process.stdout.write(chalk.dim('\n\n⏹  Stream aborted.\n'));
        return;
      }
      throw err;
    }
  }

  /**
   * Render a text chunk character-by-character.
   *
   * @param text   - The text content to display.
   * @param signal - Optional abort signal.
   */
  private async renderText(text: string, signal?: AbortSignal): Promise<void> {
    for (const char of text) {
      if (signal?.aborted) return;
      process.stdout.write(char);
      if (this.charDelay > 0) {
        await sleep(this.charDelay);
      }
    }
  }

  /**
   * Render a status message on its own line.
   *
   * @param status - The status text.
   */
  private renderStatus(status: string): void {
    process.stdout.write(`\n${chalk.dim.italic(`⟡  ${status}`)}\n`);
  }

  /**
   * Render an error message highlighted in red.
   *
   * @param error - The error text.
   */
  private renderError(error: string): void {
    process.stdout.write(`\n${chalk.red.bold(`✖  ${error}`)}\n`);
  }
}

/**
 * Pre-instantiated singleton for convenience.
 */
export const streamRenderer = new StreamRenderer();
