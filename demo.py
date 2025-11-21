"""
Comprehensive demo script for Professor Profiler agent.

This demo showcases:
1. Multi-agent system (Hub-and-Spoke with sequential sub-agents)
2. Custom tools (PDF reading, statistics, visualization)
3. Sessions & Memory (InMemorySessionService + MemoryBank)
4. Observability (Logging, Tracing, Metrics)
5. Gemini API integration

Usage:
    # Place your exam PDFs in the input/ folder
    export GOOGLE_API_KEY=your_api_key_here
    python demo.py
    
    # Results will be saved to output/ folder:
    # - output/charts/ - Visualization charts
    # - output/logs/ - Log files
    # - output/reports/ - Analysis reports
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from profiler_agent.observability import setup_logging, metrics, tracer, log_agent_event
from profiler_agent.memory import MemoryBank
from profiler_agent.paths import get_input_path, get_output_path, list_input_files, ensure_directories
from google.genai import types as genai_types


async def demo_basic_workflow():
    """Demonstrate basic agent workflow."""
    print("\n" + "="*80)
    print("DEMO 1: Basic Agent Workflow")
    print("="*80)
    
    # Ensure directories exist
    ensure_directories()
    
    # Setup logging with file output
    logger = setup_logging(level="INFO", structured=False, log_file="demo_run.log")
    
    # Initialize session service
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="professor_profiler",
        user_id="demo_user",
        session_id="demo_session_1"
    )
    
    # Initialize runner
    runner = Runner(
        agent=root_agent,
        app_name="professor_profiler",
        session_service=session_service
    )
    
    # Create sample PDF in input folder if doesn't exist
    sample_pdf = get_input_path("physics_2024.pdf")
    if not sample_pdf.exists():
        print(f"\n⚠️  Creating mock PDF at {sample_pdf}")
        with open(sample_pdf, "w") as f:
            f.write("Mock PDF content for testing")
    
    # Run agent with query (use just the filename, tool will look in input/)
    query = "Analyze the exam paper physics_2024.pdf and tell me what topics to focus on."
    print(f"\n📝 Query: {query}")
    print("\n🤖 Agent Response:")
    print("-" * 80)
    
    log_agent_event(logger, "query_start", "professor_profiler_agent", query=query)
    
    async for event in runner.run_async(
        user_id="demo_user",
        session_id="demo_session_1",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        )
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            print(f"\n{response_text}")
            log_agent_event(logger, "query_complete", "professor_profiler_agent")
    
    # Show session stats
    stats = session_service.get_stats()
    print(f"\n📊 Session Stats: {json.dumps(stats, indent=2)}")


async def demo_memory_bank():
    """Demonstrate memory bank functionality."""
    print("\n" + "="*80)
    print("DEMO 2: Memory Bank & Long-term Context")
    print("="*80)
    
    # Memory bank will automatically save to output/memory_bank.json
    memory_bank = MemoryBank()
    user_id = "demo_user"
    
    # Add memories
    print("\n💾 Adding memories to memory bank...")
    
    memory_bank.add_memory(
        user_id=user_id,
        memory_type="exam_analysis",
        content={
            "exam_name": "Physics 2024 Midterm",
            "topics": ["Electromagnetism", "Quantum Mechanics", "Thermodynamics"],
            "difficulty": "high",
            "trends": "Increased focus on quantum topics"
        },
        tags=["physics", "2024", "midterm"]
    )
    
    memory_bank.add_memory(
        user_id=user_id,
        memory_type="study_plan",
        content={
            "plan_date": "2024-03-15",
            "priority_topics": ["Quantum Mechanics", "Electromagnetism"],
            "estimated_hours": 20,
            "strategy": "Focus on problem-solving and conceptual understanding"
        },
        tags=["physics", "study_plan"]
    )
    
    memory_bank.add_memory(
        user_id=user_id,
        memory_type="preference",
        content={
            "learning_style": "visual",
            "preferred_resources": ["video lectures", "diagrams"],
            "study_time": "evening"
        },
        tags=["preferences", "learning_style"]
    )
    
    # Retrieve memories
    print("\n📚 Retrieving memories...")
    memories = memory_bank.get_memories(user_id, limit=10)
    for mem in memories:
        print(f"  - [{mem['type']}] {json.dumps(mem['content'], indent=2)}")
    
    # Search memories
    print("\n🔍 Searching for 'quantum'...")
    results = memory_bank.search_memories(user_id, "quantum")
    for result in results:
        print(f"  - Found: {result['type']} - {result['content']}")
    
    # Get summary
    summary = memory_bank.get_summary(user_id)
    print(f"\n📋 Memory Summary: {json.dumps(summary, indent=2)}")
    
    # Compact context for LLM
    context = memory_bank.compact_context(user_id, max_tokens=500)
    print(f"\n📄 Compacted Context (for LLM):\n{context}")
    
    # Cleanup
    os.remove("demo_memory.json")


async def demo_observability():
    """Demonstrate observability features."""
    print("\n" + "="*80)
    print("DEMO 3: Observability (Logging, Tracing, Metrics)")
    print("="*80)
    
    # Setup structured logging
    logger = setup_logging(level="INFO", structured=True)
    
    # Start trace
    print("\n🔍 Starting trace for agent operation...")
    trace_id = tracer.start_trace("demo_agent_execution", metadata={"user": "demo"})
    
    # Simulate agent operations
    import time
    
    print("  ⏱️  Simulating PDF ingestion...")
    time.sleep(0.1)
    tracer.add_span(trace_id, "pdf_ingestion", 100.5, {"file": "sample.pdf"})
    metrics.increment("pdf.ingested")
    metrics.histogram("pdf.pages", 12)
    
    print("  ⏱️  Simulating question classification...")
    time.sleep(0.15)
    tracer.add_span(trace_id, "question_classification", 150.2, {"count": 25})
    metrics.increment("questions.classified", 25)
    metrics.histogram("classification.duration_ms", 150.2)
    
    print("  ⏱️  Simulating trend analysis...")
    time.sleep(0.2)
    tracer.add_span(trace_id, "trend_analysis", 200.7, {"trends_found": 3})
    metrics.increment("trends.analyzed")
    metrics.histogram("analysis.duration_ms", 200.7)
    
    # End trace
    trace_data = tracer.end_trace(trace_id)
    print(f"\n📊 Trace Data:\n{json.dumps(trace_data, indent=2)}")
    
    # Get metrics
    metrics_data = metrics.get_metrics()
    print(f"\n📈 Metrics:\n{json.dumps(metrics_data, indent=2)}")
    
    # Reset for clean slate
    metrics.reset()


async def demo_tools():
    """Demonstrate custom tools."""
    print("\n" + "="*80)
    print("DEMO 4: Custom Tools (PDF, Statistics, Visualization)")
    print("="*80)
    
    from profiler_agent.tools import (
        read_pdf_content,
        analyze_statistics,
        visualize_trends,
        list_available_exams
    )
    
    # List available exams
    print(f"\n📂 Listing available exams in input/ folder...")
    available = list_available_exams()
    if available.get("count", 0) > 0:
        print(f"  ✅ Found {available['count']} exam(s):")
        for filename in available.get("files", []):
            print(f"     - {filename}")
    else:
        print(f"  ⚠️  No exams found in input/ folder")
    
    # Create mock PDF in input folder
    test_pdf = get_input_path("demo_exam.pdf")
    if not test_pdf.exists():
        print(f"\n📄 Creating mock PDF at {test_pdf}...")
        with open(test_pdf, "w") as f:
            f.write("Mock exam content")
    
    print(f"\n📄 Testing read_pdf_content tool...")
    result = read_pdf_content("demo_exam.pdf")  # Just use filename
    print(f"  ✅ Extracted content from: {result.get('filename', 'unknown')}")
    
    # Test statistics tool
    print(f"\n📊 Testing analyze_statistics tool...")
    mock_questions = {
        "questions": [
            {"topic": "Quantum Mechanics", "bloom_level": "Analyze"},
            {"topic": "Quantum Mechanics", "bloom_level": "Apply"},
            {"topic": "Electromagnetism", "bloom_level": "Understand"},
            {"topic": "Thermodynamics", "bloom_level": "Remember"},
            {"topic": "Quantum Mechanics", "bloom_level": "Analyze"},
        ]
    }
    
    stats = analyze_statistics(json.dumps(mock_questions))
    print(f"  ✅ Statistics:\n{json.dumps(stats, indent=4)}")
    
    # Test visualization tool (output will go to output/charts/)
    print(f"\n📈 Testing visualize_trends tool...")
    chart_path = "demo_chart.png"  # Will be saved to output/charts/
    viz_result = visualize_trends(json.dumps(stats), chart_path)
    
    if viz_result.get("success"):
        print(f"  ✅ Chart created: {viz_result['chart_path']}")
    else:
        print(f"  ⚠️  {viz_result.get('error', 'Unknown error')}")


async def demo_multi_agent():
    """Demonstrate multi-agent system."""
    print("\n" + "="*80)
    print("DEMO 5: Multi-Agent System (Hub-and-Spoke)")
    print("="*80)
    
    from profiler_agent.sub_agents import taxonomist, trend_spotter, strategist
    
    print(f"\n🤖 Root Agent: {root_agent.name}")
    print(f"   Model: {root_agent.model}")
    print(f"   Description: {root_agent.description}")
    print(f"   Tools: {[tool.name for tool in root_agent.tools]}")
    print(f"   Sub-agents: {[agent.name for agent in root_agent.sub_agents]}")
    
    print(f"\n🔹 Sub-agent 1: {taxonomist.name}")
    print(f"   Model: {taxonomist.model}")
    print(f"   Role: {taxonomist.description}")
    print(f"   Output Key: {taxonomist.output_key}")
    
    print(f"\n🔹 Sub-agent 2: {trend_spotter.name}")
    print(f"   Model: {trend_spotter.model}")
    print(f"   Role: {trend_spotter.description}")
    print(f"   Output Key: {trend_spotter.output_key}")
    
    print(f"\n🔹 Sub-agent 3: {strategist.name}")
    print(f"   Model: {strategist.model}")
    print(f"   Role: {strategist.description}")
    print(f"   Output Key: {strategist.output_key}")
    
    print(f"\n📊 Architecture Pattern: Hub-and-Spoke (Sequential Execution)")
    print(f"   Flow: Root → Taxonomist → Trend Spotter → Strategist")


async def main():
    """Run all demos."""
    print("\n" + "="*80)
    print("🎓 PROFESSOR PROFILER - MULTI-AGENT SYSTEM DEMO")
    print("="*80)
    print("\nThis demo showcases:")
    print("  ✅ Multi-agent system (Hub-and-Spoke with 3 sub-agents)")
    print("  ✅ Custom tools (PDF reading, statistics, visualization)")
    print("  ✅ Sessions & Memory (InMemorySessionService + MemoryBank)")
    print("  ✅ Observability (Logging, Tracing, Metrics)")
    print("  ✅ Gemini API integration (if API key provided)")
    
    # Show folder structure
    print("\n📁 Project Structure:")
    print("  📂 input/  - Place your exam PDFs here")
    print("  📂 output/ - All results saved here")
    print("     ├── charts/  - Visualization charts")
    print("     ├── logs/    - Log files")
    print("     └── reports/ - Analysis reports")
    
    # Ensure directories exist
    ensure_directories()
    
    # Check for input files
    input_files = list_input_files()
    print(f"\n📄 Found {len(input_files)} PDF file(s) in input/ folder")
    if input_files:
        for f in input_files[:3]:  # Show first 3
            print(f"   - {f.name}")
        if len(input_files) > 3:
            print(f"   ... and {len(input_files) - 3} more")
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: GOOGLE_API_KEY not set. Agent will use mock responses.")
        print("   To use real Gemini API, set: export GOOGLE_API_KEY=your_key")
    else:
        print(f"\n✅ GOOGLE_API_KEY found (length: {len(api_key)})")
    
    try:
        # Run demos
        await demo_multi_agent()
        await demo_tools()
        await demo_observability()
        await demo_memory_bank()
        await demo_basic_workflow()
        
        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"\n📊 Check the output/ folder for:")
        print(f"   - Charts: output/charts/")
        print(f"   - Logs: output/logs/demo_run.log")
        print(f"   - Memory: output/memory_bank.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
