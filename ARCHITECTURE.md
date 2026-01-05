# Professor Profiler - Multi-Agent Architecture

## Overview
A production-ready multi-agent system using Google Gemini API for analyzing exam papers and generating study recommendations.

## Key Features Implemented

### 1. Multi-Agent System ✓
- **Hub-and-Spoke Architecture**: Main orchestrator + 3 specialist sub-agents
  - **professor_profiler_agent** (Root): Orchestrates workflow
  - **taxonomist**: Classifies questions by topic and Bloom's taxonomy (Sequential)
  - **trend_spotter**: Analyzes statistical shifts in exam patterns (Sequential)
  - **strategist**: Generates actionable study plans (Sequential)
- **Parallel Processing**: Batch question classification
- **Sequential Workflow**: Orchestrated multi-step analysis pipeline

### 2. Tools ✓
- **Custom Tools**:
  - `read_pdf_content`: Extract text from PDF exam papers
  - `visualize_trends`: Generate matplotlib charts for trend analysis
  - `analyze_statistics`: Compute frequency distributions
- **Built-in Tools**: Code Execution for data analysis
- **MCP Integration**: Extensible tool framework for future integrations

### 3. Sessions & Memory ✓
- **InMemorySessionService**: State management across conversations
- **Memory Bank**: Long-term storage of:
  - Historical exam patterns
  - Student preferences
  - Previously analyzed papers
- **Context Compaction**: Smart summarization to manage token limits

### 4. Observability ✓
- **Structured Logging**: JSON logs with correlation IDs
- **Tracing**: Request flow tracking through agent hierarchy
- **Metrics**: Performance counters for agent execution time, tool usage, token consumption

### 5. Long-Running Operations ✓
- **Pause/Resume**: Support for multi-document batch processing
- **Checkpoint System**: Save intermediate results

## Architecture Flow

```
User Query → Runner → Root Agent (professor_profiler_agent)
                          ↓
                    [1. Ingest PDF Tool]
                          ↓
                    [2. Taxonomist Sub-Agent]
                          ↓ (tagged questions)
                    [3. Trend Spotter Sub-Agent]
                          ↓ (trend report)
                    [4. Strategist Sub-Agent]
                          ↓ (study plan)
                    Final Response
```

## Technology Stack
- **LLM**: Google Gemini 3 (Flash for classification, Pro for analysis)
- **Framework**: Custom ADK (Agent Development Kit)
- **PDF Processing**: pypdf
- **Visualization**: matplotlib
- **Data Analysis**: pandas
- **State Management**: In-memory with persistence option
- **Observability**: Python logging + custom metrics

## Agent Specifications

### Root Agent: professor_profiler_agent
- **Model**: gemini-3-pro
- **Role**: Orchestrator
- **Tools**: read_pdf_content, visualize_trends, analyze_statistics
- **Sub-agents**: taxonomist, trend_spotter, strategist

### Sub-Agent: taxonomist
- **Model**: gemini-3-flash (cost-effective for classification)
- **Role**: Question classification
- **Output**: Tagged questions with topics and Bloom's levels
- **Callback**: Suppresses intermediate output

### Sub-Agent: trend_spotter
- **Model**: gemini-3-pro (complex analysis)
- **Role**: Statistical trend analysis
- **Output**: Shift report with frequency and cognitive trends
- **Callback**: Suppresses intermediate output

### Sub-Agent: strategist
- **Model**: gemini-3-pro
- **Role**: Study plan generation
- **Output**: Hit List, Safe Zone, Drop List recommendations

## Environment Variables
```bash
GOOGLE_API_KEY=
GOOGLE_CLOUD_PROJECT=your_project_id  # Optional
GOOGLE_CLOUD_LOCATION=global         # Optional
GOOGLE_GENAI_USE_VERTEXAI=False      # Use Gemini API directly
```

## Deployment
- **Local**: Python script with ADK runner
- **Web Interface**: `adk web` command (if ADK supports)
- **API Server**: FastAPI wrapper for REST endpoints
- **Cloud**: Cloud Run / Cloud Functions deployment ready
