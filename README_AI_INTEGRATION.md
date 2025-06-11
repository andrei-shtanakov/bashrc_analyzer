# AI Integration - Step 2 Complete

## Overview

The bashrc analyzer now supports AI-enhanced explanations using Claude (Anthropic) and ChatGPT (OpenAI) APIs. This implementation follows the requirements from CLAUDE.md Step 2.

## Features Added

### 1. AI Service Integration
- **Claude API**: Using `anthropic` library with Haiku model for cost-effective analysis
- **ChatGPT API**: Using `openai` library with GPT-3.5-turbo model
- **Graceful fallback**: Works without API keys, offering basic recommendations

### 2. Interactive User Experience
- **Provider Selection**: User chooses between Claude, ChatGPT, or no AI
- **Output Format Options**:
  1. Terminal report only
  2. Save annotated .bashrc file with AI comments
  3. Both terminal report and annotated file

### 3. Enhanced CLI
```bash
# Basic analysis (no AI)
python main.py --no-ai

# AI-enhanced analysis (interactive)
python main.py

# Analyze specific file
python main.py /path/to/.bashrc
```

### 4. Environment Variables
```bash
export ANTHROPIC_API_KEY="your-claude-key"
export OPENAI_API_KEY="your-openai-key"
```

## Example Output

### Basic Mode (--no-ai)
```
🔍 Analyzing: /home/user/labs/bashrc_analyzer/tests/files/bashrc1
============================================================
⚠️  Found 5 potential issue(s):

📍 Line 25: module load sbSetup
   Category: Module Load in bashrc
   Problem: .bashrc is executed for every new shell...
   💡 Recommendation: We found module load in your .bashrc...
```

### AI-Enhanced Mode
```
🔍 Analyzing: /home/user/labs/bashrc_analyzer/tests/files/bashrc1
🤖 AI Assistant: Claude
============================================================
⚠️  Found 5 potential issue(s):

📍 Line 25: module load sbSetup
   Category: Module Load in bashrc
   🤖 AI Explanation:
      Loading modules in .bashrc causes them to run every time you open a shell,
      even for non-interactive sessions like SSH commands or job scripts. This
      creates unnecessary overhead and can cause conflicts in automated environments.
      
      Move these commands to ~/.bash_profile instead: they'll run once at login
      but not interfere with scripts. For HPC clusters, consider loading modules
      only when needed in your job scripts.
```

## Implementation Details

### AI Service Architecture
- `AIService` class handles multiple LLM providers
- Structured prompts optimized for HPC cluster context
- Error handling for API failures
- Token limit management (300 tokens max per explanation)

### Prompt Engineering
The AI prompts are specifically crafted for:
- **Audience**: Scientists/researchers using HPC clusters
- **Tone**: Friendly, helpful, non-technical
- **Structure**: Clear explanation → consequences → fix example → HPC tips
- **Context**: Always includes category and specific problem detected

### Code Organization
```
src/bashrc_analyzer/
├── __init__.py          # Module exports
├── pattern_config.py    # Rule-based detection (existing)
└── ai_service.py        # AI integration (new)
```

## Testing

Run the demo to see AI integration without API keys:
```bash
python demo.py
```

Run basic tests:
```bash
python test_basic.py
```

Test with sample files:
```bash
python main.py tests/files/bashrc1 --no-ai
```

## Dependencies Added
- `anthropic`: Claude API client
- `openai`: OpenAI API client

## Next Steps (Future Enhancements)
1. **Caching**: Store AI responses to reduce API costs
2. **Batch Processing**: Analyze multiple files at once
3. **Module Compatibility**: Advanced conflict detection using cluster-specific data
4. **Web Interface**: As mentioned in Step 4 of the original plan

The AI integration is now complete and ready for use! 🎉