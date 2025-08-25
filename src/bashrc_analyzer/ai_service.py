import os
import sys
from typing import Optional, List, Tuple
from enum import Enum
from pathlib import Path

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMProvider(Enum):
    CLAUDE = "claude"
    CHATGPT = "chatgpt"
    NONE = "none"


class AIService:
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize AI clients if API keys are available."""
        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            except Exception as e:
                print(f"Warning: Failed to initialize Anthropic client: {e}")
        
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available LLM providers based on API keys and installed packages."""
        providers = []
        
        if self.anthropic_client:
            providers.append(LLMProvider.CLAUDE)
        
        if self.openai_client:
            providers.append(LLMProvider.CHATGPT)
        
        providers.append(LLMProvider.NONE)
        return providers
    
    def prompt_for_provider_choice(self) -> LLMProvider:
        """Interactive prompt for user to choose LLM provider."""
        available = self.get_available_providers()
        
        if len(available) == 1 and available[0] == LLMProvider.NONE:
            print("🤖 No AI providers available. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables to enable AI explanations.")
            return LLMProvider.NONE
        
        print("\n🤖 AI-Enhanced Analysis Available!")
        print("Choose your preferred AI assistant for detailed explanations:")
        
        choices = []
        for i, provider in enumerate(available, 1):
            if provider == LLMProvider.CLAUDE:
                print(f"  {i}. Claude (Anthropic)")
                choices.append(provider)
            elif provider == LLMProvider.CHATGPT:
                print(f"  {i}. ChatGPT (OpenAI)")
                choices.append(provider)
            elif provider == LLMProvider.NONE:
                print(f"  {i}. Skip AI analysis (basic recommendations only)")
                choices.append(provider)
        
        while True:
            try:
                choice = input(f"\nEnter your choice (1-{len(choices)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(choices):
                    return choices[choice_idx]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                sys.exit(0)
    
    def get_ai_explanation(self, provider: LLMProvider, problem_description: str, 
                          code_line: str, category_name: str) -> Optional[str]:
        """Get AI explanation for a detected problem. (Legacy method - use get_batch_ai_analysis)"""
        if provider == LLMProvider.NONE:
            return None
        
        prompt = self._create_prompt(problem_description, code_line, category_name)
        
        try:
            if provider == LLMProvider.CLAUDE and self.anthropic_client:
                return self._get_claude_explanation(prompt)
            elif provider == LLMProvider.CHATGPT and self.openai_client:
                return self._get_chatgpt_explanation(prompt)
        except Exception as e:
            print(f"Warning: AI explanation failed: {e}")
            return None
        
        return None
    
    def get_batch_ai_analysis(self, provider: LLMProvider, bashrc_content: str, 
                             issues: List[Tuple[int, str, str, any]]) -> Optional[str]:
        """Get AI analysis for all issues in a single request with full bashrc context."""
        if provider == LLMProvider.NONE or not issues:
            return None
        
        prompt = self._create_batch_prompt(bashrc_content, issues)
        
        try:
            if provider == LLMProvider.CLAUDE and self.anthropic_client:
                return self._get_claude_explanation(prompt)
            elif provider == LLMProvider.CHATGPT and self.openai_client:
                return self._get_chatgpt_explanation(prompt)
        except Exception as e:
            print(f"Warning: Batch AI analysis failed: {e}")
            return None
        
        return None
    
    def _create_prompt(self, problem_description: str, code_line: str, category_name: str) -> str:
        """Create a well-structured prompt for the AI."""
        return f"""You are a friendly AI assistant helping scientists and researchers who use High Performance Computing (HPC) clusters. Your job is to explain .bashrc configuration problems in simple, clear terms.

Context: The user has a potential issue in their .bashrc file.
Category: {category_name}
Problem detected: {problem_description}
Problematic line: {code_line}

Please provide:
1. A clear, non-technical explanation of why this is problematic
2. Specific consequences this could cause
3. A concrete example of how to fix it
4. Any additional tips related to HPC cluster usage

Keep your response concise (2-3 sentences for explanation, 1-2 for consequences, concrete fix example, optional tip).
Use friendly, helpful tone. Assume the user is a scientist, not necessarily a Linux expert."""
    
    def _create_batch_prompt(self, bashrc_content: str, issues: List[Tuple[int, str, str, any]]) -> str:
        """Create a comprehensive prompt for batch analysis of all issues."""
        # Load prompt text from config file
        prompt_text = self._load_prompt_text()
        
        issues_summary = []
        for line_num, line_content, category_name, pattern in issues:
            issues_summary.append(f"Line {line_num}: {line_content.strip()}")
            issues_summary.append(f"  Category: {category_name}")
            issues_summary.append(f"  Problem: {pattern.problem}")
            issues_summary.append("")
        
        return f"""{prompt_text}

FULL .BASHRC FILE CONTENT:
```bash
{bashrc_content}
```

DETECTED ISSUES:
{chr(10).join(issues_summary)}

Please provide a comprehensive analysis that:

1. **Overview**: Summarize the main categories of problems found and their potential interactions
2. **Issue-by-Issue Analysis**: For each problematic line, provide:
   - Clear, non-technical explanation of the problem
   - Specific consequences this could cause
   - Concrete fix example
   - How this issue might interact with other detected problems

3. **Priority Recommendations**: Rank the issues by severity and suggest the order to fix them
4. **General HPC Best Practices**: Any additional tips for .bashrc files on HPC clusters

Format your response clearly with section headers. Keep explanations friendly and accessible to scientists who may not be Linux experts. Focus on practical solutions and real-world consequences in HPC environments."""
    
    def _get_claude_explanation(self, prompt: str) -> str:
        """Get explanation from Claude."""
        # Use higher token limit for batch analysis
        max_tokens = 1500 if "FULL .BASHRC FILE CONTENT:" in prompt else 300
        
        message = self.anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    
    def _get_chatgpt_explanation(self, prompt: str) -> str:
        """Get explanation from ChatGPT."""
        # Use higher token limit for batch analysis
        max_tokens = 1500 if "FULL .BASHRC FILE CONTENT:" in prompt else 300
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    def _load_prompt_text(self) -> str:
        """Load prompt text from config/prompt.txt file."""
        try:
            # Get the prompt file path relative to this module
            current_dir = Path(__file__).parent
            prompt_path = current_dir.parent.parent / "config" / "prompt.txt"
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            # Fallback to default prompt if file not found or error
            return """You are a friendly AI assistant helping scientists and researchers who use High Performance Computing (HPC) clusters. Your job is to analyze .bashrc configuration files and explain problems in simple, clear terms."""
    
    def generate_annotated_bashrc(self, file_path: str, issues: List[Tuple[int, str, str, any]], 
                                 provider: LLMProvider, batch_analysis: Optional[str] = None) -> str:
        """Generate an annotated version of the bashrc file with AI comments."""
        if provider == LLMProvider.NONE:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                bashrc_content = ''.join(lines)
        except Exception:
            return None
        
        # If batch analysis is provided, use it; otherwise fall back to individual analysis
        if batch_analysis:
            # Add the comprehensive batch analysis as a header comment
            annotated_lines = [
                "# 🤖 AI COMPREHENSIVE ANALYSIS",
                "# " + "="*50
            ]
            for analysis_line in batch_analysis.split('\n'):
                if analysis_line.strip():
                    annotated_lines.append(f"# {analysis_line}")
            annotated_lines.extend(["# " + "="*50, "", ""])
            
            # Add the original file content
            for line in lines:
                annotated_lines.append(line.rstrip())
        else:
            # Fall back to individual line analysis (legacy method)
            issue_map = {}
            for line_num, line_content, category_name, pattern in issues:
                if line_num not in issue_map:
                    issue_map[line_num] = []
                issue_map[line_num].append((line_content, category_name, pattern))
            
            annotated_lines = []
            for line_num, line in enumerate(lines, 1):
                annotated_lines.append(line.rstrip())
                
                if line_num in issue_map:
                    for line_content, category_name, pattern in issue_map[line_num]:
                        ai_explanation = self.get_ai_explanation(
                            provider, pattern.problem, line_content, category_name
                        )
                        if ai_explanation:
                            comment_lines = ai_explanation.split('\n')
                            for comment_line in comment_lines:
                                if comment_line.strip():
                                    annotated_lines.append(f"# 🤖 AI: {comment_line.strip()}")
                        annotated_lines.append("")
        
        return '\n'.join(annotated_lines)