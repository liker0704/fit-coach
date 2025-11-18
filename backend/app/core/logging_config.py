"""Centralized logging configuration with structured JSON logging."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields.

    Adds timestamp, level name, and other contextual information
    to each log record in structured JSON format.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """
        Add custom fields to log record.

        Args:
            log_record: Dictionary to be logged as JSON
            record: Original log record
            message_dict: Message dictionary
        """
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Add log level
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add module and function information
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    app_name: str = "fitcoach",
) -> None:
    """
    Configure application-wide logging.

    Sets up:
    - JSON structured logging
    - Console handler with JSON format
    - File handler with rotation (general logs)
    - Error file handler (ERROR and CRITICAL only)
    - Request context logging

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        app_name: Application name for log files
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # JSON formatter
    json_formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s"
    )

    # Console handler (stdout) - JSON format for production
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)

    # File handler - All logs with rotation
    try:
        from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

        # General log file with size-based rotation
        general_log_file = log_path / f"{app_name}.log"
        file_handler = RotatingFileHandler(
            general_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)

        # Error log file - Only errors and critical
        error_log_file = log_path / f"{app_name}_error.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        root_logger.addHandler(error_handler)

        # Time-based rotation for daily logs
        daily_log_file = log_path / f"{app_name}_daily.log"
        daily_handler = TimedRotatingFileHandler(
            daily_log_file,
            when="midnight",
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding="utf-8",
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(json_formatter)
        root_logger.addHandler(daily_handler)

    except Exception as e:
        # If file handlers fail, continue with console only
        root_logger.warning(f"Failed to setup file logging: {e}")

    # Suppress overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    root_logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "log_dir": log_dir,
            "app_name": app_name,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Processing request", extra={"user_id": 123})
    """
    return logging.getLogger(name)
