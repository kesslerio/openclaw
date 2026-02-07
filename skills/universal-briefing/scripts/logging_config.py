"""
Structured logging configuration for Universal Briefing.
Replaces ad-hoc print() calls with proper log levels.
"""
import logging
import sys


_configured = False


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application. Call once at startup."""
    global _configured
    if _configured:
        return
    _configured = True

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(numeric_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger("ub")
    root.setLevel(numeric_level)
    root.addHandler(handler)
    # Prevent duplicate messages from propagating to root logger
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under the 'ub' hierarchy."""
    return logging.getLogger(f"ub.{name}")
