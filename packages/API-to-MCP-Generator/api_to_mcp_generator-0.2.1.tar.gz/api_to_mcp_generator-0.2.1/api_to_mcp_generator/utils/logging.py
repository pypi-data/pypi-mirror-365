"""
Logging configuration module for the API to MCP Generator library.

This module provides structured logging capabilities using structlog,
with support for both JSON and console output formats, contextual logging,
and proper error handling.
"""

import sys
import logging
import structlog
from typing import Optional, Dict, Any
from pathlib import Path

# Map string log levels to Python's logging levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Default logger name for the library
DEFAULT_LOGGER_NAME = "api_to_mcp_generator"


def setup_logging(
    json_logs: bool = True,
    log_level: Optional[str] = None,
    logger_name: str = DEFAULT_LOGGER_NAME,
    include_location: bool = False,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        json_logs: Whether to output logs in JSON format
        log_level: Optional log level to set (debug, info, warning, error, critical)
        logger_name: Name for the logger
        include_location: Whether to include file location info in logs
    """
    # Get numeric log level
    level = LOG_LEVELS.get((log_level or "info").lower(), LOG_LEVELS["info"])

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Build processor list
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add location info if requested
    if include_location:
        processors.insert(
            -2,
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ),
        )

    # Choose output format and add appropriate processor
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure the standard library logger processor separately
    structlog.configure_once(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the standard library root logger
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=(
            structlog.processors.JSONRenderer()
            if json_logs
            else structlog.dev.ConsoleRenderer(colors=True)
        ),
        keep_exc_info=True,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Optional logger name. If not provided, uses the default library name.

    Returns:
        A configured structlog logger instance
    """
    _ensure_default_config()
    logger_name = name or DEFAULT_LOGGER_NAME
    return structlog.get_logger(logger_name)


class LoggerMixin:
    """
    Mixin class that provides easy access to a logger for any class.

    Usage:
        class MyClass(LoggerMixin):
            def some_method(self):
                self.logger.info("This is a log message", extra_field="value")
    """

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get a logger instance for this class."""
        return get_logger(f"{DEFAULT_LOGGER_NAME}.{self.__class__.__qualname__}")


def log_function_call(
    func_name: str,
    args: Dict[str, Any] = None,
    kwargs: Dict[str, Any] = None,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
) -> None:
    """
    Log a function call with its arguments.

    Args:
        func_name: Name of the function being called
        args: Positional arguments passed to the function
        kwargs: Keyword arguments passed to the function
        logger: Optional logger instance. If not provided, creates a new one.
    """
    if logger is None:
        logger = get_logger()

    log_data = {"function": func_name}

    if args:
        log_data["args"] = args
    if kwargs:
        log_data["kwargs"] = kwargs

    logger.debug("Function called", **log_data)


def log_operation_start(
    operation: str,
    context: Dict[str, Any] = None,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
) -> None:
    """
    Log the start of an operation.

    Args:
        operation: Name/description of the operation
        context: Additional context data
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()

    log_data = {"operation": operation, "status": "started"}
    if context:
        log_data.update(context)

    logger.info("Operation started", **log_data)


def log_operation_success(
    operation: str,
    context: Dict[str, Any] = None,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
) -> None:
    """
    Log the successful completion of an operation.

    Args:
        operation: Name/description of the operation
        context: Additional context data
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()

    log_data = {"operation": operation, "status": "success"}
    if context:
        log_data.update(context)

    logger.info("Operation completed successfully", **log_data)


def log_operation_error(
    operation: str,
    error: Exception,
    context: Dict[str, Any] = None,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
) -> None:
    """
    Log an operation error.

    Args:
        operation: Name/description of the operation
        error: The exception that occurred
        context: Additional context data
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()

    log_data = {
        "operation": operation,
        "status": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    if context:
        log_data.update(context)

    logger.error("Operation failed", **log_data, exc_info=error)


def log_validation_error(
    validation_type: str,
    errors: list,
    context: Dict[str, Any] = None,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
) -> None:
    """
    Log validation errors.

    Args:
        validation_type: Type of validation that failed
        errors: List of validation errors
        context: Additional context data
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()

    log_data = {
        "validation_type": validation_type,
        "error_count": len(errors),
        "errors": errors,
    }
    if context:
        log_data.update(context)

    logger.warning("Validation failed", **log_data)


def log_api_request(
    method: str,
    url: str,
    status_code: Optional[int] = None,
    response_time: Optional[float] = None,
    context: Dict[str, Any] = None,
    logger: Optional[structlog.stdlib.BoundLogger] = None,
) -> None:
    """
    Log an API request.

    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code
        response_time: Response time in seconds
        context: Additional context data
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger()

    log_data = {"http_method": method, "url": url}

    if status_code is not None:
        log_data["status_code"] = status_code
    if response_time is not None:
        log_data["response_time_ms"] = round(response_time * 1000, 2)
    if context:
        log_data.update(context)

    # Determine log level based on status code
    if status_code is None:
        level = "info"
    elif status_code < 400:
        level = "info"
    elif status_code < 500:
        level = "warning"
    else:
        level = "error"

    getattr(logger, level)("API request", **log_data)


def create_file_logger(file_path: Path) -> structlog.stdlib.BoundLogger:
    """
    Create a logger that writes to a specific file.

    Args:
        file_path: Path to the log file

    Returns:
        A logger configured to write to the specified file
    """
    # Create file handler
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Create logger
    logger_name = f"{DEFAULT_LOGGER_NAME}.file.{file_path.stem}"
    logger = logging.getLogger(logger_name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return structlog.get_logger(logger_name)


# Initialize with default configuration if not already configured
_is_configured = False


def _ensure_default_config():
    """Ensure logging is configured with defaults if not already done."""
    global _is_configured
    if not _is_configured and not structlog.is_configured():
        setup_logging(json_logs=False, log_level="info")
        _is_configured = True
