"""Application monitoring and metrics."""

import time
import logging
from typing import Dict, Any
from functools import wraps

from prometheus_client import Counter, Histogram, Gauge, start_http_server
from fastapi import Request, Response
import structlog

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')
AI_REQUEST_COUNT = Counter('ai_requests_total', 'Total AI requests', ['mode', 'model'])
AI_REQUEST_DURATION = Histogram('ai_request_duration_seconds', 'AI request duration', ['mode'])
TOKEN_USAGE = Counter('tokens_used_total', 'Total tokens used', ['model', 'type'])
DOCUMENT_PROCESSING = Counter('documents_processed_total', 'Documents processed', ['type', 'status'])

# Structured logger
logger = structlog.get_logger()


def setup_monitoring(port: int = 8001):
    """Setup monitoring server."""
    start_http_server(port)
    logger.info("Monitoring server started", port=port)


async def metrics_middleware(request: Request, call_next):
    """Middleware for collecting metrics."""
    start_time = time.time()
    
    # Track active connections
    ACTIVE_CONNECTIONS.inc()
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        return response
    
    finally:
        ACTIVE_CONNECTIONS.dec()


def track_ai_usage(mode: str, model: str, duration: float, input_tokens: int, output_tokens: int):
    """Track AI usage metrics."""
    AI_REQUEST_COUNT.labels(mode=mode, model=model).inc()
    AI_REQUEST_DURATION.labels(mode=mode).observe(duration)
    TOKEN_USAGE.labels(model=model, type='input').inc(input_tokens)
    TOKEN_USAGE.labels(model=model, type='output').inc(output_tokens)


def track_document_processing(doc_type: str, status: str):
    """Track document processing metrics."""
    DOCUMENT_PROCESSING.labels(type=doc_type, status=status).inc()


def monitor_function(metric_name: str = None):
    """Decorator to monitor function execution."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    "function_completed",
                    function=func.__name__,
                    duration=duration,
                    success=True
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "function_failed",
                    function=func.__name__,
                    duration=duration,
                    error=str(e),
                    success=False
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    "function_completed",
                    function=func.__name__,
                    duration=duration,
                    success=True
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "function_failed",
                    function=func.__name__, 
                    duration=duration,
                    error=str(e),
                    success=False
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


