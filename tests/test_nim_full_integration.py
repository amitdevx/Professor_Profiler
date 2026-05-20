"""Focused integration coverage for NIM support helpers."""
import sys
from pathlib import Path

import pytest

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from google.adk.clients import RateLimiter
from profiler_agent.batch_processor import BatchPDFProcessor
from profiler_agent.memory import MemoryBank
from profiler_agent.observability import migration_metrics


@pytest.mark.asyncio
async def test_rate_limiter_acquires_initial_token_quickly():
    limiter = RateLimiter(requests_per_minute=60)
    await limiter.acquire()
    assert limiter.tokens <= limiter.max_tokens


@pytest.mark.asyncio
async def test_batch_processor_runs_agent_for_each_pdf():
    class DummyAgent:
        async def run(self, prompt, context=None):
            return {"response": prompt, "context": context}

    processor = BatchPDFProcessor(max_concurrent=2, batch_size=2, batch_pause_seconds=0)
    results = await processor.process_batch(["a.pdf", "b.pdf", "c.pdf"], DummyAgent())

    assert sorted(results.keys()) == ["a.pdf", "b.pdf", "c.pdf"]
    assert results["c.pdf"]["context"]["batch_number"] == 1


@pytest.mark.asyncio
async def test_memory_compaction_creates_summary(tmp_path):
    memory_bank = MemoryBank(storage_path=str(tmp_path / "memory.json"))
    for index in range(25):
        memory_bank.add_memory(
            user_id="user",
            memory_type="exam_analysis",
            content={"index": index, "topic": "physics"},
            tags=["physics"],
        )

    compacted = await memory_bank.compact_and_summarize("user", max_memories_per_user=10)
    memories = memory_bank.memories["user"]

    assert compacted == 15
    assert len(memories) == 11
    assert any(memory["type"] == "compacted_summary" for memory in memories)


def test_migration_metrics_snapshot_updates():
    before = migration_metrics.snapshot()["nim_requests"]
    migration_metrics.log_request("meta/llama-3.1-70b-instruct", latency_ms=12.5, success=True)
    snapshot = migration_metrics.snapshot()

    assert snapshot["nim_requests"] == before + 1
    assert snapshot["avg_latency_ms"] >= 0
