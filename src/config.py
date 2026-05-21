import os
import json
import logging
from pathlib import Path
from typing import Any
from .models import AppConfig

logger = logging.getLogger(__name__)

def get_secret(key: str, default: Any = None) -> Any:
    """Retrieve secret from environment or Docker secret file."""
    # 1. Check environment variable
    val = os.getenv(key)
    if val is not None:
        return val
    
    # 2. Check Docker secret file
    secret_path = Path(f"/run/secrets/{key.lower()}")
    if secret_path.exists():
        return secret_path.read_text().strip()
    
    return default

def load_app_config() -> AppConfig:
    # Load from config.json if exists
    config_data = {}
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            config_data = json.load(f)

    # Override with environment variables for credentials
    if "credentials" not in config_data:
        config_data["credentials"] = {}

    platforms = ["telegram", "soroush", "bale", "rubika", "eitaa"]
    for p in platforms:
        token = get_secret(f"{p.upper()}_TOKEN")
        if token:
            if p not in config_data["credentials"]:
                config_data["credentials"][p] = {}
            config_data["credentials"][p]["token"] = token

    # Final validation with Pydantic
    return AppConfig(**config_data)
