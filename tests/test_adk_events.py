import sys, asyncio, os
from pathlib import Path
repo_root = Path('.').resolve()
sys.path.insert(0, str(repo_root))
from dotenv import load_dotenv
load_dotenv(repo_root / '.env')

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from google.genai import types as genai_types

async def test_events():
    provider = os.getenv("LLM_PROVIDER", "nim").lower()
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="prof_cli", user_id="default_user", session_id="test_session")
    runner = Runner(agent=root_agent, app_name="prof_cli", session_service=session_service, llm_provider=provider)
    
    async for event in runner.run_async("default_user", "test_session", genai_types.Content(role="user", parts=[genai_types.Part.from_text(text="Please analyze physics")])):
        print(f"EVENT: {type(event).__name__}")
        if hasattr(event, "agent_name"): print(f"agent_name: {event.agent_name}")
        if hasattr(event, "tool_calls"): print(f"tool_calls: {event.tool_calls}")

asyncio.run(test_events())
