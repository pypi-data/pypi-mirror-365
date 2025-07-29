"""
Command-line interface for Crystal HR Automation.
"""
import argparse
import logging
import random
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

from .core import CrystalHRAutomation
from .emailer import EmailNotifier
from .config import load_config, get_default_config_path

logger = logging.getLogger(__name__)

def setup_logging(debug: bool = False) -> None:
    """Configure logging.
    
    Args:
        debug: Enable debug logging if True
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('crystal_hr_automation.log', encoding='utf-8')
        ]
    )

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description='Automate Crystal HR punch in/out')
    
    # Main command
    subparsers = parser.add_subparsers(dest='command', help='Command to run', required=True)
    
    # Punch command
    punch_parser = subparsers.add_parser('punch', help='Perform punch in/out')
    punch_parser.add_argument('action', choices=['in', 'out'], help='Punch action')
    punch_parser.add_argument('--delay', type=int, default=0,
                           help='Delay in minutes before performing the action')
    punch_parser.add_argument('--config', type=Path, default=None,
                           help='Path to config file')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command', 
                                                   help='Config command', required=True)
    
    # Config show
    config_show = config_subparsers.add_parser('show', help='Show current configuration')
    config_show.add_argument('--config', type=Path, default=None,
                           help='Path to config file')
    
    # Config init
    config_init = config_subparsers.add_parser('init', help='Initialize configuration')
    config_init.add_argument('--force', action='store_true',
                          help='Overwrite existing config file')
    config_init.add_argument('--config', type=Path, default=None,
                          help='Path to config file')
    
    # Global options
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    return parser

def handle_punch(args: argparse.Namespace, config: Dict[str, Any]) -> int:
    """Handle the punch command.
    
    Args:
        args: Command line arguments
        config: Loaded configuration
        
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    # Apply delay if specified
    delay = args.delay or config.get('behavior', {}).get('default_delay_minutes', 0)
    
    # Add random delay if configured
    random_delay = config.get('behavior', {}).get('random_delay_max_minutes', 0)
    if random_delay > 0:
        delay += random.randint(0, random_delay * 60)
    
    if delay > 0:
        logger.info(f"⏳ Waiting for {delay} minutes before {args.action}...")
        time.sleep(delay * 60)
    
    # Initialize email notifier if configured
    email_config = config.get('email', {})
    email_notifier = None
    
    if all(k in email_config for k in ['gmail_user', 'gmail_app_password', 'recipient_email']):
        email_notifier = EmailNotifier(
            gmail_user=email_config['gmail_user'],
            gmail_app_password=email_config['gmail_app_password'],
            recipient_email=email_config['recipient_email']
        )
    
    # Initialize HR automation
    hr_config = config.get('hr_system', {})
    hr = CrystalHRAutomation(
        base_url=hr_config.get('base_url', 'https://desicrewdtrial.crystalhr.com'),
        email_notifier=email_notifier
    )
    
    # Login and perform punch
    if not hr.login(
        username=hr_config.get('username', ''),
        password=hr_config.get('password', ''),
        company_id=hr_config.get('company_id', '1')
    ):
        return 1
    
    if not hr.punch(args.action):
        return 1
    
    return 0

def handle_config_show(config_path: Path) -> int:
    """Show the current configuration.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return 1
    
    try:
        with open(config_path, 'r') as f:
            print(f"Configuration file: {config_path}")
            print("-" * 40)
            print(f.read())
        return 0
    except Exception as e:
        logger.error(f"Failed to read config file: {e}")
        return 1

def handle_config_init(config_path: Path, force: bool = False) -> int:
    """Initialize a new configuration file.
    
    Args:
        config_path: Path to the config file
        force: Overwrite existing file if True
        
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    if config_path.exists() and not force:
        logger.error(f"Config file already exists: {config_path}")
        logger.info("Use --force to overwrite")
        return 1
    
    from .config import create_default_config
    create_default_config(config_path)
    logger.info(f"Created default config at {config_path}")
    return 0

def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug=args.debug)
    
    # Determine config path
    config_path = args.config
    if config_path is None and hasattr(args, 'config'):
        from .config import get_default_config_path
        config_path = get_default_config_path()
    
    # Handle config commands
    if args.command == 'config':
        if args.config_command == 'show':
            return handle_config_show(config_path)
        elif args.config_command == 'init':
            return handle_config_init(config_path, getattr(args, 'force', False))
    
    # Load config for other commands
    try:
        config = load_config(config_path)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return 1
    
    # Handle punch command
    if args.command == 'punch':
        return handle_punch(args, config)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
