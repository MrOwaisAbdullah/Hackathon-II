"""T155: Structured logging utilities for TeamFlow backend.

This module provides structured logging with JSON output for production
and human-readable format for development.
"""
import json
import logging
import logging.config
import sys
import time
from datetime import datetime
from typing import Any
from pathlib import Path as StdPath

from fastapi import Request
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class StructuredLogger:
    """Structured logger with JSON output for production."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """Configure logger with appropriate handlers and formatters."""
        if self.logger.handlers:
            return  # Already configured

        # Set log level based on environment
        log_level = logging.DEBUG if settings.environment == "development" else logging.INFO
        self.logger.setLevel(log_level)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Format: JSON in production, human-readable in development
        if settings.environment == "production":
            formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s',
                timestamp=True
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _log(self, level: str, message: str, **kwargs):
        """Internal log method with structured extra fields."""
        extra = {
            "environment": settings.environment,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        getattr(self.logger, level)(message, extra=extra)

    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        self._log("error", message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        self._log("debug", message, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


class RequestLoggingMiddleware:
    """T155: Middleware for logging all requests and responses.

    Logs:
    - Request method, path, query params
    - Response status code, duration
    - User ID and agency ID (if authenticated)
    - Request ID for tracing
    """

    def __init__(self, app):
        self.app = app
        self.logger = get_logger("api.request")

    async def __call__(self, scope, receive, send):
        """Process request and log timing/status."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Skip logging for health checks
        if scope["path"] == "/health":
            await self.app(scope, receive, send)
            return

        # Generate request ID for tracing
        # ASGI headers are a list of tuples: [(b"host", b"..."), (b"x-request-id", b"...")]
        headers_dict = dict(scope.get("headers", []))
        request_id = headers_dict.get(b"x-request-id", b"").decode() or str(int(time.time() * 1000))

        # Extract request info
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        full_path = f"{path}?{query_string}" if query_string else path

        # Extract user info from state (will be populated by JWT middleware)
        user_id = None
        agency_id = None

        start_time = time.time()

        # Intercept response to capture status code
        status_code = None

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)

            # Calculate duration
            duration = time.time() - start_time

            # Log successful request
            self.logger.info(
                "API request completed",
                method=method,
                path=path,
                full_path=full_path,
                status_code=status_code,
                duration_ms=round(duration * 1000, 2),
                request_id=request_id,
                user_id=user_id,
                agency_id=agency_id,
            )
        except Exception as e:
            duration = time.time() - start_time

            # Log failed request
            self.logger.error(
                "API request failed",
                method=method,
                path=path,
                full_path=full_path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration * 1000, 2),
                request_id=request_id,
                user_id=user_id,
                agency_id=agency_id,
            )
            raise


def log_api_call(
    logger: StructuredLogger,
    endpoint: str,
    action: str,
    user_id: str | None = None,
    agency_id: str | None = None,
    **kwargs
):
    """Helper function for logging API calls with consistent structure.

    Args:
        logger: The structured logger instance
        endpoint: The API endpoint being called (e.g., "POST /api/v1/tasks")
        action: The action being performed (e.g., "create_task")
        user_id: The ID of the user making the request
        agency_id: The ID of the agency
        **kwargs: Additional fields to include in the log
    """
    logger.info(
        f"API call: {action}",
        endpoint=endpoint,
        action=action,
        user_id=str(user_id) if user_id else None,
        agency_id=str(agency_id) if agency_id else None,
        **kwargs
    )
