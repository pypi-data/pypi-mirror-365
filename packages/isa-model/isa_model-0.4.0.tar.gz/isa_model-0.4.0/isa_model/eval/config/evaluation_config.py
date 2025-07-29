"""
Configuration management for evaluation framework
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EvaluationConfig:
    """
    Configuration class for evaluation settings.
    """
    
    # General settings
    output_dir: str = "evaluation_results"
    max_concurrent_evaluations: int = 3
    timeout_seconds: int = 600
    
    # Model settings
    default_provider: str = "openai"
    default_max_tokens: int = 150
    default_temperature: float = 0.1
    batch_size: int = 8
    
    # Metrics settings
    compute_all_metrics: bool = False
    custom_metrics: List[str] = None
    
    # Benchmark settings
    max_samples_per_benchmark: Optional[int] = None
    enable_few_shot: bool = True
    num_shots: int = 5
    
    # Experiment tracking
    use_wandb: bool = False
    wandb_project: Optional[str] = None
    wandb_entity: Optional[str] = None
    use_mlflow: bool = False
    mlflow_tracking_uri: Optional[str] = None
    
    # Results settings
    save_predictions: bool = True
    save_detailed_results: bool = True
    export_format: str = "json"  # json, csv, html
    
    def __post_init__(self):
        """Initialize default values after creation."""
        if self.custom_metrics is None:
            self.custom_metrics = []
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'EvaluationConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            EvaluationConfig instance
        """
        # Filter out unknown keys
        valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_keys}
        
        return cls(**filtered_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return asdict(self)


class ConfigManager:
    """Manager for handling multiple evaluation configurations."""
    
    def __init__(self, config_dir: str = "configs"):
        """Initialize configuration manager."""
        self.config_dir = config_dir
        self.configs: Dict[str, EvaluationConfig] = {}
        self.default_config = EvaluationConfig()
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
    
    def get_config(self, config_name: Optional[str] = None) -> EvaluationConfig:
        """Get configuration by name."""
        if config_name is None:
            return self.default_config
        
        if config_name in self.configs:
            return self.configs[config_name]
        
        return self.default_config