/**
 * Abstract BaseTransport class for communication with backend services.
 */
export abstract class BaseTransport {
  /**
   * Send a payload and wait for a single response.
   */
  abstract send(payload: any): Promise<any>;

  /**
   * Stream a response from the backend.
   */
  abstract stream(payload: any): AsyncGenerator<any>;

  /**
   * Connect to the transport layer.
   */
  abstract connect(): Promise<void>;

  /**
   * Disconnect from the transport layer.
   */
  abstract disconnect(): Promise<void>;
}
