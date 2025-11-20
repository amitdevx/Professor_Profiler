from google.adk.agents import Agent
from ..config import config
from ..agent_utils import suppress_output_callback

trend_spotter = Agent(
    model=config.analyzer_model,
    name="trend_spotter",
    description="Analyzes statistical shifts in exam data over time.",
    instruction="Analyze the tagged questions to find Frequency Shifts and Cognitive Shifts. Output a 'Shift Report'.",
    output_key="trend_report",
    after_agent_callback=suppress_output_callback
)
