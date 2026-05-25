import asyncio
import json
from profiler_agent.sub_agents.trend_spotter import trend_spotter
from google.genai import types as genai_types

async def main():
    data = json.dumps({"questions": [
        {"topic": "Math", "bloom_level": "Apply"},
        {"topic": "Science", "bloom_level": "Remember"}
    ]})
    async for event in trend_spotter.run_async("user1", "session1", genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=f"Analyze these tagged questions and visualize the trends: {data}")])):
        if event.is_final_response():
            print("Final Response:", event.content.parts[0].text)

asyncio.run(main())
