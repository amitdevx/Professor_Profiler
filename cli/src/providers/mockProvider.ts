/**
 * @fileoverview Mock AI provider for development and testing.
 * Simulates realistic AI responses with configurable typing delays.
 * @module providers/mockProvider
 */

import {
  BaseProvider,
  type GenerateOptions,
  type ProviderResponse,
  type StreamChunk,
} from './baseProvider.js';

/** Canned responses the mock provider rotates through. */
const CANNED_RESPONSES: readonly string[] = [
  'Based on my analysis of the provided document, here are the key findings:\n\n' +
    '1. **Structure**: The document follows a well-organized hierarchical format with clear section delineation.\n' +
    '2. **Content Quality**: The arguments presented are logically sound and supported by evidence.\n' +
    '3. **Areas for Improvement**: Consider adding more quantitative data to strengthen the conclusions.\n\n' +
    'Overall, this is a solid piece of work that demonstrates strong analytical thinking.',

  'I\'ve reviewed the file and identified several important patterns:\n\n' +
    '- **Consistency**: The writing style is consistent throughout, maintaining a professional tone.\n' +
    '- **Depth**: Each section provides adequate depth without being overly verbose.\n' +
    '- **Citations**: References are properly formatted and relevant to the claims made.\n\n' +
    'My recommendation is to proceed with minor revisions focused on the introduction section.',

  'Here\'s a comprehensive breakdown of the analysis:\n\n' +
    '**Strengths:**\n' +
    '- Clear thesis statement\n' +
    '- Well-structured arguments\n' +
    '- Effective use of evidence\n\n' +
    '**Weaknesses:**\n' +
    '- Some transitions between sections could be smoother\n' +
    '- The conclusion could more explicitly tie back to the thesis\n\n' +
    'Score: 8.5/10',
];

/**
 * Mock AI provider for local development and testing.
 *
 * This provider simulates realistic AI behavior including:
 * - Configurable response delays to mimic network latency
 * - Character-by-character streaming with randomized typing speeds
 * - AbortController support for cancellation
 * - Rotating canned responses for variety
 *
 * @extends BaseProvider
 * @example
 * ```typescript
 * const mock = new MockProvider({ baseDelayMs: 200 });
 * await mock.initialize();
 * const response = await mock.generate('Analyze this document');
 * ```
 */
export class MockProvider extends BaseProvider {
  /** @inheritdoc */
  readonly name = 'mock';

  /** Index tracking which canned response to use next. */
  private responseIndex = 0;

  /** Base delay in ms before returning a generate() response. */
  private readonly baseDelayMs: number;

  /** Minimum delay in ms between streamed characters. */
  private readonly minCharDelayMs: number;

  /** Maximum delay in ms between streamed characters. */
  private readonly maxCharDelayMs: number;

  /**
   * Create a new MockProvider.
   * @param options - Configuration for simulated delays.
   * @param options.baseDelayMs - Base delay for generate() calls (default: 500).
   * @param options.minCharDelayMs - Min delay per character in stream() (default: 20).
   * @param options.maxCharDelayMs - Max delay per character in stream() (default: 80).
   */
  constructor(options?: {
    baseDelayMs?: number;
    minCharDelayMs?: number;
    maxCharDelayMs?: number;
  }) {
    super();
    this.baseDelayMs = options?.baseDelayMs ?? 500;
    this.minCharDelayMs = options?.minCharDelayMs ?? 20;
    this.maxCharDelayMs = options?.maxCharDelayMs ?? 80;
  }

  /**
   * Initialize the mock provider.
   * Simulates a brief connection delay.
   */
  async initialize(): Promise<void> {
    await this.delay(100);
    this.markInitialized();
  }

  /**
   * Generate a complete mock response.
   * Returns a canned response after simulating processing delay.
   * @param prompt - The input prompt (used to calculate simulated token counts).
   * @param options - Generation options (signal is respected for cancellation).
   * @returns A simulated provider response.
   * @throws {Error} If aborted via AbortController signal.
   */
  async generate(prompt: string, options?: GenerateOptions): Promise<ProviderResponse> {
    this.ensureInitialized();

    const startTime = Date.now();

    // Respect abort signal
    if (options?.signal?.aborted) {
      throw new Error('Generation aborted.');
    }

    await this.delay(this.baseDelayMs, options?.signal);

    const content = this.getNextResponse();
    const promptTokens = Math.ceil(prompt.length / 4);
    const completionTokens = Math.ceil(content.length / 4);

    return {
      content,
      model: options?.model ?? 'mock-v1',
      usage: {
        promptTokens,
        completionTokens,
        totalTokens: promptTokens + completionTokens,
      },
      latencyMs: Date.now() - startTime,
      truncated: false,
    };
  }

  /**
   * Stream a mock response character by character.
   * Simulates realistic typing with randomized delays between characters.
   * @param prompt - The input prompt.
   * @param options - Generation options (signal is respected for cancellation).
   * @yields {StreamChunk} Individual characters with metadata.
   * @throws {Error} If aborted via AbortController signal.
   */
  async *stream(prompt: string, options?: GenerateOptions): AsyncGenerator<StreamChunk> {
    this.ensureInitialized();

    // Suppress unused variable lint — prompt is part of the abstract contract
    void prompt;

    if (options?.signal?.aborted) {
      throw new Error('Stream aborted.');
    }

    const content = this.getNextResponse();
    let tokenCount = 0;

    for (let i = 0; i < content.length; i++) {
      // Check abort signal before each character
      if (options?.signal?.aborted) {
        throw new Error('Stream aborted.');
      }

      const charDelay =
        this.minCharDelayMs + Math.random() * (this.maxCharDelayMs - this.minCharDelayMs);
      await this.delay(charDelay, options?.signal);

      tokenCount++;
      const isLast = i === content.length - 1;

      yield {
        content: content[i],
        done: isLast,
        tokenCount,
      };
    }
  }

  /**
   * Dispose of the mock provider.
   * Resets internal state.
   */
  async dispose(): Promise<void> {
    this.responseIndex = 0;
    this.markDisposed();
  }

  /**
   * Get the next canned response, cycling through available responses.
   * @returns The next canned response string.
   * @private
   */
  private getNextResponse(): string {
    const response = CANNED_RESPONSES[this.responseIndex % CANNED_RESPONSES.length];
    this.responseIndex++;
    return response;
  }

  /**
   * Promise-based delay that respects AbortController signals.
   * @param ms - Milliseconds to wait.
   * @param signal - Optional abort signal.
   * @returns A promise that resolves after the delay or rejects on abort.
   * @private
   */
  private delay(ms: number, signal?: AbortSignal): Promise<void> {
    return new Promise((resolve, reject) => {
      if (signal?.aborted) {
        reject(new Error('Aborted.'));
        return;
      }

      const timer = setTimeout(resolve, ms);

      if (signal) {
        const onAbort = () => {
          clearTimeout(timer);
          reject(new Error('Aborted.'));
        };
        signal.addEventListener('abort', onAbort, { once: true });
      }
    });
  }
}
