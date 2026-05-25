from google.adk.agents import Agent
from ..config import config
from ..agent_utils import suppress_output_callback

taxonomist = Agent(
    model=config.classifier_model,
    gemini_model=config.gemini_classifier_model,
    nim_model=config.nim_classifier_model,
    name="taxonomist",
    description="Classifies educational questions by topic and cognitive difficulty.",
    instruction=(
        "For every exam question provided, output a JSON object with a 'questions' array. "
        "Each item should have 'topic' and 'bloom_level' (Remember, Understand, Apply, Analyze). "
        "Do NOT answer the question. You MUST output ONLY valid JSON."
    ),
    output_key="tagged_questions"
)
