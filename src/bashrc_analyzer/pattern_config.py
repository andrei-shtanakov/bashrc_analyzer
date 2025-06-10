import yaml
import re
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class Pattern:
    problem: str
    detector: str
    exclude_pattern: str
    ai_recommendation: str
    additional_check: Optional[str] = None


@dataclass
class Category:
    name: str
    description: str
    patterns: List[Pattern]


class PatternConfig:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "patterns.yaml"
        self.config_path = Path(config_path)
        self.categories: List[Category] = []
        self._load_config()
    
    def _load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                config_data = yaml.safe_load(file)
            
            for category_data in config_data.get('categories', []):
                patterns = []
                for pattern_data in category_data.get('patterns', []):
                    pattern = Pattern(
                        problem=pattern_data['problem'],
                        detector=pattern_data['detector'],
                        exclude_pattern=pattern_data.get('exclude_pattern', ''),
                        ai_recommendation=pattern_data['ai_recommendation'],
                        additional_check=pattern_data.get('additional_check')
                    )
                    patterns.append(pattern)
                
                category = Category(
                    name=category_data['name'],
                    description=category_data['description'],
                    patterns=patterns
                )
                self.categories.append(category)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def get_all_patterns(self) -> List[tuple[str, Pattern]]:
        all_patterns = []
        for category in self.categories:
            for pattern in category.patterns:
                all_patterns.append((category.name, pattern))
        return all_patterns
    
    def check_line(self, line: str) -> List[tuple[str, Pattern]]:
        matches = []
        for category_name, pattern in self.get_all_patterns():
            if re.search(pattern.detector, line, re.IGNORECASE):
                if pattern.exclude_pattern and re.search(pattern.exclude_pattern, line, re.IGNORECASE):
                    continue
                matches.append((category_name, pattern))
        return matches
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by its name."""
        for category in self.categories:
            if category.name == name:
                return category
        return None
    
    def get_patterns_by_category(self, category_name: str) -> List[Pattern]:
        """Get all patterns for a specific category."""
        category = self.get_category_by_name(category_name)
        return category.patterns if category else []