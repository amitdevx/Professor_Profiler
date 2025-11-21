# Output Folder

All analysis results, charts, logs, and reports are automatically saved here.

## Structure

```
output/
├── charts/          # Visualization charts (PNG files)
├── logs/            # Execution logs
├── reports/         # Analysis reports (future)
└── memory_bank.json # Long-term memory storage
```

## Output Files

### Charts (`output/charts/`)
- **Trend visualizations**: Bar charts, pie charts showing topic distributions
- **Bloom's taxonomy analysis**: Cognitive complexity charts
- **Comparison charts**: Multi-exam trend analysis
- Format: PNG files with high resolution (150 DPI)

### Logs (`output/logs/`)
- **Execution logs**: Detailed agent execution traces
- **Error logs**: Debugging information
- **Performance metrics**: Timing and resource usage
- Format: Plain text or JSON structured logs

### Memory Bank (`output/memory_bank.json`)
- **Historical analysis**: Previously analyzed exams
- **User preferences**: Learning styles, study preferences
- **Study plans**: Generated recommendations
- Format: JSON with searchable structure

### Reports (`output/reports/`)
- **Study recommendations**: Hit lists, safe zones, drop lists
- **Trend analysis**: Statistical patterns across exams
- **Topic summaries**: Aggregated insights
- Format: Markdown or JSON

## Finding Your Results

After running an analysis:

```bash
# View charts
ls output/charts/
open output/charts/trends_chart.png  # Mac
xdg-open output/charts/trends_chart.png  # Linux

# Read logs
cat output/logs/demo_run.log
tail -f output/logs/demo_run.log  # Follow live logs

# Check memory
cat output/memory_bank.json | jq .  # Pretty print with jq
```

## Cleanup

To clear all outputs:

```bash
# Remove all outputs (keeps directories)
rm -f output/charts/*.png
rm -f output/logs/*.log
rm -f output/memory_bank.json

# Or use the reset script (if available)
python scripts/reset_output.py
```

## .gitignore

By default, generated files in this folder are ignored by git (except README files), so you can safely commit the structure without committing results.
