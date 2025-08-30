# Bashrc Analyzer

A smart linter for `.bashrc` files designed for HPC (High Performance Computing) cluster environments. Combines rule-based detection with AI-powered explanations to help scientists and researchers identify and fix problematic shell configurations.

## 🚀 Features

### Smart Problem Detection
- **Direct PATH/LD_LIBRARY_PATH overwrites**: Prevents breaking system commands
- **Module loading issues**: Detects modules loaded in wrong shell files  
- **Conda conflicts**: Identifies conda activations that break HPC modules
- **Toolchain conflicts**: Finds incompatible compiler/library combinations
- **Hardcoded paths**: Locates suboptimal hardcoded directory paths

### AI-Enhanced Analysis
- **Multiple AI Providers**: Support for Claude (Anthropic) and ChatGPT (OpenAI)
- **Contextual Explanations**: AI analyzes your entire `.bashrc` for comprehensive insights
- **Interactive Experience**: Choose your preferred AI assistant interactively
- **Batch Analysis**: All issues analyzed together for better context understanding

### Flexible Output Options
- **Terminal Reports**: Color-coded analysis with recommendations
- **Annotated Files**: Generate commented `.bashrc` files with AI explanations inline
- **Configurable Rules**: YAML-based pattern configuration for easy customization

## 📋 Quick Start

```bash
# Basic analysis of ~/.bashrc
python main.py

# Analyze specific file with AI assistance
python main.py /path/to/your/.bashrc

# Skip AI analysis (faster, basic recommendations only)
python main.py --no-ai

# Run demo with sample problematic files
python demo.py
```

## 🛠 Installation

### Requirements
- **Python 3.13+**
- **uv** (Python package manager - recommended) or pip

### Setup
```bash
# Clone repository
git clone <repository-url>
cd bashrc_analyzer

# Install dependencies (recommended: uv)
uv sync

# OR with pip
pip install -r requirements.txt

# Test installation
python demo.py
```

### Optional: AI Integration
Set environment variables to enable AI-powered explanations:

```bash
# For Claude (Anthropic) - recommended for cost-effectiveness
export ANTHROPIC_API_KEY="your-claude-api-key"

# For ChatGPT (OpenAI)
export OPENAI_API_KEY="your-openai-api-key"

# You can set both - the tool will let you choose interactively
```

## 📊 Example Output

### Without AI (Basic Mode)
```
🔍 Analyzing: ~/.bashrc
============================================================
⚠️  Found 3 potential issue(s):

📝 Line 15: export PATH=/usr/local/bin
   Category: Direct Path Management
   Problem: Direct PATH overwrite without preserving existing paths
   💡 Recommendation: Use export PATH=/usr/local/bin:$PATH to preserve system paths
```

### With AI Enhancement
```
🔍 Analyzing: ~/.bashrc
🤖 AI Assistant: Claude
============================================================
⚠️  Found 3 potential issue(s):

📝 Line 15: export PATH=/usr/local/bin  
   Category: Direct Path Management
   🤖 AI Explanation:
      You're completely replacing your PATH variable instead of adding to it.
      This breaks access to essential system commands like 'ls', 'cd', and 'vim'
      because the shell can no longer find them.
      
      Fix: export PATH=/usr/local/bin:$PATH
      
      The :$PATH part preserves all existing system paths while adding your
      custom directory first in the search order.

📝 Line 25: conda activate myenv
   Category: Conda Environment Activation  
   🤖 AI Explanation:
      Activating conda in .bashrc causes conflicts with HPC modules and slows
      down all shell operations. Conda aggressively modifies library paths
      which can break module-loaded software.
      
      For HPC clusters: Remove this line and activate conda manually when needed,
      or better yet - load conda as a module after other required modules.
```

## ⚙️ Configuration

### Pattern Rules
Edit `config/patterns.yaml` to customize detection rules:
```yaml
categories:
  - name: "Direct Path Management"
    description: "PATH/LD_LIBRARY_PATH overwrite issues"
    patterns:
      - problem: "Direct PATH overwrite without preserving existing paths"
        detector: "export\\s+PATH\\s*="
        exclude_pattern: "\\$PATH"
        ai_recommendation: "Always append to PATH with :$PATH suffix"
```

### AI Prompts
Customize AI behavior by editing `config/prompt.txt`:
```
You are a friendly AI assistant helping scientists and researchers...
```

## 🏗 Architecture

```
src/bashrc_analyzer/
├── pattern_config.py     # YAML-based rule engine
├── ai_service.py         # AI integration (Claude/ChatGPT)
└── __init__.py

config/
├── patterns.yaml         # Detection rules
└── prompt.txt           # AI system prompt

tests/files/             # Sample problematic .bashrc files
main.py                  # CLI entry point
demo.py                  # Interactive demonstration
```

### Key Components

- **Rule-Based Engine**: Fast pattern matching using regex and YAML configuration
- **AI Service**: Handles multiple LLM providers with graceful fallbacks
- **Batch Analysis**: Sends entire `.bashrc` context to AI for comprehensive understanding
- **Interactive CLI**: User-friendly prompts for AI provider selection and output format

## 🧪 Testing

```bash
# Run basic functionality tests
python test_basic.py

# Test with sample problematic files
python main.py tests/files/bashrc1 --no-ai

# Interactive demo with AI (if API keys configured)
python demo.py
```

## 🎯 Common Use Cases

### HPC Cluster Administrators
```bash
# Check all user bashrc files in batch
for user in /home/*; do
    echo "Checking $user/.bashrc"
    python main.py "$user/.bashrc" --no-ai >> cluster_analysis.log
done
```

### Individual Users
```bash
# Get comprehensive AI analysis
python main.py

# Quick check before submitting jobs
python main.py --no-ai
```

### New User Onboarding
```bash
# Generate educational annotated file
python main.py ~/.bashrc
# Choose option 2: "Save annotated .bashrc file" 
# Share the generated file with explanations
```

## 🤝 Contributing

Issues detected by the analyzer are based on real problems observed in HPC environments. To add new detection patterns:

1. Edit `config/patterns.yaml` to add new rules
2. Test with `python test_basic.py`
3. Add sample problematic files to `tests/files/`

## 📄 License

Open source project for HPC cluster users and administrators.

---

**💡 Tip**: Start with `python demo.py` to see the analyzer in action with sample problematic configurations!