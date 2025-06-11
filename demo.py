#!/usr/bin/env python3
"""
Demo script to show AI integration capabilities
"""

import sys
from pathlib import Path
from src.bashrc_analyzer.pattern_config import PatternConfig
from src.bashrc_analyzer.ai_service import AIService, LLMProvider

def demo_ai_integration():
    """Demonstrate AI integration without requiring API keys."""
    print("🚀 Bashrc Analyzer - AI Integration Demo")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIService()
    
    # Show available providers
    providers = ai_service.get_available_providers()
    print(f"Available AI providers: {[p.value for p in providers]}")
    
    # Demo the prompt creation
    problem = "Direct PATH overwrite detected"
    code_line = "export PATH=/usr/local/bin"
    category = "Direct Path Management"
    
    prompt = ai_service._create_prompt(problem, code_line, category)
    print(f"\n📝 Example AI Prompt:")
    print("-" * 30)
    print(prompt)
    
    # Show how the analyzer detects issues
    print(f"\n🔍 Pattern Detection Demo:")
    print("-" * 30)
    
    pattern_config = PatternConfig()
    test_lines = [
        "export PATH=/usr/local/bin",
        "module load GCC/11.2.0",
        "conda activate myenv",
        "export PATH=/home/user/bin:$PATH"
    ]
    
    for line in test_lines:
        matches = pattern_config.check_line(line)
        if matches:
            print(f"Line: {line}")
            for category_name, pattern in matches:
                print(f"  → Category: {category_name}")
                print(f"  → Problem: {pattern.problem}")
            print()
    
    print("✅ Demo complete!")
    print("\n💡 To use AI features, set environment variables:")
    print("   export ANTHROPIC_API_KEY='your-key'  # For Claude")
    print("   export OPENAI_API_KEY='your-key'     # For ChatGPT")

if __name__ == "__main__":
    demo_ai_integration()