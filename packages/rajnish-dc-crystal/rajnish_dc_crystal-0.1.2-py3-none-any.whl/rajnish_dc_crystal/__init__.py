"""
Crystal HR Automation - Automate your HR tasks with Crystal HR

This package provides tools to automate common HR tasks such as punch in/out,
attendance tracking, and notifications.
"""

__version__ = "0.1.0"

# Import key components to make them available at package level
from .core import CrystalHRAutomation
from .emailer import EmailNotifier
from .config import load_config, get_default_config_path

__all__ = ['CrystalHRAutomation', 'EmailNotifier', 'load_config', 'get_default_config_path']
