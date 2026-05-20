"""Observability module for logging, tracing, and metrics."""
import logging
import time
import json
import uuid
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime
from collections import defaultdict
import threading
from .paths import get_output_path


# Configure structured logging
class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields if present
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        if hasattr(record, "agent_name"):
            log_data["agent_name"] = record.agent_name
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(level: str = "INFO", structured: bool = False, log_file: Optional[str] = None):
    """
    Setup logging configuration.

    Args:
        level: Log level (INFO, DEBUG, WARNING, ERROR)
        structured: Use JSON structured logging
        log_file: Optional log file name (saved to output/logs/)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Set formatter
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if requested
    if log_file:
        log_path = get_output_path(log_file, "logs")
        file_handler = logging.FileHandler(str(log_path))
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_path}")

    return logger


class Tracer:
    """Distributed tracing for agent operations."""

    def __init__(self):
        self._traces: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def start_trace(self, operation: str, metadata: Optional[Dict] = None) -> str:
        """Start a new trace."""
        trace_id = str(uuid.uuid4())

        with self._lock:
            self._traces[trace_id] = {
                "trace_id": trace_id,
                "operation": operation,
                "start_time": time.time(),
                "metadata": metadata or {},
                "spans": []
            }

        return trace_id

    def add_span(
        self,
        trace_id: str,
        span_name: str,
        duration_ms: float,
        metadata: Optional[Dict] = None
    ):
        """Add a span to an existing trace."""
        with self._lock:
            if trace_id in self._traces:
                self._traces[trace_id]["spans"].append({
                    "name": span_name,
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                    "metadata": metadata or {}
                })

    def end_trace(self, trace_id: str) -> Dict[str, Any]:
        """End a trace and return the trace data."""
        with self._lock:
            if trace_id not in self._traces:
                return {}

            trace = self._traces[trace_id]
            trace["end_time"] = time.time()
            trace["total_duration_ms"] = (trace["end_time"] - trace["start_time"]) * 1000

            return trace

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace data by ID."""
        with self._lock:
            return self._traces.get(trace_id)


class MetricsCollector:
    """Collect and aggregate metrics."""

    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()

    def increment(self, metric: str, value: int = 1, tags: Optional[Dict] = None):
        """Increment a counter."""
        key = self._make_key(metric, tags)
        with self._lock:
            self._counters[key] += value

    def gauge(self, metric: str, value: float, tags: Optional[Dict] = None):
        """Set a gauge value."""
        key = self._make_key(metric, tags)
        with self._lock:
            self._gauges[key] = value

    def histogram(self, metric: str, value: float, tags: Optional[Dict] = None):
        """Add a value to histogram."""
        key = self._make_key(metric, tags)
        with self._lock:
            self._histograms[key].append(value)

    def _make_key(self, metric: str, tags: Optional[Dict] = None) -> str:
        """Create metric key with tags."""
        if not tags:
            return metric

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric}{{{tag_str}}}"

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        with self._lock:
            # Calculate histogram statistics
            histogram_stats = {}
            for key, values in self._histograms.items():
                if values:
                    histogram_stats[key] = {
                        "count": len(values),
                        "sum": sum(values),
                        "mean": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values)
                    }

            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": histogram_stats,
                "timestamp": datetime.utcnow().isoformat()
            }

    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


# Global instances
tracer = Tracer()
metrics = MetricsCollector()


class MigrationMetrics:
    """Track provider migration metrics for NIM rollout visibility."""

    def __init__(self):
        self._lock = threading.Lock()
        self._metrics = {
            "nim_requests": 0,
            "nim_failures": 0,
            "nim_latency_ms": [],
            "fallback_to_gemini": 0,
            "rate_limit_hits": 0,
        }

    def log_request(self, model: str, latency_ms: float, success: bool):
        with self._lock:
            self._metrics["nim_requests"] += 1
            if not success:
                self._metrics["nim_failures"] += 1
            self._metrics["nim_latency_ms"].append(latency_ms)
            request_count = self._metrics["nim_requests"]
            recent_latency = list(self._metrics["nim_latency_ms"][-10:])

        metrics.histogram("nim.request.duration_ms", latency_ms, {"model": model})
        metrics.increment("nim.request.success" if success else "nim.request.failure", tags={"model": model})

        if request_count % 10 == 0 and recent_latency:
            logging.getLogger(__name__).info(json.dumps({
                "type": "migration_metrics",
                "provider": "nim",
                "model": model,
                "requests": request_count,
                "avg_latency_ms": sum(recent_latency) / len(recent_latency),
                "failures": self._metrics["nim_failures"],
                "fallbacks": self._metrics["fallback_to_gemini"],
            }))

    def log_fallback(self):
        with self._lock:
            self._metrics["fallback_to_gemini"] += 1
        metrics.increment("nim.fallback_to_gemini")

    def log_rate_limit_hit(self):
        with self._lock:
            self._metrics["rate_limit_hits"] += 1
        metrics.increment("nim.rate_limit_hit")

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            latency = list(self._metrics["nim_latency_ms"])
            return {
                "nim_requests": self._metrics["nim_requests"],
                "nim_failures": self._metrics["nim_failures"],
                "fallback_to_gemini": self._metrics["fallback_to_gemini"],
                "rate_limit_hits": self._metrics["rate_limit_hits"],
                "avg_latency_ms": (sum(latency) / len(latency)) if latency else 0,
            }


migration_metrics = MigrationMetrics()



def trace_operation(operation_name: str):
    """Decorator to trace function execution."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            trace_id = tracer.start_trace(operation_name)
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                tracer.add_span(trace_id, operation_name, duration_ms, {"status": "success"})
                metrics.histogram(f"{operation_name}.duration_ms", duration_ms)
                metrics.increment(f"{operation_name}.success")

                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                tracer.add_span(trace_id, operation_name, duration_ms, {"status": "error", "error": str(e)})
                metrics.increment(f"{operation_name}.error")
                raise
            finally:
                tracer.end_trace(trace_id)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            trace_id = tracer.start_trace(operation_name)
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                tracer.add_span(trace_id, operation_name, duration_ms, {"status": "success"})
                metrics.histogram(f"{operation_name}.duration_ms", duration_ms)
                metrics.increment(f"{operation_name}.success")

                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                tracer.add_span(trace_id, operation_name, duration_ms, {"status": "error", "error": str(e)})
                metrics.increment(f"{operation_name}.error")
                raise
            finally:
                tracer.end_trace(trace_id)

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_agent_event(logger: logging.Logger, event_type: str, agent_name: str, **kwargs):
    """Log agent-specific events with structured data."""
    extra = {
        "agent_name": agent_name,
        "event_type": event_type,
        **kwargs
    }

    message = f"Agent event: {event_type} - {agent_name}"
    logger.info(message, extra=extra)
