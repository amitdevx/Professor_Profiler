import os
from dataclasses import dataclass
import google.auth

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

@dataclass
class ProfilerConfiguration:
    classifier_model: str = "gemini-2.5-flash"
    analyzer_model: str = "gemini-2.5-pro"

config = ProfilerConfiguration()
