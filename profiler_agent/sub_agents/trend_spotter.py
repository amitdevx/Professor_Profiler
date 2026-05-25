from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ..config import config
from ..agent_utils import suppress_output_callback
from ..tools import analyze_statistics, visualize_trends

def generate_chart_callback(callback_context) -> str:
    response = callback_context.response
    try:
        import json
        stats = json.loads(response)
        if isinstance(stats, dict) and "total_questions" in stats:
            # We got the statistics! Generate chart.
            visualize_trends(stats)
            return response
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Chart generation failed: {e}")
    return response

trend_spotter = Agent(
    model=config.analyzer_model,
    gemini_model=config.gemini_analyzer_model,
    nim_model=config.nim_analyzer_model,
    name="trend_spotter",
    description="Analyzes statistical shifts in exam data over time.",
    instruction="Analyze the tagged questions using the analyze_statistics tool to compute distributions. Output a 'Shift Report'.",
    output_key="trend_report",
    after_agent_callback=generate_chart_callback,
    tools=[FunctionTool(func=analyze_statistics), FunctionTool(func=visualize_trends)]
)
