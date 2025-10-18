"""
Logging Configuration
Centralized logging setup for the application
"""
import logging
import logging.config
import os
from pathlib import Path
from typing import Dict, Any

def setup_logging(app_name: str = "workwave_coast", log_level: str = "INFO") -> logging.Logger:
    """
    Setup application logging configuration

    Args:
        app_name: Name of the application for log identification
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filename': f'logs/{app_name}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': f'logs/{app_name}_errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            app_name: {
                'level': log_level,
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'werkzeug': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console', 'file']
        }
    }

    # Apply configuration
    logging.config.dictConfig(logging_config)

    # Get logger for the application
    logger = logging.getLogger(app_name)
    logger.info(f"Logging configured for {app_name} at {log_level} level")

    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module

    Args:
        name: Name of the module/component

    Returns:
        Logger instance
    """
    return logging.getLogger(f"workwave_coast.{name}")

def log_request(logger: logging.Logger, request_data: Dict[str, Any]) -> None:
    """
    Log incoming request information

    Args:
        logger: Logger instance
        request_data: Request information to log
    """
    logger.info(f"Request: {request_data.get('method', 'UNKNOWN')} {request_data.get('path', 'UNKNOWN')}")

def log_response(logger: logging.Logger, response_data: Dict[str, Any]) -> None:
    """
    Log response information

    Args:
        logger: Logger instance
        response_data: Response information to log
    """
    status = response_data.get('status', 'UNKNOWN')
    logger.info(f"Response: {status}")

def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log error with context information

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    logger.error(error_msg, exc_info=True)
