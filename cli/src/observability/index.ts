export class Observability {
  private traces: Map<string, number> = new Map();
  private metrics: Record<string, number[]> = {};

  startTrace(name: string): string {
    const traceId = `${name}_${Date.now()}_${Math.random()}`;
    this.traces.set(traceId, Date.now());
    return traceId;
  }

  endTrace(traceId: string): { name: string; durationMs: number } | null {
    const start = this.traces.get(traceId);
    if (!start) return null;
    
    const durationMs = Date.now() - start;
    this.traces.delete(traceId);
    
    const name = traceId.split('_')[0];
    this.recordMetric(`${name}_duration`, durationMs);
    
    return { name, durationMs };
  }

  recordMetric(name: string, value: number) {
    if (!this.metrics[name]) {
      this.metrics[name] = [];
    }
    this.metrics[name].push(value);
  }

  getMetrics(): Record<string, number[]> {
    return this.metrics;
  }

  getSummary(): Record<string, { avg: number; min: number; max: number; count: number }> {
    const summary: Record<string, any> = {};
    for (const [key, values] of Object.entries(this.metrics)) {
      if (values.length === 0) continue;
      const sum = values.reduce((a, b) => a + b, 0);
      summary[key] = {
        avg: sum / values.length,
        min: Math.min(...values),
        max: Math.max(...values),
        count: values.length
      };
    }
    return summary;
  }
}

export const observability = new Observability();
