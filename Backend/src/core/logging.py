"""Logging configuration."""

import logging.config
import sys
from typing import Dict, Any

from src.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure application logging."""
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(funcName)s:%(lineno)d - %(message)s"
                ),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "formatter": "detailed",
                "filename": "studhelper.log",
            },
        },
        "loggers": {
            "studhelper": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    }
    
    logging.config.dictConfig(config)
    
    # Set application logger
    logger = logging.getLogger("studhelper")
    logger.info("Logging configured")

