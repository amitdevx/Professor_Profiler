# Installation Guide

Welcome to **Professor Profiler**! This guide will walk you through setting up the core Python backend, configuring your API keys, and installing the optional interactive Node.js CLI.

---

## 1. Prerequisites

Before starting, ensure you have the following installed on your system:
- **Python 3.10+**
- **Node.js 18+** (Required only for the interactive CLI)
- **Git**

You will also need an API key from at least one of these providers:
- **NVIDIA NIM API Key** (Primary - Get it from [build.nvidia.com](https://build.nvidia.com/))
- **Google Gemini API Key** (Fallback - Get it from [Google AI Studio](https://aistudio.google.com/))

---

## 2. Python Backend Setup (Core System)

The core orchestrator logic is built in Python.

### Step 2.1: Clone the Repository
```bash
git clone https://github.com/uffamit/Professor_Profiler.git
cd Professor_Profiler
```

### Step 2.2: Create a Virtual Environment
It is highly recommended to use a virtual environment to isolate dependencies.

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 2.3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 3. Configuration (.env)

The system requires environment variables to securely load your API keys and model configurations.

1. Create a copy of the example environment file:
   - **Linux/macOS:** `cp .env.example .env`
   - **Windows:** `copy .env.example .env`

2. Open the newly created `.env` file and insert your API keys:
```ini
# Provider Selection: nim or gemini
LLM_PROVIDER=nim

# NVIDIA NIM Configuration
NIM_API_KEY=your_nvidia_api_key_here
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_TIMEOUT=120
NIM_CLASSIFIER_MODEL=meta/llama-3.1-70b-instruct
NIM_ANALYZER_MODEL=meta/llama-3.3-70b-instruct

# Optional Fallback to Gemini
ENABLE_FALLBACK=true
GOOGLE_API_KEY=your_google_gemini_key_here
GEMINI_CLASSIFIER_MODEL=gemini-2.0-flash-exp
GEMINI_ANALYZER_MODEL=gemini-2.0-pro-exp
```
> [!IMPORTANT]
> The system strictly enforces the presence of your primary API key (`NIM_API_KEY`). Ensure this value is populated before running the analysis.

---

## 4. Install the Interactive CLI (Optional but Recommended)

The repository includes a sleek, interactive terminal interface written in TypeScript.

1. Navigate to the `cli/` directory:
   ```bash
   cd cli
   ```

2. Run the global installation script:
   ```bash
   ./install.sh
   ```
   *Note: This script runs `npm install`, `npm run build`, and `npm run install:global` to link the `prof` executable globally on your system.*

3. Verify the installation:
   ```bash
   prof --help
   ```

---

## 5. Verify Your Setup

To test if everything is working smoothly, you can run the built-in test suite:

```bash
# Return to the root directory
cd ..

# Ensure your virtual environment is active
source .venv/bin/activate  # (or .venv\Scripts\Activate.ps1 on Windows)

# Run the test suite
pytest tests/
```

If the tests pass, you are ready to start analyzing exam papers! Run `python run.py` directly, or use the `prof analyze` CLI command.
