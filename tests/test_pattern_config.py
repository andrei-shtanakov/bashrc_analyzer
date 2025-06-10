import pytest
from pathlib import Path
import tempfile
import yaml
from src.bashrc_analyzer.pattern_config import PatternConfig, Pattern, Category


def test_pattern_config_loading():
    """Test that the pattern configuration loads correctly from the default file."""
    config = PatternConfig()
    
    assert len(config.categories) == 5
    assert config.categories[0].name == "Direct Path Management"
    assert config.categories[1].name == "Module Load in bashrc"
    assert config.categories[2].name == "Conda Activation"
    assert config.categories[3].name == "Conflicting Modules"
    assert config.categories[4].name == "Hardcoded Paths"


def test_pattern_matching():
    """Test pattern matching functionality."""
    config = PatternConfig()
    
    # Test PATH overwrite detection
    test_line = "export PATH=/usr/local/bin"
    matches = config.check_line(test_line)
    assert len(matches) >= 1
    assert any("Direct Path Management" in match[0] for match in matches)
    
    # Test that proper PATH setting doesn't trigger
    proper_line = "export PATH=/usr/local/bin:$PATH"
    matches = config.check_line(proper_line)
    path_matches = [match for match in matches if "Direct Path Management" in match[0]]
    assert len(path_matches) == 0
    
    # Test conda activation detection
    conda_line = "conda activate myenv"
    matches = config.check_line(conda_line)
    assert any("Conda Activation" in match[0] for match in matches)
    
    # Test module load detection
    module_line = "module load gcc/12.3.0"
    matches = config.check_line(module_line)
    assert any("Module Load in bashrc" in match[0] for match in matches)


def test_get_methods():
    """Test utility methods for accessing patterns and categories."""
    config = PatternConfig()
    
    # Test get_category_by_name
    category = config.get_category_by_name("Direct Path Management")
    assert category is not None
    assert category.name == "Direct Path Management"
    
    # Test get_patterns_by_category
    patterns = config.get_patterns_by_category("Conda Activation")
    assert len(patterns) >= 1
    assert all(isinstance(p, Pattern) for p in patterns)
    
    # Test get_all_patterns
    all_patterns = config.get_all_patterns()
    assert len(all_patterns) >= 5
    assert all(isinstance(item[1], Pattern) for item in all_patterns)


def test_custom_config_file():
    """Test loading from a custom configuration file."""
    test_config = {
        'categories': [
            {
                'name': 'Test Category',
                'description': 'A test category',
                'patterns': [
                    {
                        'problem': 'Test problem',
                        'detector': 'test_pattern',
                        'exclude_pattern': '',
                        'ai_recommendation': 'Test recommendation'
                    }
                ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(test_config, f)
        temp_path = f.name
    
    try:
        config = PatternConfig(temp_path)
        assert len(config.categories) == 1
        assert config.categories[0].name == "Test Category"
        assert len(config.categories[0].patterns) == 1
    finally:
        Path(temp_path).unlink()


def test_file_not_found():
    """Test error handling when configuration file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        PatternConfig("/nonexistent/path.yaml")