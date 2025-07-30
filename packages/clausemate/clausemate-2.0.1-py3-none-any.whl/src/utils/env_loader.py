"""Environment variable loader utility."""

import os
from pathlib import Path
from typing import Optional


def load_env_vars(env_file: str = ".env") -> dict[str, str]:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        Dictionary of loaded environment variables
    """
    env_path = Path(env_file)
    loaded_vars = {}
    
    if not env_path.exists():
        return loaded_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                os.environ[key] = value
                loaded_vars[key] = value
    
    return loaded_vars


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(key, default)


def ensure_env_loaded() -> None:
    """Ensure environment variables are loaded from .env file."""
    if not os.environ.get('GEMINI_API_KEY') and not os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN'):
        load_env_vars()


# Auto-load environment variables when module is imported
load_env_vars()