"""
Rate Limiting Configuration
Setup and configuration for API rate limiting
"""
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global limiter instance
limiter: Optional[Limiter] = None

def init_rate_limiter(app: Flask) -> Limiter:
    """
    Initialize rate limiter for the Flask application

    Args:
        app: Flask application instance

    Returns:
        Configured Limiter instance
    """
    global limiter

    try:
        # Configure rate limiter
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["1000 per hour", "100 per minute"],
            storage_uri="memory://",  # Use memory storage for simplicity
            application_limits=["2000 per hour"]
        )
        limiter.init_app(app)

        # Add rate limit headers to responses
        @app.after_request
        def add_rate_limit_headers(response):
            """Add rate limit information to response headers"""
            try:
                if hasattr(response, 'headers'):
                    # These headers will be added automatically by flask-limiter
                    # but we can customize them here if needed
                    pass
            except Exception as e:
                logger.warning(f"Failed to add rate limit headers: {e}")
            return response

        logger.info("Rate limiter initialized successfully")
        return limiter

    except Exception as e:
        logger.error(f"Failed to initialize rate limiter: {e}")
        # Return a dummy limiter that doesn't actually limit anything
        return DummyLimiter()

class DummyLimiter:
    """
    Dummy limiter for when rate limiting fails to initialize
    """
    def limit(self, *args, **kwargs):
        """Dummy limit decorator that does nothing"""
        def decorator(f):
            return f
        return decorator

    def exempt(self, f):
        """Dummy exempt decorator that does nothing"""
        return f

def get_limiter() -> Limiter:
    """
    Get the current limiter instance

    Returns:
        Current limiter instance or dummy limiter if not initialized
    """
    global limiter
    return limiter or DummyLimiter()

# Common rate limit decorators
def api_rate_limit():
    """Standard API rate limit: 100 requests per minute"""
    return get_limiter().limit("100 per minute")

def strict_rate_limit():
    """Strict rate limit: 10 requests per minute"""
    return get_limiter().limit("10 per minute")

def upload_rate_limit():
    """Upload rate limit: 5 uploads per minute"""
    return get_limiter().limit("5 per minute")

def auth_rate_limit():
    """Authentication rate limit: 5 attempts per minute"""
    return get_limiter().limit("5 per minute")
