import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience dependency
    def load_dotenv(*_args, **_kwargs):
        return False

import google.auth

load_dotenv()

try:
    _, project_id = google.auth.default()
except Exception:
    # If Application Default Credentials are not available (e.g. in CI/local)
    # fall back to the env var or a sensible default so importing this module
    # doesn't raise. Tests can override `GOOGLE_CLOUD_PROJECT` if needed.
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "local")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class ProfilerConfiguration:
    gemini_classifier_model: str = os.getenv("GEMINI_CLASSIFIER_MODEL", "gemini-2.0-flash-exp")
    gemini_analyzer_model: str = os.getenv("GEMINI_ANALYZER_MODEL", "gemini-2.0-pro-exp")
    nim_classifier_model: str = os.getenv("NIM_CLASSIFIER_MODEL", "meta/llama-3.1-70b-instruct")
    nim_analyzer_model: str = os.getenv("NIM_ANALYZER_MODEL", "nvidia/llama-3.1-nemotron-ultra-253b-v1")
    nim_base_url: str = os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
    nim_timeout: int = int(os.getenv("NIM_TIMEOUT", "60"))
    session_backend: str = os.getenv("SESSION_BACKEND", "memory")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    enable_persistence: bool = os.getenv("ENABLE_SESSION_PERSISTENCE", "false").lower() == "true"
    fallback_to_gemini: bool = os.getenv("ENABLE_FALLBACK", "true").lower() == "true"

    @property
    def llm_provider(self) -> str:
        return os.getenv("LLM_PROVIDER", "gemini").lower()

    @property
    def classifier_model(self) -> str:
        if self.llm_provider == "nim":
            return os.getenv("NIM_CLASSIFIER_MODEL", self.nim_classifier_model)
        return os.getenv("GEMINI_CLASSIFIER_MODEL", self.gemini_classifier_model)

    @property
    def analyzer_model(self) -> str:
        if self.llm_provider == "nim":
            return os.getenv("NIM_ANALYZER_MODEL", self.nim_analyzer_model)
        return os.getenv("GEMINI_ANALYZER_MODEL", self.gemini_analyzer_model)

    def create_session_service(self):
        """Create the configured session service backend."""
        if self.session_backend == "redis" and self.enable_persistence:
            from google.adk.sessions.redis_session_service import RedisSessionService

            return RedisSessionService(self.redis_url)

        from google.adk.sessions import InMemorySessionService

        return InMemorySessionService()


config = ProfilerConfiguration()
