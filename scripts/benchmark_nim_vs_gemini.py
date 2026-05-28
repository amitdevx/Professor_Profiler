"""Compare Gemini and NVIDIA NIM runner latency.

This script uses the configured real provider when keys are present and the
repo's mock paths otherwise, so it is safe to run offline.
"""
import asyncio
import json
import os
import statistics
import time
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from profiler_agent.agent import root_agent

TASKS = [
    "Classify these questions by Bloom's level: Explain inertia. Solve a circuit.",
    "Analyze exam trends from these summarized topic counts.",
    "Generate study recommendations from a short trend report.",
]

async def benchmark_provider(provider: str, task: str, iterations: int = 3):
    os.environ["LLM_PROVIDER"] = provider
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="benchmark",
        session_service=session_service,
        llm_provider=provider,
    )
    times = []
    last_response = ""

    for index in range(iterations):
        session_id = f"{provider}-{abs(hash(task))}-{index}"
        await session_service.create_session("benchmark", "bench_user", session_id)
        start = time.monotonic()
        async for event in runner.run_async(
            user_id="bench_user",
            session_id=session_id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=task)],
            ),
        ):
            if event.is_final_response():
                last_response = event.content.parts[0].text
        times.append(time.monotonic() - start)

    return {
        "provider": provider,
        "task": task,
        "iterations": iterations,
        "avg_seconds": statistics.mean(times),
        "min_seconds": min(times),
        "max_seconds": max(times),
        "response_preview": last_response[:120],
    }

async def main():
    results = []
    for task in TASKS:
        for provider in ("gemini", "nim"):
            results.append(await benchmark_provider(provider, task))
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
