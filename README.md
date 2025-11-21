# Professor Profiler 🎓

A production-ready **multi-agent system** powered by **Google Gemini API** that analyzes exam papers to identify trends, classify questions, and generate personalized study recommendations.

> **🚀 New to this project?** Start here: [**GETTING_STARTED.md**](GETTING_STARTED.md)  
> **⚡ Quick Start (5 min):** [**QUICKSTART.md**](QUICKSTART.md)

## 🌟 Key Features

This project demonstrates **8+ key AI agent concepts** required for advanced agent systems:

### ✅ 1. Multi-Agent System
- **Hub-and-Spoke Architecture**: Root orchestrator + 3 specialized sub-agents
- **Sequential Execution**: Taxonomist → Trend Spotter → Strategist workflow
- **Agent Delegation**: Root agent delegates specialized tasks to sub-agents
- **Parallel Processing**: Batch question classification (ready for parallel execution)

### ✅ 2. Custom Tools & MCP Integration
- **PDF Reading Tool**: Extract text from exam papers using pypdf
- **Statistics Analysis Tool**: Compute frequency distributions and cognitive complexity
- **Visualization Tool**: Generate charts using matplotlib
- **Comparison Tool**: Analyze multiple exams for trends
- **MCP-Ready**: Extensible tool framework using FunctionTool wrapper

### ✅ 3. Sessions & Memory Management
- **InMemorySessionService**: Persistent conversation state across interactions
- **Memory Bank**: Long-term storage for:
  - Historical exam analyses
  - Student preferences
  - Previous study plans
- **Context Compaction**: Smart summarization to manage token limits

### ✅ 4. Observability
- **Structured Logging**: JSON logs with correlation IDs
- **Distributed Tracing**: Request flow tracking through agent hierarchy
- **Metrics Collection**: Performance counters for:
  - Agent execution time
  - Tool usage
  - Token consumption
  - Success/error rates

### ✅ 5. Gemini API Integration
- **Real LLM Calls**: Full integration with Google Gemini 2.5
- **Tool Calling**: Native Gemini function calling support
- **Streaming Responses**: Async event-based execution
- **Model Selection**: Flash for classification, Pro for analysis

##  Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     USER QUERY                                 │
└──────────────────┬─────────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   Runner        │  ◄── Session Service (Memory)
         │  (Orchestrator) │
         └────────┬────────┘
                  │
                  ▼
    ┌─────────────────────────┐
    │ professor_profiler_agent │ ◄── Root Agent (Gemini 2.5 Pro)
    │ (Hub)                    │
    └───────┬──────────────────┘
            │
            ├─── Tools: read_pdf, analyze_stats, visualize, compare
            │
            ├─── Sub-Agent 1: taxonomist (Flash)
            │    └─── Classifies questions by topic & Bloom's level
            │
            ├─── Sub-Agent 2: trend_spotter (Pro)
            │    └─── Analyzes statistical shifts in exam patterns
            │
            └─── Sub-Agent 3: strategist (Pro)
                 └─── Generates actionable study plans
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google AI API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/uffamit/Professor_Profiler.git
cd Professor_Profiler

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your API key
export GOOGLE_API_KEY="your_gemini_api_key_here"
```

### 📁 Folder Structure

The project uses a clear input/output folder structure:

```
Professor_Profiler/
├── input/           # 📥 Place your exam PDF files here
├── output/          # 📤 All results are saved here
│   ├── charts/      #    └─ Visualization charts (PNG files)
│   ├── logs/        #    └─ Log files
│   └── reports/     #    └─ Analysis reports
├── profiler_agent/  # Agent source code
├── tests/           # Test files
└── demo.py          # Demo script
```

**Workflow:**
1. **Place exam PDFs** in the `input/` folder
2. **Run the agent** (demo.py or your own script)
3. **Find results** in the `output/` folder

### Running Your First Analysis

```bash
# Step 1: Add your exam PDF to input folder
cp your_exam.pdf input/

# Step 2: Run the demo
python demo.py

