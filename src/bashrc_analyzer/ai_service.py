import os
import sys
from typing import Optional, List, Tuple
from enum import Enum

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
        """Get AI explanation for a detected problem."""
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
    
    def _get_claude_explanation(self, prompt: str) -> str:
        """Get explanation from Claude."""
        message = self.anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    
    def _get_chatgpt_explanation(self, prompt: str) -> str:
        """Get explanation from ChatGPT."""
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    def generate_annotated_bashrc(self, file_path: str, issues: List[Tuple[int, str, str, any]], 
                                 provider: LLMProvider) -> str:
        """Generate an annotated version of the bashrc file with AI comments."""
        if provider == LLMProvider.NONE:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return None
        
        # Create a map of line numbers to issues
        issue_map = {}
        for line_num, line_content, category_name, pattern in issues:
            if line_num not in issue_map:
                issue_map[line_num] = []
            issue_map[line_num].append((line_content, category_name, pattern))
        
        # Generate annotated content
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