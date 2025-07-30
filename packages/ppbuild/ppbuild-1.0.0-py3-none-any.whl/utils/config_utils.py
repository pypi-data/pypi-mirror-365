import logging
import os
from pathlib import Path
from typing import Any, Dict

from .visitors import ConfigProcessor

logger = logging.getLogger("pp")


def get_config_paths():
    """Get configuration file paths."""
    config_name = os.getenv("PP_CONFIG_FILE", "pp.yaml")
    env_name = os.getenv("PP_ENV_FILE", ".pp.env")

    if base_dir := os.getenv("PP_BASE_DIR"):
        base_path = Path(base_dir)
        return base_path / config_name, base_path / env_name

    search_paths = [
        Path.cwd(),
        Path.home() / ".pp",
        Path.home(),
        Path(__file__).parent,
    ]

    # Find first existing config file
    for path in search_paths:
        config_file = path / config_name
        if config_file.exists():
            return config_file, path / env_name

    # Default to current directory if none found
    return Path.cwd() / config_name, Path.cwd() / env_name


def validate_and_process_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and process configuration using visitor pattern."""
    processor = ConfigProcessor(config)
    results = processor.process_all()

    validator = results["validation"]

    if validator.has_errors():
        logger.error("Configuration validation failed:")
        logger.error(validator.get_error_summary())
        raise ValueError("Invalid configuration")

    if validator.warnings:
        logger.warning("Configuration warnings:")
        for warning in validator.warnings:
            logger.warning(f"  - {warning}")

    logger.info("Configuration validation passed")
    return results
