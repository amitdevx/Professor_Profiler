"""Callback context for agent post-processing."""
from typing import Any, Optional, Dict
from google.genai.types import Content


class CallbackContext:
    """Context passed to after_agent_callback functions."""

    def __init__(
        self,
        agent: Any,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent = agent
        self.response = response
        self.metadata = metadata or {}

    def get_response_text(self) -> str:
        """Get response as text."""
        return str(self.response)

    def to_content(self) -> Content:
        """Convert response to Content object."""
        return Content(
            role="assistant",
            parts=[{"text": self.get_response_text()}]
        )
