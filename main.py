#!/usr/bin/env python3
"""
Bashrc Analyzer - Smart Linter for .bashrc files
Analyzes bashrc files for common problems and anti-patterns.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from src.bashrc_analyzer.pattern_config import PatternConfig, Pattern
from src.bashrc_analyzer.ai_service import AIService, LLMProvider


def analyze_bashrc_file(file_path: Path, pattern_config: PatternConfig) -> List[Tuple[int, str, str, Pattern]]:
    """
    Analyze a bashrc file and return found issues.
    
    Returns:
        List of tuples: (line_number, line_content, category_name, pattern)
    """
    issues = []
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        matches = pattern_config.check_line(line)
        for category_name, pattern in matches:
            issues.append((line_num, line, category_name, pattern))
    
    return issues


def print_analysis_report(file_path: Path, issues: List[Tuple[int, str, str, Pattern]]):
    """Print a formatted analysis report."""
    print(f"🔍 Analyzing: {file_path}")
    print("=" * 60)
    
    if not issues:
        print("✅ No issues found! Your .bashrc looks good.")
        return
    
    print(f"⚠️  Found {len(issues)} potential issue(s):\n")
    
    for line_num, line, category_name, pattern in issues:
        print(f"📍 Line {line_num}: {line}")
        print(f"   Category: {category_name}")
        print(f"   Problem: {pattern.problem}")
        print(f"   💡 Recommendation: {pattern.ai_recommendation}")
        print()


def print_ai_enhanced_report(file_path: Path, issues: List[Tuple[int, str, str, Pattern]], 
                           ai_service: AIService, provider: LLMProvider):
    """Print an AI-enhanced analysis report."""
    print(f"🔍 Analyzing: {file_path}")
    print(f"🤖 AI Assistant: {provider.value.title()}")
    print("=" * 60)
    
    if not issues:
        print("✅ No issues found! Your .bashrc looks good.")
        return
    
    print(f"⚠️  Found {len(issues)} potential issue(s):\n")
    
    for line_num, line, category_name, pattern in issues:
        print(f"📍 Line {line_num}: {line}")
        print(f"   Category: {category_name}")
        
        # Get AI explanation
        ai_explanation = ai_service.get_ai_explanation(provider, pattern.problem, line, category_name)
        if ai_explanation:
            print(f"   🤖 AI Explanation:")
            for explanation_line in ai_explanation.split('\n'):
                if explanation_line.strip():
                    print(f"      {explanation_line.strip()}")
        else:
            print(f"   💡 Basic Recommendation: {pattern.ai_recommendation}")
        print()


def save_annotated_bashrc(file_path: Path, issues: List[Tuple[int, str, str, Pattern]], 
                         ai_service: AIService, provider: LLMProvider):
    """Save an annotated version of the bashrc file."""
    annotated_content = ai_service.generate_annotated_bashrc(str(file_path), issues, provider)
    if annotated_content:
        output_path = file_path.parent / f"{file_path.name}.annotated"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(annotated_content)
            print(f"💾 Annotated version saved to: {output_path}")
        except Exception as e:
            print(f"❌ Failed to save annotated file: {e}")
    else:
        print("❌ Failed to generate annotated version")


def prompt_for_output_format() -> str:
    """Prompt user for output format preference."""
    print("\n📄 Choose output format:")
    print("  1. Terminal report only")
    print("  2. Save annotated .bashrc file with AI comments")
    print("  3. Both terminal report and annotated file")
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return choice
            else:
                print("Please enter 1, 2, or 3")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Smart Linter for .bashrc files - detects common problems and anti-patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Analyze ~/.bashrc with AI assistance
  %(prog)s /path/to/.bashrc   # Analyze specific file
  %(prog)s --no-ai            # Skip AI analysis (basic mode)
  %(prog)s --help             # Show this help

Environment Variables:
  ANTHROPIC_API_KEY           # For Claude AI assistance
  OPENAI_API_KEY              # For ChatGPT AI assistance
        """
    )
    
    parser.add_argument(
        'bashrc_file',
        nargs='?',
        help='Path to .bashrc file to analyze (default: ~/.bashrc)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Skip AI analysis and use basic recommendations only'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.2.0'
    )
    
    args = parser.parse_args()
    
    # Determine which file to analyze
    if args.bashrc_file:
        bashrc_path = Path(args.bashrc_file).expanduser().resolve()
    else:
        bashrc_path = Path.home() / '.bashrc'
    
    try:
        # Load pattern configuration
        pattern_config = PatternConfig()
        
        # Analyze the file
        issues = analyze_bashrc_file(bashrc_path, pattern_config)
        
        # Initialize AI service
        ai_service = AIService()
        
        if args.no_ai or not issues:
            # Basic report without AI
            print_analysis_report(bashrc_path, issues)
        else:
            # AI-enhanced analysis
            provider = ai_service.prompt_for_provider_choice()
            
            if provider == LLMProvider.NONE:
                print_analysis_report(bashrc_path, issues)
            else:
                # Get output format preference
                output_format = prompt_for_output_format()
                
                if output_format in ['1', '3']:
                    print_ai_enhanced_report(bashrc_path, issues, ai_service, provider)
                
                if output_format in ['2', '3']:
                    save_annotated_bashrc(bashrc_path, issues, ai_service, provider)
        
        # Exit with error code if issues found (useful for CI/CD)
        sys.exit(1 if issues else 0)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
