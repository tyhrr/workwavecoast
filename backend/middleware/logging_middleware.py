"""
Logging Middleware
Request/response logging and performance monitoring
"""
import logging
import time
import uuid
from functools import wraps
from flask import request, g, current_app
from typing import Dict, Any, Callable, Optional
import json

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Middleware for request/response logging"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.logging_middleware = self
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

    def before_request(self):
        """Log request start and set up tracking"""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

        # Skip logging for health checks and static files
        if self._should_skip_logging():
            return

        # Log request start
        request_data = {
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_type': request.content_type,
            'content_length': request.content_length,
            'args': dict(request.args),
            'endpoint': request.endpoint
        }

        # Add JSON data for POST/PUT requests (but sanitize sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            try:
                json_data = request.get_json()
                if json_data:
                    # Sanitize sensitive fields
                    sanitized_data = self._sanitize_request_data(json_data)
                    request_data['json_data'] = sanitized_data
            except Exception as e:
                request_data['json_error'] = str(e)

        logger.info("Request started", extra=request_data)

    def after_request(self, response):
        """Log response"""
        if not hasattr(g, 'request_id') or self._should_skip_logging():
            return response

        # Calculate request duration
        duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0

        # Log response
        response_data = {
            'request_id': g.request_id,
            'status_code': response.status_code,
            'content_type': response.content_type,
            'content_length': response.content_length,
            'duration_ms': round(duration * 1000, 2),
            'method': request.method,
            'path': request.path
        }

        # Add response data for errors or debug mode
        if response.status_code >= 400 or current_app.debug:
            try:
                if response.is_json:
                    response_json = response.get_json()
                    if response_json:
                        response_data['response_data'] = response_json
            except Exception:
                pass  # Ignore response parsing errors

        # Choose log level based on status code
        if response.status_code >= 500:
            logger.error("Request completed with server error", extra=response_data)
        elif response.status_code >= 400:
            logger.warning("Request completed with client error", extra=response_data)
        else:
            logger.info("Request completed successfully", extra=response_data)

        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.request_id

        return response

    def teardown_request(self, exception):
        """Log any uncaught exceptions"""
        if exception and hasattr(g, 'request_id'):
            logger.error(
                "Request ended with exception",
                extra={
                    'request_id': g.request_id,
                    'exception': str(exception),
                    'exception_type': type(exception).__name__,
                    'method': request.method,
                    'path': request.path
                },
                exc_info=True
            )

    def _should_skip_logging(self) -> bool:
        """Determine if logging should be skipped for this request"""
        skip_paths = [
            '/health',
            '/health/quick',
            '/static/',
            '/favicon.ico'
        ]

        return any(request.path.startswith(path) for path in skip_paths)

    def _sanitize_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from request logging"""
        sensitive_fields = [
            'password',
            'token',
            'secret',
            'key',
            'authorization',
            'auth',
            'credentials'
        ]

        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_request_data(value)
            else:
                sanitized[key] = value

        return sanitized


def log_requests(include_response: bool = False, include_duration: bool = True) -> Callable:
    """
    Decorator to log individual requests

    Args:
        include_response: Whether to include response data in logs
        include_duration: Whether to include request duration
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            request_id = getattr(g, 'request_id', str(uuid.uuid4()))

            # Log request start
            logger.info(
                f"Starting {f.__name__}",
                extra={
                    'request_id': request_id,
                    'function': f.__name__,
                    'method': request.method,
                    'path': request.path
                }
            )

            try:
                result = f(*args, **kwargs)

                # Log success
                log_data = {
                    'request_id': request_id,
                    'function': f.__name__,
                    'status': 'success'
                }

                if include_duration:
                    duration = time.time() - start_time
                    log_data['duration_ms'] = round(duration * 1000, 2)

                if include_response and result:
                    # Only log first 500 chars of response to avoid huge logs
                    result_str = str(result)[:500]
                    log_data['response_preview'] = result_str

                logger.info(f"Completed {f.__name__}", extra=log_data)
                return result

            except Exception as e:
                # Log error
                duration = time.time() - start_time
                logger.error(
                    f"Error in {f.__name__}",
                    extra={
                        'request_id': request_id,
                        'function': f.__name__,
                        'status': 'error',
                        'error': str(e),
                        'duration_ms': round(duration * 1000, 2)
                    },
                    exc_info=True
                )
                raise

        return decorated_function
    return decorator


def log_performance(threshold_ms: float = 1000) -> Callable:
    """
    Decorator to log slow requests

    Args:
        threshold_ms: Log warning if request takes longer than this (milliseconds)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            try:
                result = f(*args, **kwargs)

                duration = time.time() - start_time
                duration_ms = round(duration * 1000, 2)

                if duration_ms > threshold_ms:
                    logger.warning(
                        f"Slow request detected in {f.__name__}",
                        extra={
                            'function': f.__name__,
                            'duration_ms': duration_ms,
                            'threshold_ms': threshold_ms,
                            'method': request.method,
                            'path': request.path
                        }
                    )

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Performance monitoring error in {f.__name__}",
                    extra={
                        'function': f.__name__,
                        'duration_ms': round(duration * 1000, 2),
                        'error': str(e)
                    }
                )
                raise

        return decorated_function
    return decorator


def log_user_actions(action: str, resource: str = None) -> Callable:
    """
    Decorator to log user actions for auditing

    Args:
        action: Action being performed (e.g., 'create', 'update', 'delete')
        resource: Resource being acted upon (e.g., 'application', 'user')
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user info if available
            user_info = getattr(g, 'current_user', {})
            user_id = user_info.get('id', 'anonymous')
            username = user_info.get('username', 'anonymous')

            # Log the action
            logger.info(
                f"User action: {action}",
                extra={
                    'action': action,
                    'resource': resource,
                    'user_id': user_id,
                    'username': username,
                    'function': f.__name__,
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr
                }
            )

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def log_api_usage(f: Callable) -> Callable:
    """
    Decorator to log API endpoint usage for analytics
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log API usage
        logger.info(
            "API endpoint accessed",
            extra={
                'endpoint': f.__name__,
                'method': request.method,
                'path': request.path,
                'user_agent': request.headers.get('User-Agent', ''),
                'remote_addr': request.remote_addr,
                'timestamp': time.time()
            }
        )

        return f(*args, **kwargs)

    return decorated_function
