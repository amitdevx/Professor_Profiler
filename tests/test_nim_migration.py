"""Offline tests for the Gemini to NVIDIA NIM migration."""
import importlib
import os
import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from google.adk.agents import Agent
from google.adk.clients import NIMClient
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types as genai_types


@pytest.mark.asyncio
async def test_nim_client_initialization_without_key(monkeypatch):
    monkeypatch.delenv("NIM_API_KEY", raising=False)
    client = NIMClient()

    assert client.provider == "nim"
    assert "nvidia" in client.base_url.lower()
    response = await client.generate_content(
        model="meta/llama-3.1-70b-instruct",
        prompt="hello",
        system_instruction="You are concise.",
    )
    assert response.startswith("[NIM Mock]")


def test_tool_schema_conversion_to_openai():
    def sample_tool(input_text: str, count: int = 1) -> str:
        """Sample tool for testing."""
        return input_text * count

    tool = FunctionTool(func=sample_tool)
    schema = tool.to_openai_schema()

    assert schema["type"] == "function"
    assert schema["function"]["name"] == "sample_tool"
    assert schema["function"]["parameters"]["properties"]["input_text"]["type"] == "string"
    assert schema["function"]["parameters"]["properties"]["count"]["type"] == "integer"
    assert schema["function"]["parameters"]["required"] == ["input_text"]


def test_model_config_switching(monkeypatch):
    import profiler_agent.config as cfg_module

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    importlib.reload(cfg_module)
    assert "gemini" in cfg_module.config.classifier_model.lower()

    monkeypatch.setenv("LLM_PROVIDER", "nim")
    importlib.reload(cfg_module)
    assert "llama" in cfg_module.config.classifier_model.lower()
    assert "/" in cfg_module.config.classifier_model


@pytest.mark.asyncio
async def test_runner_executes_nim_mock_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nim")
    monkeypatch.delenv("NIM_API_KEY", raising=False)

    agent = Agent(
        name="simple_agent",
        model="meta/llama-3.1-70b-instruct",
        nim_model="meta/llama-3.1-70b-instruct",
        gemini_model="gemini-2.0-flash-exp",
        description="Test agent",
    )
    session_service = InMemorySessionService()
    await session_service.create_session("test_app", "test_user", "nim_session")

    runner = Runner(
        agent=agent,
        app_name="test_app",
        session_service=session_service,
        llm_provider="nim",
        fallback_to_gemini=False,
    )

    final_event = None
    async for event in runner.run_async(
        user_id="test_user",
        session_id="nim_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text="Analyze this")],
        ),
    ):
        if event.is_final_response():
            final_event = event

    assert final_event is not None
    assert final_event.metadata["provider"] == "nim"
    assert "[NIM Mock]" in final_event.content.parts[0].text
