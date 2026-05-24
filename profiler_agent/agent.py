import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .config import config
from .sub_agents import taxonomist, trend_spotter, strategist
from .tools import read_pdf_content, analyze_statistics, visualize_trends, compare_exams

professor_profiler_agent = Agent(
    name="professor_profiler_agent",
    model=config.analyzer_model,
    gemini_model=config.gemini_analyzer_model,
    nim_model=config.nim_analyzer_model,
    description="Main orchestrator. Ingests PDFs, classifies questions, finds trends, and creates study plans.",
    instruction=f"""Workflow:
1. If you need to read an external PDF and the text is not already provided, use read_pdf_content to ingest it. If the file's content is already provided inline in the prompt, DO NOT use read_pdf_content.
2. Delegate to taxonomist sub-agent to classify questions by topic and Bloom's taxonomy
3. Use analyze_statistics tool to compute frequency distributions
4. Delegate to trend_spotter sub-agent to identify statistical shifts
5. Use visualize_trends tool to create charts
6. Delegate to strategist sub-agent to generate study recommendations

Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}

You have access to these tools:
- read_pdf_content: Extract text from PDF files
- analyze_statistics: Compute statistical patterns
- visualize_trends: Generate charts
- compare_exams: Compare multiple exam papers

Your sub-agents are:
- taxonomist: Classifies questions (fast model)
- trend_spotter: Analyzes trends (detailed analysis)
- strategist: Generates study plans (actionable recommendations)""",
    sub_agents=[taxonomist, trend_spotter, strategist],
    tools=[
        FunctionTool(func=read_pdf_content),
        FunctionTool(func=analyze_statistics),
        FunctionTool(func=visualize_trends),
        FunctionTool(func=compare_exams)
    ],
)

root_agent = professor_profiler_agent