# Step 3: Check results in output folder
ls output/charts/     # View generated charts
cat output/logs/demo_run.log  # View execution logs
cat output/memory_bank.json   # View stored memories
```

### Running Tests

```bash
# Run integration tests
python tests/test_agent.py

# Or use pytest
pytest tests/
```

## 📋 Usage Examples

### Basic Usage (with input/output folders)

```python
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from profiler_agent.agent import root_agent
from profiler_agent.paths import list_input_files
from google.genai import types as genai_types

async def analyze_exam():
    # Initialize session service
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="professor_profiler",
        user_id="student_123",
        session_id="session_001"
    )
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name="professor_profiler",
        session_service=session_service
    )
    
    # List available exams in input/ folder
    exams = list_input_files()
    print(f"Found {len(exams)} exam(s): {[e.name for e in exams]}")
    
    # Run analysis (agent will look for PDF in input/ folder)
    query = "Analyze physics_2024.pdf and tell me what to study"
    
    async for event in runner.run_async(
        user_id="student_123",
        session_id="session_001",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        )
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)
            # Results automatically saved to output/ folder

asyncio.run(analyze_exam())
```

### Using Memory Bank (saves to output/ folder)

```python
from profiler_agent.memory import MemoryBank

memory_bank = MemoryBank()

# Store exam analysis
memory_bank.add_memory(
    user_id="student_123",
    memory_type="exam_analysis",
    content={
        "exam": "Physics Midterm 2024",
        "topics": ["Quantum Mechanics", "Electromagnetism"],
        "difficulty": "high"
    },
    tags=["physics", "2024"]
)

# Retrieve memories
memories = memory_bank.get_memories("student_123", memory_type="exam_analysis")

# Search memories
results = memory_bank.search_memories("student_123", "quantum")

# Get compacted context for LLM
context = memory_bank.compact_context("student_123", max_tokens=500)
```

### Using Observability

```python
from profiler_agent.observability import setup_logging, metrics, tracer

# Setup structured logging
logger = setup_logging(level="INFO", structured=True)

# Start trace
trace_id = tracer.start_trace("exam_analysis", metadata={"user": "student_123"})

# Record metrics
metrics.increment("exams.analyzed")
metrics.histogram("processing.duration_ms", 1500.5)

# End trace
trace_data = tracer.end_trace(trace_id)

# Get all metrics
all_metrics = metrics.get_metrics()
```

## 🏗️ Project Structure

```
Professor_Profiler/
├── google/adk/                  # Custom ADK framework
│   ├── agents/
│   │   ├── agent.py            # Agent implementation with Gemini integration
│   │   └── callback_context.py # Callback context for post-processing
│   ├── runners/
│   │   └── runner.py           # Agent execution runner
│   ├── sessions/
│   │   └── in_memory_session_service.py  # Session state management
│   └── tools/
│       └── function_tool.py    # Function tool wrapper
│
├── profiler_agent/             # Main agent application
│   ├── agent.py               # Root agent definition
│   ├── config.py              # Configuration management
│   ├── tools.py               # Custom tools (PDF, stats, viz)
│   ├── memory.py              # Memory bank implementation
│   ├── observability.py       # Logging, tracing, metrics
│   ├── agent_utils.py         # Utility functions
│   └── sub_agents/            # Specialized sub-agents
│       ├── taxonomist.py      # Question classification
│       ├── trend_spotter.py   # Trend analysis
│       └── strategist.py      # Study plan generation
│
├── tests/
│   ├── test_agent.py          # Integration tests
│   └── sample_data/           # Test data
│
├── demo.py                    # Comprehensive demo script
├── requirements.txt           # Python dependencies
├── ARCHITECTURE.md            # Detailed architecture documentation
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

```bash
# Required: Google AI API Key
export GOOGLE_API_KEY="your_api_key"

# Optional: For Vertex AI
export GOOGLE_CLOUD_PROJECT="your_project_id"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_VERTEXAI="False"  # Set to "True" for Vertex AI
```

### Model Configuration

Edit `profiler_agent/config.py` to customize models:

