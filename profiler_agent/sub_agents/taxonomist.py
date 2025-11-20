from google.adk.agents import Agent
from ..config import config
from ..agent_utils import suppress_output_callback

taxonomist = Agent(
    model=config.classifier_model,
    name="taxonomist",
    description="Classifies educational questions by topic and cognitive difficulty.",
    instruction="For every exam question provided, output tags for 'Topic' and 'Blooms Level' (Remember, Understand, Apply, Analyze). Do NOT answer the question.",
    output_key="tagged_questions",
    after_agent_callback=suppress_output_callback 
)
