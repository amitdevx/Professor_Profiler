# Professor Profiler

> **An advanced hierarchical multi-agent system that reverse-engineers exam papers using NVIDIA NIM and Google Gemini to decode topic weights and cognitive complexity, outputting optimized study recommendations.**

---

## Overview

Professor Profiler is a Hierarchical Multi-Agent System (HMAS) designed to mimic the cognitive process of an expert academic coach. By orchestrating specialized worker agents powered by NVIDIA NIM (with optional Google Gemini fallback), it ingests exam PDFs, classifies questions (using Bloom's Taxonomy), tracks statistical trends, and formulates high-impact study plans.

This project serves as a reference implementation for:
*   Hub-and-Spoke Agent Architecture
*   Hosted LLM Integration via NVIDIA NIM (OpenAI-compatible) and Google Gemini (fallback)
*   Long-term Memory Management (JSON-persisted memory banks)
*   Production-grade Observability (tracing, request count, and latency metrics)

---

## System Architecture

The system creates a directed acyclic graph (DAG) of agent execution, managed by a central orchestrator.

### High-Level Design
```mermaid
flowchart TD
    subgraph External_Layer [" External Layer"]
        User(["User / Client"])
        PDF_File["Exam PDF"]
    end

    subgraph Orchestration_Layer [" Orchestration Layer"]
        Runner["<b>Runner</b><br><i>State Management</i>"]
        Memory[("<b>Memory Bank</b><br><i>JSON Persistence</i>")]
        Session["<b>Session Service</b>"]
    end

    subgraph Agent_Layer [" Agent Hierarchy"]
        Root["<b>ROOT AGENT</b><br><i>Llama 3.3 70B (NIM)</i><br>The Orchestrator"]

        subgraph Workers ["Specialized Sub-Agents"]
            Taxonomist["<b>Taxonomist</b><br><i>Llama 3.1 70B (NIM)</i><br>Topic & Bloom's Classification"]
            Trend["<b>Trend Spotter</b><br><i>Llama 3.3 70B (NIM)</i><br>Statistical Analysis"]
            Strat["<b>Strategist</b><br><i>Llama 3.3 70B (NIM)</i><br>Study Planning"]
        end
    end

    subgraph Tool_Layer [" Tool Layer"]
        Reader["PDF Ingestion"]
        Plotter["Matplotlib Viz"]
        Calc["Stats Engine"]
    end

    User --> Runner
    PDF_File --> Reader
    Runner <--> Session
    Runner <--> Memory
    Runner --> Root

    Root --Delegates--> Taxonomist
    Root --Delegates--> Trend
    Root --Delegates--> Strat

    Root --Calls--> Reader
    Root --Calls--> Plotter
    Trend --Calls--> Calc
```
---

## Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Core Logic** | Python 3.10+ | Type-hinted, async-native codebase. |
| **LLM Provider** | NVIDIA NIM | OpenAI-compatible endpoint hosting high-performance open models. |
| **Fallback Engine** | Google Gemini | Rollback path when NIM fails or for comparison testing. |
| **Document Processing** | `pypdf` | Robust text extraction from exam PDFs. |
| **Visualization** | `matplotlib` | Generates distribution bar charts and pie charts. |
| **Observability** | Custom Logging | Structured logging with latency and success metrics. |
| **Configuration** | `python-dotenv` | Environment variable validation and typed configurations. |

---

## Agent Personas

The system splits the cognitive load across three distinct worker agents:

### 1. The Taxonomist (Classifier)
*   **Model:** `meta/llama-3.1-70b-instruct` (NIM) | `gemini-2.0-flash-exp` (Gemini)
*   **Role:** The meticulous grader. It reads every question and tags it with a topic and Bloom's Taxonomy Level (Remember, Understand, Apply, Analyze, Evaluate, Create).

### 2. The Trend Spotter (Analyst)
*   **Model:** `meta/llama-3.3-70b-instruct` (NIM) | `gemini-2.0-pro-exp` (Gemini)
*   **Role:** The data scientist. It looks at the frequency and cognitive complexity distribution to isolate shifts and outliers.

### 3. The Strategist (Coach)
*   **Model:** `meta/llama-3.3-70b-instruct` (NIM) | `gemini-2.0-pro-exp` (Gemini)
*   **Role:** The academic coach. It aggregates findings into a study recommendation containing a Hit List, Safe Zone, and Drop List.

---

## Getting Started

For full instructions on setting up the core Python backend, configuring your API keys, and installing the optional interactive Node.js CLI, please see our dedicated [Installation Guide (INSTALL.md)](INSTALL.md).

---

## Usage

### 1. Interactive Execution (Recommended)
Place your exam PDF inside the `input/` folder, then run the startup runner:

#### Linux / macOS
```bash
python3 run.py
```

#### Windows
```powershell
python run.py
```

This script will:
- Check for existing PDFs in `input/`. If empty, it automatically generates three sample exams using `create_sample_exams.py`.
- Prompt you to select a PDF for analysis.
- Execute the orchestrator and all sub-agents sequentially.
- Save a structured Markdown study report to `output/reports/`.
- Print request metrics (total requests, average latency, and fallback counts).

### 2. Running the Benchmarks
To compare latency and execution between NVIDIA NIM and Google Gemini:

#### Linux / macOS
```bash
python3 scripts/benchmark_nim_vs_gemini.py
```

#### Windows
```powershell
python scripts/benchmark_nim_vs_gemini.py
```

### 3. Verification & Testing
To execute the automated test suites:

#### Linux / macOS
```bash
# Run unit and migration tests
pytest tests/test_nim_migration.py

# Run integration tests
pytest tests/test_nim_full_integration.py

# Run agent routing tests
pytest tests/test_agent.py
```

#### Windows
```powershell
# Run unit and migration tests
pytest tests/test_nim_migration.py

# Run integration tests
pytest tests/test_nim_full_integration.py

# Run agent routing tests
pytest tests/test_agent.py
```

---

## Project Structure

```text
Professor_Profiler/
├── input/                      # Exam PDF inputs
├── output/                     # Generated artifacts
│   ├── charts/                 # Visualizations (.png)
│   ├── logs/                   # Execution log files
│   └── reports/                # Markdown study recommendations
├── google/adk/                 # Custom Agent Development Kit (ADK)
│   ├── agents/                 # Base Agent & tool execution
│   ├── clients/                # NIM Client wrapping AsyncOpenAI
│   └── runners/                # Orchestrator Runner
├── profiler_agent/             # App-specific agents and configurations
│   ├── sub_agents/             # Taxonomist, Trend Spotter, Strategist
│   ├── tools.py                # Ingestion, Stats, and Viz tools
│   └── config.py               # Provider settings
├── run.py                      # Interactive startup runner
├── demo.py                     # Feature demo runner
└── tests/                      # Automated test suite
```

---

## Troubleshootings

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| KeyError / 404 Not Found | Model not active on tier | Switch NIM models in `.env` to meta family (e.g. `meta/llama-3.1-70b-instruct`). |
| TypeError: ARC4 | Warning message | Cryptography warning from pypdf. Safe to ignore or update cryptography package. |
| asyncio.TimeoutError | Slow hosted API endpoint | Increase `NIM_TIMEOUT` inside `.env` to `120` or higher. |
| 401 Unauthorized | Invalid key | Verify `NIM_API_KEY` or `GOOGLE_API_KEY` is loaded correctly in `.env`. |

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more details.

**Maintained by [amitdevx](https://github.com/amitdevx)**  
Website: [amitdevx](https://amitdevx.tech)
