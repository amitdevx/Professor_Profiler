#!/usr/bin/env python3
"""
Professor Profiler - Interactive Startup and Execution Runner
"""
import asyncio
import os
import sys
import json
from pathlib import Path

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from dotenv import load_dotenv
load_dotenv(repo_root / ".env")

import warnings
warnings.filterwarnings("ignore")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from profiler_agent.observability import setup_logging, migration_metrics
from profiler_agent.paths import get_input_path, get_output_path, list_input_files, ensure_directories
from google.genai import types as genai_types


def check_dependencies():
    """Ensure required packages are available."""
    try:
        import openai
        import pypdf
        import matplotlib
        import reportlab
    except ImportError as e:
        print(f"Error: Missing dependency: {e.name}. Please run: pip install -r requirements.txt")
        sys.exit(1)


def generate_sample_exams_if_needed():
    """Automatically generate sample PDFs if input/ is empty."""
    input_files = list_input_files(".pdf")
    if not input_files:
        print("No exam PDFs found in the input directory.")
        print("Running create_sample_exams.py to generate mock exams...")
        try:
            from create_sample_exams import main as generate_main
            generate_main()
            input_files = list_input_files(".pdf")
        except Exception as e:
            print(f"Error: Failed to generate sample exams: {e}")
    return input_files


async def run_analysis(pdf_filename: str, agent_name: str = "all"):
    """Run the multi-agent profiling pipeline on the selected PDF."""
    print("\n" + "="*80)
    print(f"Initializing Analysis for: {pdf_filename}")
    if agent_name != "all":
        print(f"Targeting Agent: {agent_name}")
    print("="*80)

    ensure_directories()
    setup_logging(level="INFO", structured=False, log_file="agent_run.log")

    # Verify LLM provider configuration
    provider = os.getenv("LLM_PROVIDER", "nim").lower()
    api_key_var = "NIM_API_KEY" if provider == "nim" else "GOOGLE_API_KEY"
    api_key = os.getenv(api_key_var)

    if not api_key:
        raise ValueError(f"CRITICAL: {api_key_var} is not set in environment or .env file. Mock mode is disabled.")
    else:
        print(f"Using LLM Provider: {provider.upper()}")

    session_service = InMemorySessionService()
    session_id = f"session_{int(asyncio.get_event_loop().time())}"
    await session_service.create_session(
        app_name="professor_profiler",
        user_id="default_user",
        session_id=session_id
    )

    agent_to_run = root_agent
    if agent_name != "all":
        name_map = {
            "parser": "root",
            "research": "taxonomist",
            "analysis": "trend_spotter",
            "recommendation": "strategist",
            "taxonomist": "taxonomist",
            "trend_spotter": "trend_spotter",
            "recommend": "strategist",
            "strategist": "strategist",
        }
        target_name = name_map.get(agent_name.lower(), agent_name.lower())
        
        if target_name == "root":
            agent_to_run = root_agent
        else:
            found = False
            for sub in root_agent.sub_agents:
                if sub.name.lower() == target_name:
                    agent_to_run = sub
                    found = True
                    break
            if not found:
                print(f"Warning: agent '{agent_name}' not found. Defaulting to orchestrator.", flush=True)
    
    runner = Runner(
        agent=agent_to_run,
        app_name="professor_profiler",
        session_service=session_service,
        llm_provider=provider
    )

    if agent_name == "all":
        query = (
            f"Analyze the exam paper {pdf_filename}. Make sure to execute the entire workflow: "
            "1) read the PDF content, 2) classify all questions, 3) compute the topic and Bloom's level "
            "statistics, 4) generate and save a visualization chart, and 5) formulate the final study plan."
        )
    else:
        query = f"Please process the exam paper {pdf_filename} according to your specialization."
    
    print("\nExecuting Agent Pipeline (Root Orchestrator + Sub-agents)...")
    print("--------------------------------------------------------------------------------")

    final_response = None
    try:
        async for event in runner.run_async(
            user_id="default_user",
            session_id=session_id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=query)]
            )
        ):
            if not event.is_final_response():
                print(f"[{event.agent_name}] processing...", flush=True)
            else:
                final_response = event.content.parts[0].text

        if final_response:
            print("\n" + "="*80, flush=True)
            print("ANALYSIS REPORT GENERATED SUCCESSFULLY", flush=True)
            print("="*80, flush=True)
            print(final_response, flush=True)
            print("="*80, flush=True)
            
            report_name = f"{Path(pdf_filename).stem}_analysis_report.md"
            report_path = get_output_path(report_name, "reports")
            with open(report_path, "w") as f:
                f.write(final_response)
            
            print(f"\nSaved report to: {report_path}")
            
            import json
            import re
            
            trend_match = re.search(r'\[trend_spotter Response\](.*?)\[strategist Response\]', final_response, re.DOTALL)
            if trend_match:
                try:
                    trend_text = trend_match.group(1).strip()
                    json_start = trend_text.find('{')
                    json_end = trend_text.rfind('}')
                    if json_start != -1 and json_end != -1:
                        stats_json = trend_text[json_start:json_end+1]
                        stats = json.loads(stats_json)
                        if "total_questions" in stats:
                            from profiler_agent.tools import visualize_trends
                            visualize_trends(stats)
                except Exception as e:
                    print(f"Failed to generate chart from stats: {e}")

            chart_folder = get_output_path("", "charts")
            charts = list(chart_folder.glob("*.png"))
            if charts:
                print(f"Saved charts to: {chart_folder}")

            if provider == "nim":
                metrics = migration_metrics.snapshot()
                print("\nNIM Metrics Summary:")
                print(f"   - Total NIM Requests: {metrics['nim_requests']}")
                print(f"   - Average NIM Latency: {metrics['avg_latency_ms']:.2f} ms")
                print(f"   - Fallback to Gemini Triggered: {metrics['fallback_to_gemini']} times")

    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()


def main():
    check_dependencies()
    ensure_directories()
    
    print("\n" + "="*80)
    print("PROFESSOR PROFILER STARTUP RUNNER")
    print("="*80)
    print("This tool reverse-engineers exam papers to decode topic frequency and difficulty.")
    
    pdf_files = generate_sample_exams_if_needed()
    if not pdf_files:
        print("Error: No PDFs available. Please place a PDF in the input directory and restart.")
        sys.exit(1)

    print("\nAvailable Exam PDFs in the input directory:")
    for idx, f in enumerate(pdf_files, 1):
        print(f"  [{idx}] {f.name}")
    print(f"  [{len(pdf_files) + 1}] Enter custom filename / absolute path")

    try:
        choice = input(f"\nSelect a file to analyze (1-{len(pdf_files) + 1}) [default: 1]: ").strip()
        if not choice:
            selected_file = pdf_files[0].name
        else:
            choice_idx = int(choice)
            if choice_idx == len(pdf_files) + 1:
                selected_file = input("Enter filename (in input directory) or absolute path: ").strip()
            elif 1 <= choice_idx <= len(pdf_files):
                selected_file = pdf_files[choice_idx - 1].name
            else:
                print("Error: Invalid selection. Defaulting to first file.")
                selected_file = pdf_files[0].name
        
        asyncio.run(run_analysis(selected_file))

    except (KeyboardInterrupt, SystemExit):
        print("\nExiting Startup Runner.")
    except ValueError:
        print("Error: Invalid input. Exiting.")


if __name__ == "__main__":
    main()
