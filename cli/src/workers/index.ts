export class WorkerPool {
  async runTask<T>(taskFn: () => Promise<T>): Promise<T> {
    // For now, just run directly. Worker threads added in v2.
    return taskFn();
  }
}

export const workerPool = new WorkerPool();
