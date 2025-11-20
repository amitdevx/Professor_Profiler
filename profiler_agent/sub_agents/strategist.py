from google.adk.agents import Agent
from ..config import config

strategist = Agent(
    model=config.analyzer_model,
    name="strategist",
    description="Generates actionable study plans.",
    instruction="Based on the Trend Report, tell the student EXACTLY what to study. Create a Hit List, Safe Zone, and Drop List.",
    output_key="final_study_plan"
)
