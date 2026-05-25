"""Async token-bucket rate limiting for hosted LLM APIs."""
import asyncio
import time


class RateLimiter:
    """Simple token-bucket limiter measured in requests per minute."""

    def __init__(self, requests_per_minute: int = 100):
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        self.max_tokens = float(requests_per_minute)
        self.tokens = float(requests_per_minute)
        self.refill_rate = float(requests_per_minute) / 60.0
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until one request token is available."""
        async with self.lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
                self.last_update = now

                if self.tokens >= 1:
                    self.tokens -= 1
                    return

                sleep_time = (1 - self.tokens) / self.refill_rate
                await asyncio.sleep(max(sleep_time, 0.01))
