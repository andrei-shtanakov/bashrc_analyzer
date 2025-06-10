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


def main():
    parser = argparse.ArgumentParser(
        description="Smart Linter for .bashrc files - detects common problems and anti-patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Analyze ~/.bashrc
  %(prog)s /path/to/.bashrc   # Analyze specific file
  %(prog)s --help             # Show this help
        """
    )
    
    parser.add_argument(
        'bashrc_file',
        nargs='?',
        help='Path to .bashrc file to analyze (default: ~/.bashrc)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
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
        
        # Print report
        print_analysis_report(bashrc_path, issues)
        
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
