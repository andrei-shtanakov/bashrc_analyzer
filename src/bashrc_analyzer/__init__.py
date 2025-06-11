"""
Bashrc Analyzer - Smart Linter for .bashrc files
"""

from .pattern_config import PatternConfig, Pattern, Category
from .ai_service import AIService, LLMProvider

__version__ = "0.2.0"
__all__ = ["PatternConfig", "Pattern", "Category", "AIService", "LLMProvider"]