import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .config import config
from .sub_agents import taxonomist, trend_spotter, strategist
from .tools import read_pdf_content

professor_profiler_agent = Agent(
    name="professor_profiler_agent",
    model=config.analyzer_model,
    description="Main orchestrator. Ingests PDFs, classifies questions, finds trends, and creates study plans.",
    instruction=f"Workflow: 1. Ingest PDF. 2. Classify via taxonomist. 3. Analyze via trend_spotter. 4. Recommend via strategist. Current date: {datetime.datetime.now()}",
    sub_agents=[taxonomist, trend_spotter, strategist],
    tools=[FunctionTool(func=read_pdf_content)],
)
root_agent = professor_profiler_agent
