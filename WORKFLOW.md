# Professor Profiler Workflow 🔄

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER WORKFLOW                                │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   USER       │
    │ Has Exam PDFs│
    └──────┬───────┘
           │
           ▼
    ┌─────────────────┐
    │  Step 1: INPUT  │     Place exam PDFs in input/ folder
    │                 │     (or run create_sample_exams.py)
    │   input/        │
    │   ├── physics_2024.pdf
    │   ├── physics_2023.pdf
    │   └── chemistry.pdf
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────────┐
    │  Step 2: PROCESS    │   Run: python demo.py
    │                     │   
    │  Professor Profiler │   ┌─────────────────────┐
    │  Multi-Agent System │   │ 1. Taxonomist       │
    │                     │──▶│    Classifies Qs    │
    │  - Read PDFs        │   │                     │
    │  - Analyze content  │   │ 2. Trend Spotter    │
    │  - Generate insights│◀──│    Finds patterns   │
    │  - Create charts    │   │                     │
    │  - Save results     │   │ 3. Strategist       │
    │                     │──▶│    Makes plan       │
    └─────────┬───────────┘   └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │  Step 3: OUTPUT     │   All results saved automatically
    │                     │
    │   output/           │
    │   ├── charts/       │   📊 Visualization charts
    │   │   └── trends.png
    │   ├── logs/         │   📝 Execution logs
    │   │   └── run.log
    │   ├── reports/      │   📄 Analysis reports (future)
    │   └── memory_bank.json  🧠 Historical data
    └─────────┬───────────┘
              │
              ▼
    ┌──────────────┐
    │   USER       │   View results, make decisions
    │ Reviews Data │   Adjust study plan
    └──────────────┘
```

## Detailed Steps

### Step 1: Input Setup 📥

**Option A: Use Samples (Recommended for first-time users)**
```bash
python create_sample_exams.py
```
This generates 3 realistic exam PDFs:
- `physics_2024_midterm.pdf` - 10 physics questions
- `physics_2023_final.pdf` - 10 thermodynamics questions
- `chemistry_2024_q1.pdf` - 10 chemistry questions

**Option B: Use Your Own PDFs**
```bash
cp your_exam.pdf input/
```

### Step 2: Run Analysis 🔍

```bash
# Set your Google API key
export GOOGLE_API_KEY="your-key-here"

# Run the analysis
python demo.py
```

**What Happens Inside:**

1. **Root Agent** orchestrates the workflow
2. **Taxonomist** classifies questions using Bloom's taxonomy
3. **Trend Spotter** identifies patterns across exams
4. **Strategist** generates study recommendations

### Step 3: Review Results 📊

**Charts** (`output/charts/`)
```bash
# View generated charts
ls output/charts/
open output/charts/trends_chart.png  # Mac
xdg-open output/charts/trends_chart.png  # Linux
```

**Logs** (`output/logs/`)
```bash
# Check execution logs
cat output/logs/demo_run.log

# Follow live logs
tail -f output/logs/demo_run.log
```

**Memory Bank** (`output/memory_bank.json`)
```bash
# View historical data
cat output/memory_bank.json | jq .

# Search for specific exam
jq '.[] | select(.exam_name | contains("physics"))' output/memory_bank.json
```

## Data Flow Diagram

```
INPUT → PROCESSING → OUTPUT
  │         │          │
  │         │          ├─→ Charts (PNG)
  │         │          ├─→ Logs (TXT)
  │         │          ├─→ Reports (MD/JSON)
  │         │          └─→ Memory (JSON)
  │         │
  │         ├─→ Root Agent
  │         │    │
  │         │    ├─→ Taxonomist (Classify)
  │         │    ├─→ Trend Spotter (Analyze)
  │         │    └─→ Strategist (Recommend)
  │         │
  │         └─→ Tools
  │              ├─→ PDF Reader
  │              ├─→ Statistics
  │              ├─→ Visualizer
  │              └─→ Comparator
  │
  └─→ Exam PDFs (input/)
