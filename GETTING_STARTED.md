# Getting Started with Professor Profiler 🚀

Welcome! This guide will help you navigate the documentation and get started quickly.

## 📖 Documentation Index

### For First-Time Users
1. **[QUICKSTART.md](QUICKSTART.md)** ⭐ START HERE
   - 3-step setup guide
   - Sample data generation
   - First analysis walkthrough
   - **Time to first result: ~5 minutes**

2. **[WORKFLOW.md](WORKFLOW.md)** 
   - Visual workflow diagrams
   - Step-by-step process
   - Tool usage examples
   - Troubleshooting guide

### For Developers
3. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - System design overview
   - Multi-agent architecture
   - Component relationships
   - Technology stack

4. **[FEATURES.md](FEATURES.md)**
   - Complete feature list (8+ key concepts)
   - Implementation details
   - Code examples
   - Extensibility points

5. **[FOLDER_IMPLEMENTATION.md](FOLDER_IMPLEMENTATION.md)**
   - Input/output folder structure
   - Path management utilities
   - Git integration
   - Migration guide

### Reference
6. **[README.md](README.md)** - Main project documentation
7. **[STATUS.md](STATUS.md)** - Current implementation status
8. **Folder-specific**:
   - [input/README.md](input/README.md) - Using the input folder
   - [output/README.md](output/README.md) - Understanding outputs

## 🎯 Quick Navigation

### "I want to..."

#### → Run a quick test
```bash
python create_sample_exams.py  # Generate sample PDFs
export GOOGLE_API_KEY="your-key"
python demo.py                 # Run analysis
```
📚 See: [QUICKSTART.md](QUICKSTART.md)

#### → Understand the system architecture
- Read: [ARCHITECTURE.md](ARCHITECTURE.md)
- Visual diagrams showing agent interactions
- Technology stack and design decisions

#### → See what features are available
- Read: [FEATURES.md](FEATURES.md)
- 8+ key AI agent concepts implemented
- Custom tools and integrations

#### → Know where files go
- Read: [FOLDER_IMPLEMENTATION.md](FOLDER_IMPLEMENTATION.md)
- `input/` - Place exam PDFs here
- `output/` - All results saved here

#### → Understand the workflow
- Read: [WORKFLOW.md](WORKFLOW.md)
- Visual process diagrams
- Data flow examples

#### → Customize or extend
- Start with: [FEATURES.md](FEATURES.md) - Extensibility section
- Then: `profiler_agent/` code files
- Add tools: `profiler_agent/tools.py`
- Add agents: `profiler_agent/sub_agents/`

## 📁 Project Structure

```
Professor_Profiler/
├── 📖 Documentation (Start here!)
│   ├── QUICKSTART.md              ⭐ NEW USERS START HERE
│   ├── WORKFLOW.md                Visual process guide
│   ├── ARCHITECTURE.md            System design
│   ├── FEATURES.md                What it can do
│   ├── FOLDER_IMPLEMENTATION.md   File organization
│   ├── STATUS.md                  Current state
│   └── README.md                  Main docs
│
├── 📥 Input (Place exam PDFs here)
│   ├── README.md                  Usage guide
│   └── [your_exam.pdf]
│
├── 📤 Output (Results saved here)
│   ├── README.md                  Understanding outputs
│   ├── charts/                    Visualizations
│   ├── logs/                      Execution logs
│   ├── reports/                   Analysis reports
│   └── memory_bank.json           Historical data
│
├── 🤖 Core Agent System
│   ├── profiler_agent/            Main agent code
│   │   ├── agent.py              Root agent
│   │   ├── tools.py              Custom tools
│   │   ├── memory.py             Memory management
│   │   ├── paths.py              Path utilities
│   │   └── sub_agents/           Specialized agents
│   │       ├── taxonomist.py    Question classifier
│   │       ├── trend_spotter.py Pattern analyzer
│   │       └── strategist.py    Study planner
│   │
│   └── google/adk/               Agent Development Kit
│       ├── agents/               Agent base classes
│       ├── tools/                Tool framework
│       ├── runners/              Execution engine
│       └── sessions/             State management
│
├── 🧪 Testing & Examples
│   ├── tests/                    Unit tests
│   ├── demo.py                   Main demo script
│   └── create_sample_exams.py   Sample data generator
│
└── ⚙️ Configuration
    ├── requirements.txt          Python dependencies
    ├── .gitignore               Git configuration
    └── profiler_agent/config.py Settings
```

## 🏃 Quick Start Paths

### Path 1: Fastest Start (5 minutes)
For: "I just want to see it work"

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate samples
python create_sample_exams.py

# 3. Set API key
export GOOGLE_API_KEY="your-key-here"

# 4. Run!
python demo.py
```

### Path 2: Understanding First (15 minutes)
For: "I want to know how it works first"

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) (5 min)
2. Read [WORKFLOW.md](WORKFLOW.md) (5 min)
3. Browse code in `profiler_agent/` (5 min)
4. Run demo following [QUICKSTART.md](QUICKSTART.md)

### Path 3: Deep Dive (30 minutes)
For: "I want to customize this"

1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Read [FEATURES.md](FEATURES.md)
3. Study code in `profiler_agent/` and `google/adk/`
4. Read [FOLDER_IMPLEMENTATION.md](FOLDER_IMPLEMENTATION.md)
5. Run tests: `pytest tests/`
6. Modify and experiment

## 🎓 Learning Journey

```
1. QUICKSTART     → Get first results
   ↓
2. WORKFLOW       → Understand the process
   ↓
3. ARCHITECTURE   → Learn the design
   ↓
4. FEATURES       → Discover capabilities
   ↓
5. CODE           → Study implementation
   ↓
6. CUSTOMIZE      → Build your own
```

## 📊 Documentation Stats

- **Total docs**: 7 main files + 2 folder-specific
- **Total lines**: 1,567 lines
- **Coverage**: Setup, architecture, features, workflow, implementation
- **Time to productivity**: ~5 minutes (quickstart) to ~30 minutes (deep dive)

## 🆘 Common Questions

### "Where do I put my exam PDFs?"
→ `input/` folder - See [input/README.md](input/README.md)

### "Where are the results?"
→ `output/` folder - See [output/README.md](output/README.md)

### "How does it work?"
→ [WORKFLOW.md](WORKFLOW.md) for process, [ARCHITECTURE.md](ARCHITECTURE.md) for design

### "What can it do?"
→ [FEATURES.md](FEATURES.md) - Lists 8+ key features

### "How do I customize it?"
→ Edit files in `profiler_agent/` - Start with `tools.py` or `sub_agents/`

### "Something's broken, help!"
→ Check `output/logs/` → See [WORKFLOW.md](WORKFLOW.md) troubleshooting section

## 🔗 External Resources

- **Google Gemini API**: https://ai.google.dev/
- **Python Documentation**: https://docs.python.org/3/
- **VS Code**: https://code.visualstudio.com/docs

## 🚀 Next Steps

Choose your path:
- **Try it now**: Run [QUICKSTART.md](QUICKSTART.md) steps
- **Learn first**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
- **See the process**: Review [WORKFLOW.md](WORKFLOW.md)
- **Explore features**: Check [FEATURES.md](FEATURES.md)

---

**Need help?** Check the documentation files above or review code comments in `profiler_agent/`.

**Ready to start?** → Go to [QUICKSTART.md](QUICKSTART.md)
