import sys, asyncio, os, json
from pathlib import Path
repo_root = Path('/home/amitdevx/Code/Professor_Profiler').resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from dotenv import load_dotenv
load_dotenv(repo_root / '.env')

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from google.genai import types as genai_types

async def run_chat(query: str):
    provider = os.getenv("LLM_PROVIDER", "nim").lower()
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="prof_cli", user_id="default_user", session_id="cli_chat")
    runner = Runner(agent=root_agent, app_name="prof_cli", session_service=session_service, llm_provider=provider)
    
    final_response = ""
    async for event in runner.run_async("default_user", "cli_chat", genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=query)])):
        if type(event).__name__ == 'AgentCallEvent' and hasattr(event, 'agent_name'):
             print(json.dumps({"type": "status", "agent": event.agent_name, "message": f"Calling agent {event.agent_name}..."}), flush=True)
        elif type(event).__name__ == 'AgentResponseEvent' and hasattr(event, 'agent_name'):
             print(json.dumps({"type": "status", "agent": event.agent_name, "message": f"Agent {event.agent_name} completed."}), flush=True)
        
        if event.is_final_response():
            final_response = event.content.parts[0].text
            
    print("FINAL_RESPONSE_START")
    print(final_response)

asyncio.run(run_chat("test query"))
