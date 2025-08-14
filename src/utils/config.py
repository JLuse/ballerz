"""
Configuration management utilities for the fantasy football analytics tool.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration settings
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    return config


def get_data_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    """
    Get data directory paths from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of Path objects for data directories
    """
    paths = config.get('paths', {})
    
    return {
        'raw_data': Path(paths.get('raw_data', 'data/raw')),
        'processed_data': Path(paths.get('processed_data', 'data/processed')),
        'models': Path(paths.get('models', 'models')),
        'results': Path(paths.get('results', 'results'))
    }


def ensure_directories(config: Dict[str, Any]) -> None:
    """
    Ensure all required directories exist.
    
    Args:
        config: Configuration dictionary
    """
    paths = get_data_paths(config)
    
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)


def get_model_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract model configuration from main config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Model configuration dictionary
    """
    return config.get('model', {})


def get_feature_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract feature configuration from main config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Feature configuration dictionary
    """
    return config.get('features', {})
