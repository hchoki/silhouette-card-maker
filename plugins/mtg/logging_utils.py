"""
Logging and error handling utilities for MTG card processing.
"""

import logging
import sys
from typing import Any
from functools import wraps

# Configure logging
def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with consistent formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

class ProcessingError(Exception):
    """Base exception for card processing errors."""
    pass

class ScryfallError(ProcessingError):
    """Errors related to Scryfall API interactions."""
    pass

class FrameDetectionError(ProcessingError):
    """Errors related to frame detection and analysis."""
    pass

class FileProcessingError(ProcessingError):
    """Errors related to file operations and image processing."""
    pass

def safe_get_card_field(card_json: dict, field: str, default: Any = None) -> Any:
    """Safely extract a field from card JSON with logging."""
    try:
        return card_json.get(field, default)
    except (KeyError, TypeError, AttributeError) as e:
        logger = logging.getLogger(__name__)
        card_name = card_json.get('name', 'unknown') if isinstance(card_json, dict) else 'unknown'
        logger.warning(f"⚠️ Failed to get field '{field}' from card '{card_name}': {e}")
        return default

def format_processing_status(current: int, total: int, operation: str = "Processing") -> str:
    """Format a consistent processing status message."""
    percentage = (current / total * 100) if total > 0 else 0
    return f"{operation} [{current}/{total}] ({percentage:.1f}%)"