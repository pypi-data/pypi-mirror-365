"""
Configuration management for CrewAIMaster.
"""

import os
import yaml
import time
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
from pathlib import Path


class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: str = "openai"  # openai, google, anthropic, deepseek, custom
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    project_id: Optional[str] = None  # For Google Cloud
    region: Optional[str] = None      # For Google Cloud
    auth_file: Optional[str] = None   # For Google Service Account

class MemoryConfig(BaseModel):
    """Memory configuration."""
    enabled: bool = True
    short_term_limit: int = 10
    long_term_limit: int = 100
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

class ToolConfig(BaseModel):
    """Tool configuration."""
    enabled_categories: List[str] = ["web_search", "file_ops", "code_exec", "api_calls"]
    max_tools_per_agent: int = 5
    custom_tools_path: Optional[str] = None

class crewaimasterConfig(BaseModel):
    """Main CrewAIMaster configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
    
    # Agent generation settings
    max_agents_per_crew: int = 5
    default_agent_verbose: bool = True
    default_agent_max_iter: int = 5
    
    # Crew execution settings
    default_process: str = "sequential"
    execution_timeout: int = 300  # seconds
    
    # Logging and debugging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    debug_mode: bool = False

class Config:
    """Configuration manager for CrewAIMaster."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration."""
        self.config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        # First check for .crewaimaster/config.yaml in current directory
        local_config = Path(".crewaimaster/config.yaml")
        if local_config.exists():
            return str(local_config)
        
        # Fallback to home directory
        config_dir = Path.home() / ".crewaimaster"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.yaml")
    
    def _load_config(self) -> crewaimasterConfig:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f) or {}
                return crewaimasterConfig(**config_data)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                print("Using default configuration.")
        
        # Create default config and save it
        config = crewaimasterConfig()
        self.save_config(config)
        return config
    
    def save_config(self, config: Optional[crewaimasterConfig] = None):
        """Save configuration to file."""
        config_to_save = config or self._config
        
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(config_to_save.model_dump(), f, default_flow_style=False)
        except Exception as e:
            print(f"Warning: Failed to save config to {self.config_path}: {e}")
    
    def get(self, key: str = None) -> Any:
        """Get configuration value or entire config."""
        if key is None:
            return self._config
        
        # Support nested key access like "database.url"
        value = self._config
        for part in key.split('.'):
            value = getattr(value, part, None)
            if value is None:
                break
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        # This would need more complex logic for nested updates
        # For now, we'll keep it simple
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            self.save_config()
    
    @property
    def llm(self) -> LLMConfig:
        """Get LLM configuration."""
        return self._config.llm
    
    @property
    def memory(self) -> MemoryConfig:
        """Get memory configuration."""
        return self._config.memory
    
    @property
    def tools(self) -> ToolConfig:
        """Get tools configuration."""
        return self._config.tools
    
    def update_from_env(self):
        """Update configuration from environment variables. (DISABLED - Use .crewaimaster/config.yaml only)"""
        # Environment variable override is disabled to force users to use .crewaimaster/config.yaml
        # This ensures all configuration is managed through the CLI and config file
        pass