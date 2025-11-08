"""
Secrets management for Aegis.

Reads API keys from files (not environment variables) for better security.
OpenRouter key is stored in OPENROUTER_API_KEY.txt to avoid committing secrets.

See docs/ARCHITECTURE.md for secrets model explanation.
"""
from pathlib import Path
import os

# Find project root (where app/ directory is located)
_PROJECT_ROOT = Path(__file__).parent.parent

def read_airia_key() -> str | None:
    """
    Read Airia API key from AIRIA_API_KEY.txt.
    
    Returns:
        API key string if file exists, None otherwise
    """
    possible_paths = [
        _PROJECT_ROOT / "AIRIA_API_KEY.txt",
        Path("AIRIA_API_KEY.txt"),
    ]
    
    for p in possible_paths:
        if p.exists():
            try:
                return p.read_text().strip()
            except Exception:
                continue
    return None

def read_openrouter_key() -> str | None:
    """
    Read OpenRouter API key from OPENROUTER_API_KEY.txt.
    
    Returns:
        API key string if file exists, None otherwise
    """
    # Try multiple possible paths (project root, current dir)
    possible_paths = [
        _PROJECT_ROOT / "OPENROUTER_API_KEY.txt",  # Project root (preferred)
        Path("OPENROUTER_API_KEY.txt"),  # Current directory (fallback)
    ]
    
    for p in possible_paths:
        if p.exists():
            try:
                return p.read_text().strip()
            except Exception:
                continue
    return None
