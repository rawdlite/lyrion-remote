#!/usr/bin/env python3
"""Shared configuration loader for lyrion-remote."""
import os
import sys
import tomllib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_config():
    """Load and return configuration from TOML file.
    
    Search order:
    1. LYRION_REMOTE_CONFIG environment variable
    2. /config/lyrion-remote/config.toml (production)
    3. ~/.config/lyrion-remote/config.toml (user home)
    
    Returns:
        dict: Parsed configuration
        
    Raises:
        SystemExit: If config file not found or cannot be parsed
    """
    config_path = Path(os.getenv('LYRION_REMOTE_CONFIG', '/config/lyrion-remote/config.toml'))
    if not config_path.is_file():
        config_path = Path.home() / '.config' / 'lyrion-remote' / 'config.toml'
    
    if not config_path.is_file():
        print(f"Error: Configuration file not found at '{config_path}'")
        print("Please ensure the file exists or set the LYRION_REMOTE_CONFIG environment variable.")
        sys.exit(1)
    
    try:
        with open(config_path, mode='rb') as fp:
            settings = tomllib.load(fp)
        logger.debug(f'Loaded configuration from {config_path}')
        return settings
    except Exception as exc:
        print(f"Error: Failed to parse configuration file at '{config_path}': {exc}")
        sys.exit(1)
