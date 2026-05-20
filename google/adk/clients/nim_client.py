"""NVIDIA NIM client wrapper with an OpenAI-compatible chat interface."""
import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience dependency
    def load_dotenv(*_args, **_kwargs):
        return False

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover - allows offline tests before deps install
    AsyncOpenAI = None

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:  # pragma: no cover - graceful fallback before deps install
    def retry(*_args, **_kwargs):
        def decorator(func):
            return func
        return decorator

    def stop_after_attempt(_attempts):
        return None

    def wait_exponential(**_kwargs):
        return None

from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)
load_dotenv()


class NIMClient:
    """Small adapter around NVIDIA NIM's OpenAI-compatible endpoint."""

    provider = "nim"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        requests_per_minute: Optional[int] = None,
    ):
        self.api_key = api_key or os.getenv("NIM_API_KEY")
        self.base_url = base_url or os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.timeout = int(timeout or os.getenv("NIM_TIMEOUT", "60"))
        rpm = int(requests_per_minute or os.getenv("NIM_REQUESTS_PER_MINUTE", "100"))
        self.rate_limiter = RateLimiter(requests_per_minute=rpm)
        self.client = None

        if not self.api_key:
            logger.warning("No NIM_API_KEY found; NIM client will return mock responses")
        elif AsyncOpenAI is None:
            logger.warning("openai package is not installed; NIM client will return mock responses")
        else:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )

    async def generate_content(
        self,
        model: str,
        prompt: str,
        system_instruction: str = "",
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        """Generate a text response or a serialized tool call request."""
        if not self.client:
            return f"[NIM Mock] {prompt[:100]}"

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        request_kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": float(kwargs.get("temperature", os.getenv("NIM_TEMPERATURE", "0.7"))),
            "top_p": float(kwargs.get("top_p", os.getenv("NIM_TOP_P", "0.95"))),
            "max_tokens": int(kwargs.get("max_output_tokens", os.getenv("NIM_MAX_TOKENS", "2048"))),
        }

        normalized_tools = self._normalize_tools(tools)
        if normalized_tools:
            request_kwargs["tools"] = normalized_tools
            request_kwargs["tool_choice"] = "auto"

        await self.rate_limiter.acquire()
        return await self._request_with_retry(request_kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _request_with_retry(self, request_kwargs: Dict[str, Any]) -> str:
        start = time.monotonic()
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(**request_kwargs),
                timeout=self.timeout,
            )
            latency_ms = (time.monotonic() - start) * 1000
            self._log_metrics(request_kwargs["model"], latency_ms, success=True)
            return self._extract_response(response)
        except asyncio.TimeoutError:
            latency_ms = (time.monotonic() - start) * 1000
            self._log_metrics(request_kwargs.get("model", "unknown"), latency_ms, success=False)
            logger.warning("NIM request timed out after %ss", self.timeout)
            raise
        except Exception:
            latency_ms = (time.monotonic() - start) * 1000
            self._log_metrics(request_kwargs.get("model", "unknown"), latency_ms, success=False)
            logger.exception("NIM API request failed")
            raise

    def _extract_response(self, response: Any) -> str:
        if not getattr(response, "choices", None):
            return ""

        message = response.choices[0].message
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            tool_call = tool_calls[0]
            function = tool_call.function
            return f"TOOL_CALL:{function.name}:{function.arguments or '{}'}"

        return getattr(message, "content", "") or ""

    def _normalize_tools(self, tools: Optional[Any]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        if isinstance(tools, dict) and "function_declarations" in tools:
            return [self._gemini_declaration_to_openai(tool) for tool in tools["function_declarations"]]
        return list(tools)

    def _gemini_declaration_to_openai(self, declaration: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": declaration.get("name", "tool"),
                "description": declaration.get("description", ""),
                "parameters": declaration.get("parameters", {"type": "object", "properties": {}}),
            },
        }

    def _log_metrics(self, model: str, latency_ms: float, success: bool) -> None:
        try:
            from profiler_agent.observability import migration_metrics

            migration_metrics.log_request(model=model, latency_ms=latency_ms, success=success)
        except Exception:
            logger.debug("Migration metrics logging skipped", exc_info=True)
