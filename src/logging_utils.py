"""Lightweight structured logging for CLI and API."""

from __future__ import annotations

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("chokepoint")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    return logger


def get_logger(name: str = "chokepoint") -> logging.Logger:
    return logging.getLogger(name)
