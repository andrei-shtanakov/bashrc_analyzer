# Smart Linter for `.bashrc`

Configuration file analyzer for HPC clusters with AI assistant.

## Description

Two-tier system:
- **Rule-Based Engine** - fast analysis of common problems
- **AI Layer** - contextual explanations and recommendations

## Usage

```bash
module load tools/bashrc-checker
check-my-bashrc [file_path]  # defaults to ~/.bashrc
```

## Detected Issues

### Critical Issues
- **PATH/LD_LIBRARY_PATH overwrites**: `export PATH=/path` instead of `export PATH=/path:$PATH`
- **Conda in .bashrc**: Activating conda environments causes conflicts with system modules
- **Modules in .bashrc**: `module load` slows down all shells, better in `.bash_profile`

### Compatibility Conflicts  
- **Incompatible toolchains**: Simultaneous loading of different GCC/Intel versions
- **Hardcoded paths**: Local paths instead of system modules

## Architecture Decisions

- **Parser**: `bashlex` for reliable bash syntax analysis
- **AI integration**: API keys through environment variables
- **Conflicts**: Compatibility matrix in JSON/YAML
- **Cluster context**: Dynamic `module avail` queries

## Configuration

- **AI Prompt**: `config/prompt.txt`
- **API Keys**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (env vars)
- **Conflict Matrix**: `config/conflicts.json`

## Known Limitations

- Requires access to cluster `module` command
- AI analysis requires internet connection
- Complex bash constructs may not be fully analyzed

## TODO / Development Plans

- Expand module compatibility rule base
- Support for other shells (.zshrc, .cshrc)
- Web interface (if there's demand)
- Integration with cluster monitoring systems