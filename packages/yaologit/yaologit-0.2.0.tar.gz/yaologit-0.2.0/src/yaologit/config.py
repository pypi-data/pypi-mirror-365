"""
Configuration management for YaoLogit
"""

import os
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class YaoLogitConfig:
    """Configuration class for YaoLogit logger"""
    
    # Basic configuration
    name: str = "yaologit"
    log_dir: Union[str, Path] = "./logs"
    verbose: bool = True
    
    # Log levels to create separate files for
    levels: List[str] = field(default_factory=lambda: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    
    # Whether to create separate files for each log level
    separate_by_level: bool = True
    
    # Loguru specific configurations
    enqueue: bool = True  # Thread-safe logging
    backtrace: bool = True  # Show full traceback
    diagnose: bool = True  # Show variable values in traceback
    
    # Rotation and retention
    rotation: Optional[str] = "1 day"  # When to rotate log files
    retention: Optional[str] = "7 days"  # How long to keep old logs
    compression: Optional[str] = "zip"  # Compress rotated logs
    
    # Format
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    
    # Performance
    buffer_size: int = 1024 * 1024  # 1MB buffer
    
    # File encoding
    encoding: str = "utf-8"
    
    # Whether to also log to console
    console_output: bool = True
    console_level: str = "INFO"
    
    def __post_init__(self):
        """Validate and normalize configuration"""
        # Convert log_dir to Path
        self.log_dir = Path(self.log_dir).resolve()
        
        # Validate log levels
        valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
        for level in self.levels:
            if level not in valid_levels:
                raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")
        
        # Ensure log directory exists
        if self.separate_by_level:
            for level in self.levels:
                level_dir = self.log_dir / level
                level_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            "name": self.name,
            "log_dir": str(self.log_dir),
            "verbose": self.verbose,
            "levels": self.levels,
            "separate_by_level": self.separate_by_level,
            "enqueue": self.enqueue,
            "backtrace": self.backtrace,
            "diagnose": self.diagnose,
            "rotation": self.rotation,
            "retention": self.retention,
            "compression": self.compression,
            "format": self.format,
            "buffer_size": self.buffer_size,
            "encoding": self.encoding,
            "console_output": self.console_output,
            "console_level": self.console_level,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'YaoLogitConfig':
        """Create configuration from dictionary"""
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls) -> 'YaoLogitConfig':
        """Create configuration from environment variables"""
        config = {}
        
        # Map environment variables to config fields
        env_mapping = {
            "YAOLOGIT_NAME": "name",
            "YAOLOGIT_LOG_DIR": "log_dir",
            "YAOLOGIT_VERBOSE": "verbose",
            "YAOLOGIT_ENQUEUE": "enqueue",
            "YAOLOGIT_ROTATION": "rotation",
            "YAOLOGIT_RETENTION": "retention",
            "YAOLOGIT_COMPRESSION": "compression",
            "YAOLOGIT_CONSOLE_OUTPUT": "console_output",
            "YAOLOGIT_CONSOLE_LEVEL": "console_level",
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert boolean strings
                if config_key in ["verbose", "enqueue", "console_output"]:
                    config[config_key] = value.lower() in ("true", "1", "yes", "on")
                else:
                    config[config_key] = value
        
        # Handle levels as comma-separated list
        levels_env = os.environ.get("YAOLOGIT_LEVELS")
        if levels_env:
            config["levels"] = [level.strip() for level in levels_env.split(",")]
        
        return cls(**config)