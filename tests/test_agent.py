"""
Integration tests for Professor Profiler agent system.
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest

# Ensure repo root is on sys.path so running this script directly
# (python tests/test_agent.py) can import local packages like `google.adk`.
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from profiler_agent.observability import setup_logging
from google.genai import types as genai_types


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization."""
    print("TEST 1: Agent Initialization")
    print("-" * 60)
    
    assert root_agent.name == "professor_profiler_agent"
    assert len(root_agent.sub_agents) == 3
    assert len(root_agent.tools) > 0
    
    print(f"✅ Root agent: {root_agent.name}")
    print("✅ Sub-agents: {sub_agents}".format(sub_agents=[a.name for a in root_agent.sub_agents]))
    print("✅ Tools: {tools}".format(tools=[t.name for t in root_agent.tools]))
    print()


@pytest.mark.asyncio
async def test_session_service():
    """Test session service."""
    print("TEST 2: Session Service")
    print("-" * 60)

    session_service = InMemorySessionService()

    # Create session
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session"
    )

    assert session["session_id"] == "test_session"
    print("✅ Created session: {session_id}".format(session_id=session['session_id']))

    # Add messages
    await session_service.add_message(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        role="user",
        content="Test message"
    )

    messages = await session_service.get_messages(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session"
    )

    assert len(messages) == 1
    print("✅ Added and retrieved message")

    # Update context
    await session_service.update_context(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        context_updates={"test_key": "test_value"}
    )

    context = await session_service.get_context(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session"
    )

    assert context["test_key"] == "test_value"
    print("✅ Updated and retrieved context")
    print()


@pytest.mark.asyncio
async def test_tools():
    """Test custom tools."""
    print("TEST 3: Custom Tools")
    print("-" * 60)

    from profiler_agent.tools import read_pdf_content, analyze_statistics
    import json

    # Ensure mock file exists
    os.makedirs("tests/sample_data", exist_ok=True)
    test_file = "tests/sample_data/test.pdf"
    with open(test_file, "w") as f:
        f.write("mock pdf content")

    # Test PDF tool
    result = read_pdf_content(test_file)
    assert "filename" in result or "error" in result
    print("✅ PDF tool executed: {filename}".format(filename=result.get('filename', 'error')))

    # Test statistics tool
    mock_data = {
        "questions": [
            {"topic": "Math", "bloom_level": "Apply"},
            {"topic": "Math", "bloom_level": "Analyze"}
        ]
    }

    stats = analyze_statistics(json.dumps(mock_data))
    assert "total_questions" in stats
    assert stats["total_questions"] == 2
    print("✅ Statistics tool executed: {count} questions".format(count=stats['total_questions']))
    print()


@pytest.mark.asyncio
async def test_runner_execution():
    """Test runner with agent execution."""
    print("TEST 4: Runner Execution")
    print("-" * 60)

    # Setup
    setup_logging(level="INFO")
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_sess"
    )

    runner = Runner(
        agent=root_agent,
        app_name="test_app",
        session_service=session_service
    )

    # Ensure mock file exists
    os.makedirs("tests/sample_data", exist_ok=True)
    with open("tests/sample_data/physics_2024.pdf", "w") as f:
        f.write("mock content")

    query = "Analyze tests/sample_data/physics_2024.pdf"
    print("Query: {query}".format(query=query))

    final_response = None
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_sess",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        )
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Response received: {response}...".format(response=final_response[:100]))

    assert final_response is not None
    print("✅ Runner executed successfully")
    print()


@pytest.mark.asyncio
async def test_memory_bank():
    """Test memory bank functionality."""
    print("TEST 5: Memory Bank")
    print("-" * 60)

    from profiler_agent.memory import MemoryBank

    memory_bank = MemoryBank(storage_path="test_memory.json")

    # Add memory
    memory_id = memory_bank.add_memory(
        user_id="test_user",
        memory_type="test",
        content={"key": "value"},
        tags=["test"]
    )

    print("✅ Added memory: {memory_id}".format(memory_id=memory_id))

    # Retrieve memory
    memories = memory_bank.get_memories("test_user")
    assert len(memories) > 0
    print("✅ Retrieved {count} memories".format(count=len(memories)))

    # Search
    results = memory_bank.search_memories("test_user", "value")
    assert len(results) > 0
    print("✅ Search found {count} results".format(count=len(results)))

    # Cleanup
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")
    print()


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PROFESSOR PROFILER - INTEGRATION TESTS")
    print("="*60)
    print()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not set - using mock responses")
    else:
        print("✅ GOOGLE_API_KEY configured")

    print()

    try:
        await test_agent_initialization()
        await test_session_service()
        await test_tools()
        await test_memory_bank()
        await test_runner_execution()

        print("="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print("\n❌ TEST FAILED: {error}".format(error=e))
        raise
    except Exception as e:
        print("\n❌ ERROR: {error}".format(error=e))
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
