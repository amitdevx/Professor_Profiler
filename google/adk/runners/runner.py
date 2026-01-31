"""Runner for executing agents with Gemini API."""
import os
import asyncio
import logging
from typing import Optional, AsyncIterator, Any, Dict
from google.genai import types as genai_types
from google import genai


logger = logging.getLogger(__name__)


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
    """Execute agents with session management and streaming."""

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
        self.kwargs = kwargs

        # Initialize Gemini client
        if not self.api_key:
            logger.warning("No GOOGLE_API_KEY found, agent will use mock responses")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    async def run_async(
        self,
        user_id: str,
        session_id: str,
        new_message: genai_types.Content,
        **kwargs
    ) -> AsyncIterator[RunnerEvent]:
        """Execute agent and stream results."""

        # Extract message text
        message_text = ""
        if new_message and hasattr(new_message, "parts") and len(new_message.parts) > 0:
            part = new_message.parts[0]
            if hasattr(part, "text"):
                message_text = part.text
            elif hasattr(part, "from_text"):
                message_text = str(part)

        logger.info(f"Running agent {self.agent.name} for session {session_id}")
        logger.debug(f"Message: {message_text[:100]}...")

        # Get or create session
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )

        # Initialize agent with client
        if self.client:
            await self.agent.initialize(self.client)

        # Execute agent
        try:
            # Yield intermediate events
            yield RunnerEvent(
                content=genai_types.Content(
                    role="assistant",
                    parts=[genai_types.Part.from_text(text=f"Processing with {self.agent.name}...")]
                ),
                agent_name=self.agent.name,
                is_final=False
            )

            # Run agent
            if self.client:
                result = await self.agent.run(
                    prompt=message_text,
                    context=session.get("context", {})
                )
                response_text = result.get("response", "No response")
            else:
                # Mock response if no API key
                response_text = f"[Mock Response] {self.agent.name} processed: {message_text[:100]}"

            # Update session with result
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
                    content=response_text
                )

            # Yield final response
            yield RunnerEvent(
                content=genai_types.Content(
                    role="assistant",
                    parts=[genai_types.Part.from_text(text=response_text)]
                ),
                agent_name=self.agent.name,
                is_final=True,
                metadata={"session_id": session_id}
            )

        except Exception as e:
            logger.error(f"Error running agent: {e}", exc_info=True)
            yield RunnerEvent(
                content=genai_types.Content(
                    role="assistant",
                    parts=[genai_types.Part.from_text(text=f"Error: {str(e)}")]
                ),
                agent_name=self.agent.name,
                is_final=True,
                metadata={"error": str(e)}
            )
