"""Prometheus metrics for uptime monitoring (T093).

Provides Prometheus metrics for tracking:
- Chat service health
- Request latency and throughput
- Error rates
- Resource utilization

These metrics are exposed via /metrics endpoint for Prometheus scraping.
"""

import time
from functools import wraps
from typing import Callable

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# T093: Create a custom registry for our metrics
registry = CollectorRegistry()

# Chat Service Metrics
chat_requests_total = Counter(
    'teamflow_chat_requests_total',
    'Total number of chat requests',
    ['endpoint', 'status'],
    registry=registry
)

chat_request_duration_seconds = Histogram(
    'teamflow_chat_request_duration_seconds',
    'Chat request duration in seconds',
    ['endpoint'],
    buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=registry
)

chat_active_connections = Gauge(
    'teamflow_chat_active_connections',
    'Number of active chat connections',
    registry=registry
)

chat_errors_total = Counter(
    'teamflow_chat_errors_total',
    'Total number of chat errors',
    ['error_type', 'endpoint'],
    registry=registry
)

# AI Agent Metrics
ai_agent_requests_total = Counter(
    'teamflow_ai_agent_requests_total',
    'Total number of AI agent requests',
    ['model'],
    registry=registry
)

ai_agent_response_time_seconds = Histogram(
    'teamflow_ai_agent_response_time_seconds',
    'AI agent response time in seconds',
    ['model'],
    buckets=(.1, .5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
    registry=registry
)

ai_agent_tokens_total = Counter(
    'teamflow_ai_agent_tokens_total',
    'Total number of tokens processed',
    ['model', 'type'],  # type can be 'prompt' or 'completion'
    registry=registry
)

# RAG Service Metrics
rag_search_requests_total = Counter(
    'teamflow_rag_search_requests_total',
    'Total number of RAG search requests',
    ['status'],
    registry=registry
)

rag_search_duration_seconds = Histogram(
    'teamflow_rag_search_duration_seconds',
    'RAG search duration in seconds',
    buckets=(.01, .05, .1, .25, .5, 1.0, 2.5, 5.0),
    registry=registry
)

rag_results_count = Histogram(
    'teamflow_rag_results_count',
    'Number of results returned from RAG searches',
    buckets=(0, 1, 2, 3, 5, 10, 20, 50),
    registry=registry
)

# MCP Tools Metrics
mcp_tool_calls_total = Counter(
    'teamflow_mcp_tool_calls_total',
    'Total number of MCP tool calls',
    ['tool_name', 'status'],
    registry=registry
)

mcp_tool_duration_seconds = Histogram(
    'teamflow_mcp_tool_duration_seconds',
    'MCP tool execution duration in seconds',
    ['tool_name'],
    buckets=(.01, .05, .1, .25, .5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

# System Health Metrics
system_health = Gauge(
    'teamflow_system_health',
    'System health status (1=healthy, 0=unhealthy)',
    ['service'],  # service can be 'database', 'qdrant', 'ai_agent', etc.
    registry=registry
)

system_uptime_seconds = Gauge(
    'teamflow_system_uptime_seconds',
    'System uptime in seconds',
    registry=registry
)


# Track startup time for uptime calculation
_startup_time = time.time()


def update_uptime() -> None:
    """Update system uptime metric (T093)."""
    uptime = time.time() - _startup_time
    system_uptime_seconds.set(uptime)


def track_chat_request(endpoint: str, status: str = "success"):
    """Decorator to track chat requests (T093).

    Args:
        endpoint: Endpoint name (e.g., 'respond', 'sessions')
        status: Request status (success/error)

    Returns:
        Decorator function

    Example:
        @track_chat_request('respond')
        async def chat_respond(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = "error"
                chat_errors_total.labels(
                    error_type=type(e).__name__,
                    endpoint=endpoint
                ).inc()
                raise
            finally:
                # Track request duration
                duration = time.time() - start_time
                chat_request_duration_seconds.labels(endpoint=endpoint).observe(duration)
                chat_requests_total.labels(endpoint=endpoint, status=status_code).inc()

        return wrapper
    return decorator


def track_ai_request(model: str):
    """Decorator to track AI agent requests (T093).

    Args:
        model: Model name (e.g., 'gemini-pro', 'gpt-4')

    Returns:
        Decorator function

    Example:
        @track_ai_request('gemini-pro')
        async def process_message(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            result = await func(*args, **kwargs)

            # Track response time
            duration = time.time() - start_time
            ai_agent_response_time_seconds.labels(model=model).observe(duration)
            ai_agent_requests_total.labels(model=model).inc()

            return result

        return wrapper
    return decorator


def track_mcp_tool(tool_name: str):
    """Decorator to track MCP tool execution (T093).

    Args:
        tool_name: Name of the MCP tool

    Returns:
        Decorator function

    Example:
        @track_mcp_tool('add_task')
        def add_task(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = "error"
                raise
            finally:
                # Track tool execution duration
                duration = time.time() - start_time
                mcp_tool_duration_seconds.labels(tool_name=tool_name).observe(duration)
                mcp_tool_calls_total.labels(tool_name=tool_name, status=status_code).inc()

        return wrapper
    return decorator


def get_metrics() -> bytes:
    """Get Prometheus metrics in text format (T093).

    Returns:
        Metrics in Prometheus text format

    Example:
        from fastapi import Response
        @app.get("/metrics")
        async def metrics():
            return Response(content=get_metrics(), media_type=CONTENT_TYPE_LATEST)
    """
    # Update uptime before generating metrics
    update_uptime()

    return generate_latest(registry)


# Export metrics and helper functions
__all__ = [
    'get_metrics',
    'track_chat_request',
    'track_ai_request',
    'track_mcp_tool',
    'update_uptime',
    'chat_active_connections',
    'system_health',
]
