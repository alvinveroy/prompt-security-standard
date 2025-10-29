"""
UPSS Configuration Loader
Loads and manages prompt configurations following the Universal Prompt Security Standard.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
from datetime import datetime


class UPSSLoader:
    """Loader for UPSS configuration files."""
    
    def __init__(self, config_path: str):
        """
        Initialize the UPSS loader.
        
        Args:
            config_path: Path to the UPSS configuration YAML file
        """
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent
        self.config: Dict[str, Any] = {}
        self.prompts_cache: Dict[str, str] = {}
        self.audit_log: list = []
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load and parse the UPSS configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        if not self.config:
            raise ValueError("Configuration file is empty")
        
        if 'upss_version' not in self.config:
            raise ValueError("Missing required field: upss_version")
    
    def get_prompt(self, prompt_id: str, use_cache: bool = True) -> str:
        """
        Retrieve a prompt by its ID.
        
        Args:
            prompt_id: Identifier for the prompt
            use_cache: Whether to use cached prompts
            
        Returns:
            The prompt content as a string
        """
        if use_cache and prompt_id in self.prompts_cache:
            self._log_access(prompt_id, "cache_hit")
            return self.prompts_cache[prompt_id]
        
        if 'prompts' not in self.config or prompt_id not in self.config['prompts']:
            raise KeyError(f"Prompt not found: {prompt_id}")
        
        prompt_config = self.config['prompts'][prompt_id]
        prompt_path = self.config_dir / prompt_config['path']
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.prompts_cache[prompt_id] = content
        self._log_access(prompt_id, "loaded")
        
        return content
    
    def get_prompt_metadata(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific prompt.
        
        Args:
            prompt_id: Identifier for the prompt
            
        Returns:
            Dictionary containing prompt metadata
        """
        if 'prompts' not in self.config or prompt_id not in self.config['prompts']:
            raise KeyError(f"Prompt not found: {prompt_id}")
        
        return self.config['prompts'][prompt_id]
    
    def list_prompts(self) -> list:
        """
        List all available prompt IDs.
        
        Returns:
            List of prompt identifiers
        """
        if 'prompts' not in self.config:
            return []
        return list(self.config['prompts'].keys())
    
    def get_prompt_hash(self, prompt_id: str) -> str:
        """
        Calculate SHA-256 hash of a prompt for integrity verification.
        
        Args:
            prompt_id: Identifier for the prompt
            
        Returns:
            Hexadecimal hash string
        """
        content = self.get_prompt(prompt_id)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _log_access(self, prompt_id: str, action: str) -> None:
        """
        Log prompt access for audit purposes.
        
        Args:
            prompt_id: Identifier for the prompt
            action: Action performed (loaded, cache_hit, etc.)
        """
        audit_config = self.config.get('audit', {})
        if not audit_config.get('enabled', False):
            return
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'prompt_id': prompt_id,
            'action': action
        }
        self.audit_log.append(log_entry)
    
    def get_audit_log(self) -> list:
        """
        Retrieve the audit log.
        
        Returns:
            List of audit log entries
        """
        return self.audit_log.copy()
    
    def reload(self) -> None:
        """Reload configuration and clear cache."""
        self.prompts_cache.clear()
        self._load_config()


if __name__ == "__main__":
    # Example usage
    loader = UPSSLoader("upss_config.yaml")
    
    print("Available prompts:", loader.list_prompts())
    print("\nSystem Assistant Prompt:")
    print(loader.get_prompt("system_assistant"))
    
    print("\nPrompt Metadata:")
    print(loader.get_prompt_metadata("system_assistant"))
    
    print("\nPrompt Hash:", loader.get_prompt_hash("system_assistant"))
