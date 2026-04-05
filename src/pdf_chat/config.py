"""Configuration management for PDF Chat Assistant."""

import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.yaml"

_DEFAULTS = {
    "model": {
        "name": "gemma4",
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "chunking": {
        "chunk_size": 2000,
        "chunk_overlap": 200,
        "top_k": 3,
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    },
    "export": {
        "output_dir": "exports",
    },
}


def load_config(config_path: str | None = None) -> dict:
    """Load configuration from YAML file, falling back to defaults."""
    config = _DEFAULTS.copy()
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if path.exists():
        try:
            with open(path, "r") as f:
                user_config = yaml.safe_load(f) or {}
            config = _deep_merge(config, user_config)
            logger.info("Loaded config from %s", path)
        except Exception as exc:
            logger.warning("Failed to load config from %s: %s", path, exc)
    else:
        logger.debug("No config file at %s, using defaults", path)
    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep-merge *override* into *base*, returning a new dict."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def setup_logging(config: dict | None = None) -> None:
    """Configure logging from the config dict."""
    cfg = (config or _DEFAULTS).get("logging", {})
    logging.basicConfig(
        level=getattr(logging, cfg.get("level", "INFO")),
        format=cfg.get("format", _DEFAULTS["logging"]["format"]),
    )