```python
@dataclass
class ProfilerConfiguration:
    classifier_model: str = "gemini-2.0-flash-exp"  # Fast for classification
    analyzer_model: str = "gemini-2.0-flash-thinking-exp-01-21"      # Detailed for analysis
```

## 📊 Agent Capabilities

### Taxonomist (Sub-Agent 1)
- **Purpose**: Classify questions by topic and cognitive level
- **Model**: gemini-2.0-flash-exp (optimized for speed)
- **Output**: Tagged questions with topics and Bloom's taxonomy levels
- **Bloom's Levels**: Remember, Understand, Apply, Analyze, Evaluate, Create

### Trend Spotter (Sub-Agent 2)
- **Purpose**: Identify statistical patterns across exams
- **Model**: gemini-2.0-flash-thinking-exp-01-21 (deep analysis)
- **Output**: Shift report showing:
  - Frequency shifts (topics appearing more/less)
  - Cognitive shifts (difficulty level changes)
  - Emerging patterns

### Strategist (Sub-Agent 3)
- **Purpose**: Generate actionable study recommendations
- **Model**: gemini-2.0-flash-thinking-exp-01-21
- **Output**: Study plan with:
  - **Hit List**: High-priority topics
  - **Safe Zone**: Well-covered topics  
  - **Drop List**: Low-value topics to skip

## 🧪 Testing

### Run All Tests

```bash
python tests/test_agent.py
```

### Run Demo

```bash
python demo.py
```

The demo showcases:
1. Multi-agent system architecture
2. Custom tools execution
3. Observability features
4. Memory bank operations
5. Full agent workflow with mock or real API

## 📈 Performance & Observability

### Metrics Tracked

- `exams.analyzed`: Counter of analyzed exams
- `questions.classified`: Number of classified questions
- `trends.identified`: Trends found per analysis
- `agent.execution.duration_ms`: Agent execution time
- `tool.invocation.count`: Tool usage statistics

### Logging Levels

- **INFO**: General operations (session creation, agent execution)
- **DEBUG**: Detailed execution flow (message additions, context updates)
- **WARNING**: Non-critical issues (missing API key, fallback behavior)
- **ERROR**: Failures (API errors, tool failures)

### Trace Data Structure

```json
{
  "trace_id": "uuid-here",
  "operation": "exam_analysis",
  "total_duration_ms": 1543.2,
  "spans": [
    {"name": "pdf_ingestion", "duration_ms": 120.5},
    {"name": "classification", "duration_ms": 450.2},
    {"name": "trend_analysis", "duration_ms": 680.1},
    {"name": "strategy_generation", "duration_ms": 292.4}
  ]
}
```

## 🛠️ Extending the System

### Adding a New Tool

```python
from google.adk.tools import FunctionTool

def my_custom_tool(param: str) -> dict:
    """
    Description of what the tool does.
    
    Args:
        param: Parameter description
    
    Returns:
        Dictionary with results
    """
    return {"result": "processed"}

# Add to agent
root_agent.tools.append(FunctionTool(func=my_custom_tool))
```

### Adding a New Sub-Agent

```python
from google.adk.agents import Agent
from profiler_agent.config import config

new_agent = Agent(
    name="my_agent",
    model=config.analyzer_model,
    description="What this agent does",
    instruction="Detailed instructions for the agent",
    output_key="agent_output"
)

# Add to root agent
root_agent.sub_agents.append(new_agent)
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📚 Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/)
- [Agent Development Kit (ADK) Concepts](./ARCHITECTURE.md)
- [Bloom's Taxonomy Reference](https://cft.vanderbilt.edu/guides-sub-pages/blooms-taxonomy/)

## 🎯 Roadmap

- [ ] Add evaluation metrics for agent performance
- [ ] Implement A2A (Agent-to-Agent) protocol
- [ ] Cloud deployment configurations (Cloud Run, Functions)
- [ ] Web interface with real-time updates
- [ ] Support for more document formats (DOCX, images)
- [ ] Vector database integration for semantic search
- [ ] Multi-language support

---

**Built with ❤️ using Google Gemini AI**