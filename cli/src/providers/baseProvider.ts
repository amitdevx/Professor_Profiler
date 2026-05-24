/**
 * @fileoverview Abstract base class for all AI providers in Professor Profiler.
 * Defines the contract that concrete providers must implement for AI generation.
 * @module providers/baseProvider
 */

/**
 * Options for configuring AI generation requests.
 */
export interface GenerateOptions {
  /** The model identifier to use for generation (e.g., 'gemini-pro'). */
  model?: string;
  /** Controls randomness in output. Range: 0.0 (deterministic) to 2.0 (creative). */
  temperature?: number;
  /** Maximum number of tokens to generate in the response. */
  maxTokens?: number;
  /** AbortController signal to cancel the request. */
  signal?: AbortSignal;
  /** System prompt to prepend to the generation context. */
  systemPrompt?: string;
}

/**
 * Structured response from an AI provider.
 */
export interface ProviderResponse {
  /** The generated text content. */
  content: string;
  /** The model that produced this response. */
  model: string;
  /** Token usage statistics. */
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  /** Time taken to generate the response in milliseconds. */
  latencyMs: number;
  /** Whether the response was truncated due to max tokens. */
  truncated: boolean;
}

/**
 * A chunk of streamed output from an AI provider.
 */
export interface StreamChunk {
  /** The token or text fragment. */
  content: string;
  /** Whether this is the final chunk. */
  done: boolean;
  /** Cumulative token count so far. */
  tokenCount?: number;
}

/**
 * Abstract base class for all AI providers.
 *
 * Providers encapsulate the logic for communicating with different AI backends
 * (e.g., Gemini, OpenAI, local models). Every provider must implement the
 * core methods: `initialize`, `generate`, `stream`, and `dispose`.
 *
 * @abstract
 * @example
 * ```typescript
 * class MyProvider extends BaseProvider {
 *   name = 'my-provider';
 *   async initialize() { // connect to API }
 *   async generate(prompt, options) { // ... }
 *   async *stream(prompt, options) { // ... }
 *   async dispose() { // cleanup }
 * }
 * ```
 */
export abstract class BaseProvider {
  /** Whether this provider has been successfully initialized. */
  private _initialized = false;

  /** Human-readable name for this provider. */
  abstract readonly name: string;

  /** Whether this provider has been successfully initialized. */
  get isInitialized(): boolean {
    return this._initialized;
  }

  /**
   * Initialize the provider (API key validation, connection setup, etc.).
   * Must be called before `generate()` or `stream()`.
   * @throws {Error} If initialization fails.
   */
  abstract initialize(): Promise<void>;

  /**
   * Generate a complete response for the given prompt.
   * @param prompt - The input prompt text.
   * @param options - Optional generation configuration.
   * @returns The complete provider response.
   * @throws {Error} If generation fails or is aborted.
   */
  abstract generate(prompt: string, options?: GenerateOptions): Promise<ProviderResponse>;

  /**
   * Stream a response token-by-token for the given prompt.
   * @param prompt - The input prompt text.
   * @param options - Optional generation configuration.
   * @yields {StreamChunk} Individual tokens/chunks as they are generated.
   * @throws {Error} If streaming fails or is aborted.
   */
  abstract stream(prompt: string, options?: GenerateOptions): AsyncGenerator<StreamChunk>;

  /**
   * Clean up resources held by this provider.
   * Should be called when the provider is no longer needed.
   */
  abstract dispose(): Promise<void>;

  /**
   * Marks this provider as initialized. Should be called by subclasses
   * at the end of their `initialize()` implementation.
   * @protected
   */
  protected markInitialized(): void {
    this._initialized = true;
  }

  /**
   * Marks this provider as not initialized. Useful during dispose.
   * @protected
   */
  protected markDisposed(): void {
    this._initialized = false;
  }

  /**
   * Guard that throws if the provider is not initialized.
   * Subclasses should call this at the start of `generate()` and `stream()`.
   * @protected
   * @throws {Error} If provider is not initialized.
   */
  protected ensureInitialized(): void {
    if (!this._initialized) {
      throw new Error(`Provider '${this.name}' is not initialized. Call initialize() first.`);
    }
  }
}
