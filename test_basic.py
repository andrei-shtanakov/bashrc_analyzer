#!/usr/bin/env python3
"""
Basic tests for the bashrc analyzer
"""

from src.bashrc_analyzer.pattern_config import PatternConfig
from src.bashrc_analyzer.ai_service import AIService, LLMProvider

def test_pattern_matching():
    """Test basic pattern matching."""
    print("Testing pattern matching...")
    config = PatternConfig()
    
    test_cases = [
        ("export PATH=/usr/local/bin", "Direct Path Management"),
        ("conda activate myenv", "Conda Activation"),
        ("module load gcc/12.3.0", "Module Load in bashrc"),
        ("export PATH=/home/user/bin:$PATH", "Hardcoded Paths")
    ]
    
    for line, expected_category in test_cases:
        matches = config.check_line(line)
        found = any(expected_category in match[0] for match in matches)
        print(f"  Line: '{line}' -> {expected_category}: {'✅' if found else '❌'}")
        assert found, f"Expected to find {expected_category} in line: {line}"
    
    print("Pattern matching tests passed! ✅\n")

def test_ai_service_init():
    """Test AI service initialization."""
    print("Testing AI service initialization...")
    ai_service = AIService()
    
    providers = ai_service.get_available_providers()
    print(f"  Available providers: {[p.value for p in providers]}")
    
    # Should always have 'none' as an option
    assert LLMProvider.NONE in providers
    print("AI service initialization tests passed! ✅\n")

def test_prompt_generation():
    """Test AI prompt generation."""
    print("Testing AI prompt generation...")
    ai_service = AIService()
    
    prompt = ai_service._create_prompt(
        "Test problem", 
        "export PATH=/test", 
        "Test Category"
    )
    
    assert "HPC" in prompt
    assert "Test problem" in prompt
    assert "export PATH=/test" in prompt
    assert "Test Category" in prompt
    print("AI prompt generation tests passed! ✅\n")

if __name__ == "__main__":
    print("🧪 Running Basic Tests for Bashrc Analyzer")
    print("=" * 50)
    
    test_pattern_matching()
    test_ai_service_init()
    test_prompt_generation()
    
    print("🎉 All tests passed!")