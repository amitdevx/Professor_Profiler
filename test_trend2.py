import asyncio
import json
from profiler_agent.sub_agents.trend_spotter import trend_spotter
from google.genai import types as genai_types
from google.adk.clients.nim_client import NIMClient

async def main():
    client = NIMClient()
    await trend_spotter.initialize(client)
    data = json.dumps({"questions": [
        {"topic": "Math", "bloom_level": "Apply"},
        {"topic": "Science", "bloom_level": "Remember"}
    ]})
    result = await trend_spotter.run(prompt=f"Analyze these tagged questions using the analyze_statistics tool to compute distributions. Then, YOU MUST use the visualize_trends tool to create a chart. Output a 'Shift Report': {data}")
    print("Final Response:", result)

asyncio.run(main())
