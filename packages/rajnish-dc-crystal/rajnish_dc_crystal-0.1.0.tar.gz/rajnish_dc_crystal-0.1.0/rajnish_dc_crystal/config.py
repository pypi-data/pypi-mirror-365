"""
Configuration management for Crystal HR Automation.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_default_config_path() -> Path:
    """Get the default path for the configuration file.
    
    Returns:
        Path: Path to the default config file
    """
    return Path.home() / ".config" / "crystal_hr" / "config.json"

def create_default_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Create a default configuration.
    
    Args:
        config_path: Optional path to save the default config
        
    Returns:
        dict: Default configuration dictionary
    """
    default_config = {
        "hr_system": {
            "username": "your_username",
            "password": "your_password",
            "company_id": "1",
            "base_url": "https://desicrewdtrial.crystalhr.com"
        },
        "email": {
            "gmail_user": "your.email@gmail.com",
            "gmail_app_password": "your_app_password",
            "recipient_email": "recipient@example.com"
        },
        "behavior": {
            "default_delay_minutes": 0,
            "random_delay_max_minutes": 0
        }
    }
    
    if config_path:
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info(f"Created default config at {config_path}")
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
    
    return default_config

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from file or create default if not exists.
    
    Args:
        config_path: Path to config file. If None, uses default location.
        
    Returns:
        dict: Configuration dictionary
    """
    if config_path is None:
        config_path = get_default_config_path()
    
    if not config_path.exists():
        logger.info(f"Config file not found at {config_path}, creating default config")
        return create_default_config(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded config from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        logger.info("Using default configuration")
        return create_default_config()

def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> bool:
    """Save configuration to file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path to save config. If None, uses default location.
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    if config_path is None:
        config_path = get_default_config_path()
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Saved config to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        return False
