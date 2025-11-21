# Quick Start Guide 🚀

Get started with Professor Profiler in 3 simple steps!

## Step 1: Add Your Exam PDFs

### Option A: Use Sample PDFs (Recommended for testing)

```bash
# Generate sample exam PDFs automatically
python create_sample_exams.py
```

This creates 3 sample exams in the `input/` folder:
- `physics_2024_midterm.pdf` - 10 physics questions
- `physics_2023_final.pdf` - 10 thermodynamics questions  
- `chemistry_2024_q1.pdf` - 10 chemistry questions

### Option B: Use Your Own PDFs

```bash
# Copy your exam papers to the input folder
cp your_exam.pdf input/
```

Or drag and drop PDF files into the `input/` folder.

## Step 2: Run Analysis

```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Set your Google API key
export GOOGLE_API_KEY="your-api-key-here"

# Run the demo
python demo.py
```

## Step 3: View Results

Results are automatically saved to the `output/` folder:

```bash
# View generated charts
ls output/charts/

# Read analysis logs
cat output/logs/demo_run.log

# Check memory bank
cat output/memory_bank.json
```

## Folder Structure

```
Professor_Profiler/
├── input/              # 📥 Place your exam PDFs here
│   ├── README.md
│   └── [your_exam.pdf]
│
├── output/             # 📤 All results saved here
│   ├── charts/         # 📊 Visualizations
│   ├── logs/           # 📝 Execution logs
│   ├── reports/        # 📄 Analysis reports
│   └── memory_bank.json # 🧠 Historical data
│
├── profiler_agent/     # Core agent code
├── google/adk/         # Agent Development Kit
└── demo.py            # Run this!
```

## Environment Setup

### Option 1: Using .env file (Recommended)

```bash
# Create .env file
echo "GOOGLE_API_KEY=your-api-key-here" > .env

# Run demo (automatically loads .env)
python demo.py
```

### Option 2: Using environment variable

```bash
export GOOGLE_API_KEY="your-api-key-here"
python demo.py
```

### Option 3: Using config file

Edit `profiler_agent/config.py` and set your API key directly (not recommended for production).

## Example Queries

Once running, try these example queries:

```python
# Analyze a single exam
"Analyze physics_2024.pdf and identify key topics"

# Compare multiple exams
"Compare physics_2023.pdf and physics_2024.pdf to find trends"

# Get study recommendations
"What should I focus on for the next physics exam?"

# Bloom's taxonomy analysis
"Analyze the cognitive complexity of math_201.pdf"
```

## Troubleshooting

### "No such file or directory: input/*.pdf"
- Make sure you've placed at least one PDF file in the `input/` folder
- Check that the file has a `.pdf` extension

### "API key not found"
- Set `GOOGLE_API_KEY` environment variable
- Or create a `.env` file with your key

### "ModuleNotFoundError"
- Run `pip install -r requirements.txt`
- Make sure you're in the correct directory

### Import errors
- Ensure you're running from the project root directory
- Check that all `__init__.py` files are present

## Getting Help

- Read the full README: [README.md](README.md)
- Check architecture docs: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- View feature list: [docs/FEATURES.md](docs/FEATURES.md)
- Input folder help: [input/README.md](input/README.md)
- Output folder help: [output/README.md](output/README.md)

## Next Steps

1. **Customize Agents**: Edit files in `profiler_agent/sub_agents/`
2. **Add New Tools**: Extend `profiler_agent/tools.py`
3. **Configure Settings**: Modify `profiler_agent/config.py`
4. **Write Tests**: Add tests to `tests/` folder
5. **Deploy**: Package for production use

---

**Happy Analyzing!** 📚✨