```

## Multi-Agent Execution Flow

```
┌────────────────────────────────────────────────────────────┐
│                    ROOT AGENT                              │
│  "Analyze physics_2024.pdf and identify key topics"       │
└─────────────────┬──────────────────────────────────────────┘
                  │
                  ├─→ [DELEGATE] Taxonomist
                  │   ├─ Read PDF: physics_2024.pdf
                  │   ├─ Extract questions
                  │   ├─ Classify by Bloom's level
                  │   └─ Return: {questions: [...], taxonomy: {...}}
                  │
                  ├─→ [DELEGATE] Trend Spotter
                  │   ├─ Receive: Taxonomist output
                  │   ├─ Compare with history (memory_bank.json)
                  │   ├─ Identify patterns
                  │   ├─ Generate statistics
                  │   └─ Return: {trends: [...], stats: {...}}
                  │
                  ├─→ [DELEGATE] Strategist
                  │   ├─ Receive: Trend Spotter output
                  │   ├─ Analyze cognitive levels
                  │   ├─ Generate recommendations
                  │   ├─ Create hit/safe/drop lists
                  │   └─ Return: {strategy: {...}, recommendations: [...]}
                  │
                  └─→ [SYNTHESIZE] Final Response
                      ├─ Save to memory_bank.json
                      ├─ Generate charts (output/charts/)
                      ├─ Write logs (output/logs/)
                      └─ Return comprehensive analysis
```

## Tool Usage Examples

### Reading PDFs
```python
from profiler_agent.tools import read_pdf_content
from profiler_agent.paths import get_input_path

# Automatically finds PDF in input/ folder
pdf_path = get_input_path("physics_2024.pdf")
content = read_pdf_content(pdf_path)
```

### Generating Charts
```python
from profiler_agent.tools import visualize_trends
from profiler_agent.paths import get_output_path

# Automatically saves to output/charts/
chart_path = get_output_path("trends.png", "charts")
visualize_trends(data, output_path=chart_path)
```

### Accessing Memory
```python
from profiler_agent.memory import MemoryBank
from profiler_agent.paths import get_output_path

# Automatically uses output/memory_bank.json
memory = MemoryBank(get_output_path("memory_bank.json"))
history = memory.search("physics")
```

## Integration Points

### Environment Variables
```bash
# Required
export GOOGLE_API_KEY="your-api-key-here"

# Optional
export PROFILER_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
export PROFILER_INPUT_DIR="/custom/path/input"
export PROFILER_OUTPUT_DIR="/custom/path/output"
```

### Configuration
See `profiler_agent/config.py` for all settings:
- API keys
- Model selection (Flash vs Pro)
- Temperature settings
- Token limits
- Timeout values

### Custom Paths
```python
from profiler_agent.paths import get_input_path, get_output_path

# Override defaults
input_path = get_input_path("exam.pdf", base_dir="/custom/input")
output_path = get_output_path("result.json", base_dir="/custom/output")
```

## Troubleshooting Workflow

```
Problem? → Check Logs → Review Code → Fix → Test
    │          │            │          │       │
    │          │            │          │       └─→ Verify output/
    │          │            │          │
    │          │            │          └─→ Re-run demo.py
    │          │            │
    │          │            └─→ Update profiler_agent/
    │          │
    │          └─→ cat output/logs/demo_run.log
    │
    └─→ Common Issues:
        ├─ PDF not found → Check input/ folder
        ├─ API error → Verify GOOGLE_API_KEY
        ├─ Import error → pip install -r requirements.txt
        └─ Permission denied → Check file permissions
```

## Performance Tips

1. **Batch Processing**: Place multiple PDFs in `input/` for comparison
2. **Caching**: Results cached in `memory_bank.json` - reuse when possible
3. **Model Selection**: Use Flash for classification, Pro for deep analysis
4. **Parallel Tools**: Enable parallel execution in config for faster processing
5. **Log Level**: Set to WARNING in production to reduce log volume

## Next Steps

After reviewing results:
1. **Refine Analysis**: Adjust settings in `profiler_agent/config.py`
2. **Add Custom Tools**: Extend `profiler_agent/tools.py`
3. **Create Reports**: Use data from `output/` to generate custom reports
4. **Integrate**: Use as API or library in your application
5. **Deploy**: Package for production use

---

**For more details, see:**
- [QUICKSTART.md](QUICKSTART.md) - Getting started in 3 steps
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [FEATURES.md](FEATURES.md) - Complete feature list
- [README.md](README.md) - Main documentation
