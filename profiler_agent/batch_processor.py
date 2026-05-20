"""Batch PDF processing helpers for provider rate and context limits."""
import asyncio
from typing import Any, Dict, List


class BatchPDFProcessor:
    """Process PDFs in small batches with optional concurrency control."""

    def __init__(self, max_concurrent: int = 1, batch_size: int = 5, batch_pause_seconds: float = 2.0):
        if max_concurrent <= 0:
            raise ValueError("max_concurrent must be positive")
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.batch_pause_seconds = batch_pause_seconds

    async def process_batch(self, pdf_files: List[str], agent: Any) -> Dict[str, Any]:
        """Process a list of PDF paths through an initialized agent."""
        results: Dict[str, Any] = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)

        for batch_index, start in enumerate(range(0, len(pdf_files), self.batch_size)):
            batch = pdf_files[start:start + self.batch_size]
            if batch_index > 0:
                await self._compact_memory()
                await asyncio.sleep(self.batch_pause_seconds)

            async def run_one(pdf_file: str):
                async with semaphore:
                    return pdf_file, await agent.run(
                        prompt=f"Process exam paper: {pdf_file}",
                        context={"batch_number": batch_index, "pdf_file": pdf_file},
                    )

            for pdf_file, result in await asyncio.gather(*(run_one(pdf_file) for pdf_file in batch)):
                results[pdf_file] = result

        return results

    async def _compact_memory(self) -> None:
        """Compact persisted memory if the optional memory bank is in use."""
        from profiler_agent.memory import MemoryBank

        memory_bank = MemoryBank()
        await memory_bank.compact_and_summarize()
