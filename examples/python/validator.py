"""
UPSS Configuration Validator
Validates UPSS configuration files and prompt structures.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


class UPSSValidator:
    """Validator for UPSS configuration files."""
    
    REQUIRED_ROOT_FIELDS = ['upss_version', 'prompts']
    REQUIRED_PROMPT_FIELDS = ['path', 'type', 'version']
    ALLOWED_PROMPT_TYPES = ['system', 'user', 'assistant']
    
    def __init__(self, config_path: str):
        """
        Initialize the validator.
        
        Args:
            config_path: Path to the UPSS configuration file
        """
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.config: Dict[str, Any] = {}
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Perform full validation of the UPSS configuration.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check file exists
        if not self.config_path.exists():
            self.errors.append(f"Configuration file not found: {self.config_path}")
            return False, self.errors, self.warnings
        
        # Load and parse YAML
        if not self._load_config():
            return False, self.errors, self.warnings
        
        # Validate structure
        self._validate_structure()
        self._validate_prompts()
        self._validate_security_config()
        self._validate_prompt_files()
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _load_config(self) -> bool:
        """Load and parse the configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            if not self.config:
                self.errors.append("Configuration file is empty")
                return False
            
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading configuration: {e}")
            return False
    
    def _validate_structure(self) -> None:
        """Validate the root structure of the configuration."""
        for field in self.REQUIRED_ROOT_FIELDS:
            if field not in self.config:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate UPSS version format
        if 'upss_version' in self.config:
            version = self.config['upss_version']
            if not isinstance(version, str) or not version:
                self.errors.append("upss_version must be a non-empty string")
    
    def _validate_prompts(self) -> None:
        """Validate the prompts configuration."""
        if 'prompts' not in self.config:
            return
        
        prompts = self.config['prompts']
        if not isinstance(prompts, dict):
            self.errors.append("prompts must be a dictionary")
            return
        
        if not prompts:
            self.warnings.append("No prompts defined in configuration")
        
        for prompt_id, prompt_config in prompts.items():
            self._validate_prompt(prompt_id, prompt_config)
    
    def _validate_prompt(self, prompt_id: str, config: Any) -> None:
        """Validate a single prompt configuration."""
        if not isinstance(config, dict):
            self.errors.append(f"Prompt '{prompt_id}' configuration must be a dictionary")
            return
        
        # Check required fields
        for field in self.REQUIRED_PROMPT_FIELDS:
            if field not in config:
                self.errors.append(f"Prompt '{prompt_id}' missing required field: {field}")
        
        # Validate type
        if 'type' in config:
            prompt_type = config['type']
            if prompt_type not in self.ALLOWED_PROMPT_TYPES:
                self.errors.append(
                    f"Prompt '{prompt_id}' has invalid type: {prompt_type}. "
                    f"Allowed types: {', '.join(self.ALLOWED_PROMPT_TYPES)}"
                )
        
        # Validate version format
        if 'version' in config:
            version = config['version']
            if not isinstance(version, str) or not version:
                self.errors.append(f"Prompt '{prompt_id}' version must be a non-empty string")
        
        # Validate path
        if 'path' in config:
            path = config['path']
            if not isinstance(path, str) or not path:
                self.errors.append(f"Prompt '{prompt_id}' path must be a non-empty string")
    
    def _validate_security_config(self) -> None:
        """Validate security configuration if present."""
        if 'security' not in self.config:
            self.warnings.append("No security configuration defined")
            return
        
        security = self.config['security']
        if not isinstance(security, dict):
            self.errors.append("security must be a dictionary")
            return
        
        # Validate access control if present
        if 'access_control' in security:
            ac = security['access_control']
            if not isinstance(ac, dict):
                self.errors.append("security.access_control must be a dictionary")
            elif ac.get('enabled') and 'roles' not in ac:
                self.warnings.append("Access control is enabled but no roles defined")
    
    def _validate_prompt_files(self) -> None:
        """Validate that prompt files exist and are readable."""
        if 'prompts' not in self.config:
            return
        
        for prompt_id, prompt_config in self.config['prompts'].items():
            if 'path' not in prompt_config:
                continue
            
            prompt_path = self.config_dir / prompt_config['path']
            
            if not prompt_path.exists():
                self.errors.append(f"Prompt file not found for '{prompt_id}': {prompt_path}")
            elif not prompt_path.is_file():
                self.errors.append(f"Prompt path for '{prompt_id}' is not a file: {prompt_path}")
            else:
                # Try to read the file
                try:
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if not content.strip():
                        self.warnings.append(f"Prompt file for '{prompt_id}' is empty: {prompt_path}")
                    
                    # Check file size
                    validation_config = self.config.get('validation', {})
                    max_size = validation_config.get('max_prompt_size', 10240)
                    if len(content) > max_size:
                        self.warnings.append(
                            f"Prompt file for '{prompt_id}' exceeds maximum size "
                            f"({len(content)} > {max_size}): {prompt_path}"
                        )
                except Exception as e:
                    self.errors.append(f"Error reading prompt file for '{prompt_id}': {e}")


def main():
    """Command-line interface for the validator."""
    if len(sys.argv) < 2:
        print("Usage: python validator.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    validator = UPSSValidator(config_file)
    
    print(f"Validating UPSS configuration: {config_file}")
    print("=" * 60)
    
    is_valid, errors, warnings = validator.validate()
    
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"  ✗ {error}")
    
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
    
    if not errors and not warnings:
        print("\n✓ Configuration is valid with no warnings!")
    elif is_valid:
        print(f"\n✓ Configuration is valid (with {len(warnings)} warning(s))")
    else:
        print(f"\n✗ Configuration is invalid ({len(errors)} error(s))")
    
    print("=" * 60)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
