import os
from dataclasses import dataclass
import google.auth

try:
    _, project_id = google.auth.default()
except Exception:
    # If Application Default Credentials are not available (e.g. in CI/local test),
    # fall back to the env var or a sensible default so importing this module
    # doesn't raise. Tests can override `GOOGLE_CLOUD_PROJECT` if needed.
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "local")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

@dataclass
class ProfilerConfiguration:
    classifier_model: str = "gemini-3-flash"
    analyzer_model: str = "gemini-3-pro"

config = ProfilerConfiguration()
