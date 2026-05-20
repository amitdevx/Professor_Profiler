"""Runner for executing agents with Gemini or NVIDIA NIM."""
import logging
import os
from typing import Any, AsyncIterator, Dict, Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience dependency
    def load_dotenv(*_args, **_kwargs):
        return False

from google import genai
from google.genai import types as genai_types

from google.adk.clients import NIMClient

logger = logging.getLogger(__name__)
load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class RunnerEvent:
    """Event emitted during agent execution."""

    def __init__(
        self,
        content: Optional[genai_types.Content] = None,
        agent_name: Optional[str] = None,
        is_final: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.agent_name = agent_name
        self._is_final = is_final
        self.metadata = metadata or {}

    def is_final_response(self) -> bool:
        """Check if this is the final response."""
        return self._is_final

    def __repr__(self):
        return f"RunnerEvent(agent='{self.agent_name}', is_final={self._is_final})"


class Runner:
    """Execute agents with session management and provider switching."""

    def __init__(
        self,
        agent: Any,
        app_name: str,
        session_service: Any,
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.agent = agent
        self.app_name = app_name
        self.session_service = session_service
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.llm_provider = str(kwargs.get("llm_provider") or os.getenv("LLM_PROVIDER", "gemini")).lower()
        self.fallback_to_gemini = bool(kwargs.get("fallback_to_gemini", _env_bool("ENABLE_FALLBACK", True)))
        self.kwargs = kwargs
        self.client = self._build_client(self.llm_provider)

    async def run_async(
        self,
        user_id: str,
        session_id: str,
        new_message: genai_types.Content,
        **kwargs
    ) -> AsyncIterator[RunnerEvent]:
        """Execute agent and stream results."""
        message_text = self._extract_message_text(new_message)

        logger.info("Running agent %s for session %s via %s", self.agent.name, session_id, self.llm_provider)
        logger.debug("Message: %s...", message_text[:100])

        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )

        provider_used = self.llm_provider
        fallback_used = False

        try:
            yield RunnerEvent(
                content=genai_types.Content(
                    role="assistant",
                    parts=[genai_types.Part.from_text(text=f"Processing with {self.agent.name} via {self.llm_provider}...")]
                ),
                agent_name=self.agent.name,
                is_final=False,
                metadata={"provider": self.llm_provider}
            )

            try:
                response_text = await self._run_agent_once(
                    provider=self.llm_provider,
                    client=self.client,
                    prompt=message_text,
                    context=session.get("context", {}) if session else {},
                )
            except Exception as primary_error:
                if self.llm_provider == "nim" and self.fallback_to_gemini:
                    logger.warning("NIM execution failed, attempting Gemini fallback: %s", primary_error)
                    fallback_client = self._build_client("gemini")
                    if fallback_client:
                        response_text = await self._run_agent_once(
                            provider="gemini",
                            client=fallback_client,
                            prompt=message_text,
                            context=session.get("context", {}) if session else {},
                        )
                        provider_used = "gemini"
                        fallback_used = True
                        try:
                            from profiler_agent.observability import migration_metrics

                            migration_metrics.log_fallback()
                        except Exception:
                            logger.debug("Fallback metrics logging skipped", exc_info=True)
                    else:
                        raise primary_error
                else:
                    raise

            if session:
                await self.session_service.add_message(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id,
                    role="user",
                    content=message_text
                )
                await self.session_service.add_message(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id,
                    role="assistant",
                    content=response_text,
                    metadata={"provider": provider_used, "fallback_used": fallback_used}
                )

            yield RunnerEvent(
                content=genai_types.Content(
                    role="assistant",
                    parts=[genai_types.Part.from_text(text=response_text)]
                ),
                agent_name=self.agent.name,
                is_final=True,
                metadata={
                    "session_id": session_id,
                    "provider": provider_used,
                    "fallback_used": fallback_used,
                }
            )

        except Exception as e:
            logger.error("Error running agent: %s", e, exc_info=True)
            yield RunnerEvent(
                content=genai_types.Content(
                    role="assistant",
                    parts=[genai_types.Part.from_text(text=f"Error: {str(e)}")]
                ),
                agent_name=self.agent.name,
                is_final=True,
                metadata={"error": str(e), "provider": provider_used}
            )

    def _build_client(self, provider: str):
        if provider == "nim":
            logger.info("Using NVIDIA NIM backend")
            return NIMClient()
        if provider == "gemini":
            if not self.api_key:
                logger.warning("No GOOGLE_API_KEY found; Gemini runner will use mock responses")
                return None
            return genai.Client(api_key=self.api_key)
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

    async def _run_agent_once(self, provider: str, client: Any, prompt: str, context: Dict[str, Any]) -> str:
        if not client:
            return f"[Mock Response] {self.agent.name} processed: {prompt[:100]}"

        await self.agent.initialize(client, provider=provider)
        result = await self.agent.run(prompt=prompt, context=context)
        if result.get("error"):
            raise RuntimeError(result["error"])
        return result.get("response", "No response")

    def _extract_message_text(self, new_message: genai_types.Content) -> str:
        if new_message and hasattr(new_message, "parts") and len(new_message.parts) > 0:
            part = new_message.parts[0]
            if hasattr(part, "text"):
                return part.text or ""
            if hasattr(part, "from_text"):
                return str(part)
        return ""
