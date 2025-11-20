import asyncio
import os
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from google.genai import types as genai_types

async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="app", user_id="user", session_id="sess")
    runner = Runner(agent=root_agent, app_name="app", session_service=session_service)
    
    # Ensure mock file exists
    os.makedirs("tests/sample_data", exist_ok=True)
    with open("tests/sample_data/physics_2024.pdf", "w") as f: f.write("mock")

    query = "Analyze tests/sample_data/physics_2024.pdf"
    print(f"&gt;&gt;&gt; {query}")
    async for event in runner.run_async(user_id="user", session_id="sess", new_message=genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=query)])):
        if event.is_final_response(): print(event.content.parts[0].text)

if __name__ == "__main__": asyncio.run(main())
