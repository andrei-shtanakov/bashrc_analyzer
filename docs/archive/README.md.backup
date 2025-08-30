# Bashrc Analyzer

A smart linter for `.bashrc` files that detects common problems and anti-patterns in HPC cluster environments.

## Overview

The Bashrc Analyzer helps scientists and researchers identify and fix problematic configurations in their `.bashrc` files that can cause issues on High Performance Computing clusters. It combines rule-based detection with optional AI-powered explanations.

## Features

- **Smart Detection**: Identifies 5 categories of common problems:
  - Direct PATH/LD_LIBRARY_PATH overwrites
  - Module loading in `.bashrc` (should be in `.bash_profile`)
  - Conda environment activation conflicts
  - Conflicting module versions
  - Hardcoded paths in home directories

- **AI-Enhanced Explanations**: Optional integration with Claude or ChatGPT for detailed, context-aware explanations

- **Multiple Output Formats**:
  - Terminal reports with recommendations
  - Annotated `.bashrc` files with inline AI comments

## Quick Start

```bash
# Basic analysis
python main.py

# Analyze specific file
python main.py /path/to/.bashrc

# Skip AI analysis
python main.py --no-ai
```

## AI Integration

Set environment variables to enable AI explanations:

```bash
export ANTHROPIC_API_KEY="your-claude-key"    # For Claude
export OPENAI_API_KEY="your-openai-key"       # For ChatGPT
```

## Installation

```bash
# Install dependencies
uv sync

# Run demo
python demo.py

# Run tests
python test_basic.py
```

## Example Output

```
= Analyzing: ~/.bashrc
============================================================
   Found 3 potential issue(s):

=Í Line 15: export PATH=/usr/local/bin
   Category: Direct Path Management
   > AI Explanation:
      You're completely replacing the PATH variable instead of adding to it.
      This breaks access to system commands like 'ls' and 'cd'...
```

## Requirements

- Python 3.13+
- Optional: Anthropic or OpenAI API keys for AI features

## License

Open source project for HPC cluster users and administrators.