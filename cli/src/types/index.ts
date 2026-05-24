/**
 * @module types
 * @description Core type definitions for the Professor Profiler CLI.
 * All interfaces used across the application are defined and exported from here.
 */

/**
 * Represents the status lifecycle of an agent task.
 */
export type AgentTaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

/**
 * Represents a single task assigned to an AI agent.
 */
export interface AgentTask {
  /** Unique identifier for the task */
  id: string;
  /** Human-readable name of the task */
  name: string;
  /** Current execution status */
  status: AgentTaskStatus;
  /** Timestamp when the task was started */
  startTime: Date;
  /** Timestamp when the task completed (if finished) */
  endTime?: Date;
  /** Result data from the completed task */
  result?: unknown;
}

/**
 * Encapsulates the result returned by an agent after task execution.
 */
export interface AgentResult {
  /** Name of the agent that produced this result */
  agentName: string;
  /** Whether the agent completed successfully */
  success: boolean;
  /** The output data from the agent */
  data: unknown;
  /** Error message if the agent failed */
  error?: string | null;
  /** Execution duration in milliseconds */
  duration: number;
}

/**
 * Represents the type of content in a stream chunk.
 */
export type StreamChunkType = 'text' | 'status' | 'error';

/**
 * A single chunk of streamed output from an agent.
 */
export interface StreamChunk {
  /** The text token or content fragment */
  token: string;
  /** Name of the agent producing this chunk */
  agentName: string;
  /** Timestamp when this chunk was generated */
  timestamp: Date;
  /** The type of content this chunk represents */
  type: StreamChunkType;
}

/**
 * Response data from an AI provider (e.g., Gemini, OpenAI).
 */
export interface ProviderResponse {
  /** The generated text content */
  content: string;
  /** The model identifier used for generation */
  model: string;
  /** Total tokens consumed (prompt + completion) */
  tokensUsed: number;
  /** Round-trip latency in milliseconds */
  latencyMs: number;
}

/**
 * Top-level CLI configuration persisted to disk.
 */
export interface CLIConfig {
  /** Active AI provider name (e.g., 'gemini', 'openai') */
  provider: string;
  /** Model identifier to use for inference */
  model: string;
  /** UI theme name */
  theme: string;
  /** Map of provider names to their API keys */
  apiKeys: Record<string, string>;
  /** Directory path for analysis output files */
  outputDir: string;
  /** Whether anonymous usage telemetry is enabled */
  telemetryEnabled: boolean;
}

/**
 * Configuration for a specific AI provider.
 */
export interface ProviderConfig {
  /** Provider display name */
  name: string;
  /** Authentication API key */
  apiKey: string;
  /** Base URL for the provider's API */
  baseUrl: string;
  /** Default model to use */
  model: string;
  /** Request timeout in milliseconds */
  timeout: number;
}

/**
 * Represents the state of an interactive CLI session.
 */
export interface SessionState {
  /** Unique session identifier */
  sessionId: string;
  /** Timestamp when the session was started */
  startTime: Date;
  /** Ordered history of user inputs and agent responses */
  history: Array<{ role: 'user' | 'assistant'; content: string; timestamp: Date }>;
  /** Arbitrary key-value context data for the session */
  context: Map<string, unknown>;
}

/**
 * Metadata about a resolved file reference (from @file syntax).
 */
export interface FileInfo {
  /** Original file name */
  name: string;
  /** Absolute path to the file */
  path: string;
  /** File size in bytes */
  size: number;
  /** MIME type or file extension type */
  type: string;
  /** Timestamp when the file was resolved */
  resolvedAt: Date;
}

/**
 * Metadata describing a CLI command for help generation and routing.
 */
export interface CommandMeta {
  /** Primary command name */
  name: string;
  /** Human-readable description */
  description: string;
  /** Alternative names for the command */
  aliases: string[];
  /** Usage pattern string (e.g., 'analyze <file> [options]') */
  usage: string;
  /** Array of example invocations */
  examples: string[];
}

/**
 * Context object passed to lifecycle hooks (pre/post command, error, telemetry).
 */
export interface HookContext {
  /** Name of the command being executed */
  commandName: string;
  /** Raw arguments passed to the command */
  args: string[];
  /** Timestamp when the command started */
  startTime: Date;
  /** Current CLI configuration snapshot */
  config: CLIConfig;
}
