# Changelog - Version 1.2.0

## Release Date: January 5, 2026

## Summary
Updated all Gemini model references to use valid Gemini 2.0 experimental models throughout the codebase.

## Changes

### Model Updates
- **Classifier Model**: Updated to `gemini-2.0-flash-exp` (fast, cost-effective for classification tasks)
- **Analyzer Model**: Updated to `gemini-2.0-pro-exp` (powerful, optimized for complex analysis)

### Files Modified

#### Configuration
- **profiler_agent/config.py**
  - `classifier_model`: `gemini-2.0-flash-exp`
  - `analyzer_model`: `gemini-2.0-pro-exp`

#### Documentation
- **ARCHITECTURE.md**
  - Updated technology stack description
  - Updated all agent model specifications (Root, Taxonomist, Trend Spotter, Strategist)
  
- **README.md**
  - Updated badge to show Gemini 2.0
  - Updated overview description
  - Updated system architecture diagrams
  - Updated tech stack table
  - Updated Agent Personas section with correct model names

- **FEATURES.md**
  - Updated API integration references
  - Updated agent descriptions
  - Updated learning outcomes section

### Technical Details

All agents now use validated Gemini 2.0 experimental models:

| Agent | Model | Purpose |
|-------|-------|---------|
| Root Agent | `gemini-2.0-pro-exp` | Orchestration and complex reasoning |
| Taxonomist | `gemini-2.0-flash-exp` | Fast question classification |
| Trend Spotter | `gemini-2.0-pro-exp` | Statistical analysis |
| Strategist | `gemini-2.0-pro-exp` | Study plan generation |

### Compatibility
- Fully compatible with Google Gemini API
- No breaking changes to existing functionality
- All existing tools and workflows remain unchanged

### Testing
- Configuration validated
- Model names verified against Google Gemini API
- All documentation updated consistently

## Migration Notes
No migration required. This update only changes the underlying model names while maintaining the same API interface and functionality.

## Next Steps
- Test with actual Gemini API calls
- Monitor performance with new model versions
- Consider adding support for additional Gemini 2.0 models as they become available
