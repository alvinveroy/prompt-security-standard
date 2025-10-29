"""
Unit tests for UPSS implementation
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from upss_loader import UPSSLoader
from validator import UPSSValidator


class TestUPSSLoader:
    """Test suite for UPSSLoader."""
    
    def test_load_config(self, tmp_path):
        """Test loading a valid configuration."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'test_prompt': {
                    'path': 'prompts/test.md',
                    'type': 'system',
                    'version': '1.0.0'
                }
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_file = prompt_dir / "test.md"
        prompt_file.write_text("Test prompt content")
        
        loader = UPSSLoader(str(config_file))
        assert loader.config['upss_version'] == '1.0.0'
    
    def test_get_prompt(self, tmp_path):
        """Test retrieving a prompt."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'test_prompt': {
                    'path': 'prompts/test.md',
                    'type': 'system',
                    'version': '1.0.0'
                }
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_file = prompt_dir / "test.md"
        test_content = "Test prompt content"
        prompt_file.write_text(test_content)
        
        loader = UPSSLoader(str(config_file))
        content = loader.get_prompt('test_prompt')
        assert content == test_content
    
    def test_prompt_caching(self, tmp_path):
        """Test that prompts are cached correctly."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'test_prompt': {
                    'path': 'prompts/test.md',
                    'type': 'system',
                    'version': '1.0.0'
                }
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_file = prompt_dir / "test.md"
        prompt_file.write_text("Test content")
        
        loader = UPSSLoader(str(config_file))
        
        # First access
        content1 = loader.get_prompt('test_prompt')
        
        # Second access should use cache
        content2 = loader.get_prompt('test_prompt')
        
        assert content1 == content2
        assert 'test_prompt' in loader.prompts_cache
    
    def test_list_prompts(self, tmp_path):
        """Test listing all prompts."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'prompt1': {'path': 'p1.md', 'type': 'system', 'version': '1.0.0'},
                'prompt2': {'path': 'p2.md', 'type': 'user', 'version': '1.0.0'}
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        loader = UPSSLoader(str(config_file))
        prompts = loader.list_prompts()
        
        assert len(prompts) == 2
        assert 'prompt1' in prompts
        assert 'prompt2' in prompts


class TestUPSSValidator:
    """Test suite for UPSSValidator."""
    
    def test_valid_config(self, tmp_path):
        """Test validation of a valid configuration."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'test_prompt': {
                    'path': 'prompts/test.md',
                    'type': 'system',
                    'version': '1.0.0'
                }
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_file = prompt_dir / "test.md"
        prompt_file.write_text("Test content")
        
        validator = UPSSValidator(str(config_file))
        is_valid, errors, warnings = validator.validate()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_field(self, tmp_path):
        """Test validation fails for missing required fields."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'test_prompt': {
                    'path': 'prompts/test.md',
                    'type': 'system'
                    # Missing 'version'
                }
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        validator = UPSSValidator(str(config_file))
        is_valid, errors, warnings = validator.validate()
        
        assert not is_valid
        assert any('version' in error for error in errors)
    
    def test_invalid_prompt_type(self, tmp_path):
        """Test validation fails for invalid prompt type."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'test_prompt': {
                    'path': 'prompts/test.md',
                    'type': 'invalid_type',
                    'version': '1.0.0'
                }
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        validator = UPSSValidator(str(config_file))
        is_valid, errors, warnings = validator.validate()
        
        assert not is_valid
        assert any('invalid type' in error.lower() for error in errors)
    
    def test_missing_prompt_file(self, tmp_path):
        """Test validation fails when prompt file doesn't exist."""
        config = {
            'upss_version': '1.0.0',
            'prompts': {
                'test_prompt': {
                    'path': 'prompts/nonexistent.md',
                    'type': 'system',
                    'version': '1.0.0'
                }
            }
        }
        
        config_file = tmp_path / "upss_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        validator = UPSSValidator(str(config_file))
        is_valid, errors, warnings = validator.validate()
        
        assert not is_valid
        assert any('not found' in error.lower() for error in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
