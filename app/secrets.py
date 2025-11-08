"""
Secrets management for Aegis.

Reads API keys from files (not environment variables) for better security.
OpenRouter key is stored in OPENROUTER_API_KEY.txt to avoid committing secrets.

See docs/ARCHITECTURE.md for secrets model explanation.
"""
from pathlib import Path

def read_openrouter_key() -> str | None:
    """
    Read OpenRouter API key from OPENROUTER_API_KEY.txt.
    
    Returns:
        API key string if file exists, None otherwise
    """
    p = Path("OPENROUTER_API_KEY.txt")
    return p.read_text().strip() if p.exists() else None
