"""
CORS Middleware
Cross-Origin Resource Sharing configuration and middleware
"""
import logging
from functools import wraps
from flask import request, current_app, g
from typing import Dict, List, Optional, Union, Callable

logger = logging.getLogger(__name__)


class CORSMiddleware:
    """Middleware for CORS handling"""

    def __init__(self, app=None, **kwargs):
        self.app = app

        # Default CORS configuration
        self.config = {
            'origins': kwargs.get('origins', ['*']),
            'methods': kwargs.get('methods', ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']),
            'allow_headers': kwargs.get('allow_headers', [
                'Content-Type',
                'Authorization',
                'X-Requested-With',
                'Accept',
                'Origin',
                'X-Request-ID'
            ]),
            'expose_headers': kwargs.get('expose_headers', [
                'X-Request-ID',
                'X-Total-Count',
                'X-Page-Count'
            ]),
            'supports_credentials': kwargs.get('supports_credentials', True),
            'max_age': kwargs.get('max_age', 86400),  # 24 hours
            'vary_header': kwargs.get('vary_header', True)
        }

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.cors_middleware = self

        # Apply CORS to all routes
        app.after_request(self.after_request)

        # Handle preflight OPTIONS requests
        app.before_request(self.before_request)

    def before_request(self):
        """Handle preflight OPTIONS requests"""
        if request.method == 'OPTIONS':
            # This is a preflight request
            response = current_app.make_default_options_response()
            return self._apply_cors_headers(response)

    def after_request(self, response):
        """Apply CORS headers to all responses"""
        return self._apply_cors_headers(response)

    def _apply_cors_headers(self, response):
        """Apply CORS headers to response"""
        origin = request.headers.get('Origin')

        # Handle origin
        if self._is_origin_allowed(origin):
            response.headers['Access-Control-Allow-Origin'] = origin
        elif '*' in self.config['origins']:
            response.headers['Access-Control-Allow-Origin'] = '*'

        # Methods
        if self.config['methods']:
            response.headers['Access-Control-Allow-Methods'] = ', '.join(self.config['methods'])

        # Headers
        if self.config['allow_headers']:
            response.headers['Access-Control-Allow-Headers'] = ', '.join(self.config['allow_headers'])

        # Expose headers
        if self.config['expose_headers']:
            response.headers['Access-Control-Expose-Headers'] = ', '.join(self.config['expose_headers'])

        # Credentials
        if self.config['supports_credentials']:
            response.headers['Access-Control-Allow-Credentials'] = 'true'

        # Max age for preflight cache
        if request.method == 'OPTIONS' and self.config['max_age']:
            response.headers['Access-Control-Max-Age'] = str(self.config['max_age'])

        # Vary header
        if self.config['vary_header']:
            vary = response.headers.get('Vary', '')
            if vary:
                vary += ', Origin'
            else:
                vary = 'Origin'
            response.headers['Vary'] = vary

        return response

    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if origin is allowed"""
        if not origin:
            return False

        if '*' in self.config['origins']:
            return True

        return origin in self.config['origins']

    def update_config(self, **kwargs):
        """Update CORS configuration"""
        self.config.update(kwargs)
        logger.info(f"CORS configuration updated: {kwargs}")


def cors_enabled(
    origins: Union[str, List[str]] = None,
    methods: List[str] = None,
    allow_headers: List[str] = None,
    expose_headers: List[str] = None,
    supports_credentials: bool = None,
    max_age: int = None
) -> Callable:
    """
    Decorator to enable CORS for specific routes with custom configuration

    Args:
        origins: Allowed origins (string or list)
        methods: Allowed methods
        allow_headers: Allowed request headers
        expose_headers: Headers to expose to client
        supports_credentials: Whether to support credentials
        max_age: Max age for preflight cache
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Store custom CORS config in g for this request
            g.custom_cors = {
                'origins': [origins] if isinstance(origins, str) else origins,
                'methods': methods,
                'allow_headers': allow_headers,
                'expose_headers': expose_headers,
                'supports_credentials': supports_credentials,
                'max_age': max_age
            }

            # Remove None values
            g.custom_cors = {k: v for k, v in g.custom_cors.items() if v is not None}

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def no_cors(f: Callable) -> Callable:
    """
    Decorator to disable CORS for specific routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.disable_cors = True
        return f(*args, **kwargs)

    return decorated_function


class SecurityHeaders:
    """Additional security headers middleware"""

    def __init__(self, app=None, **kwargs):
        self.app = app

        # Default security headers
        self.config = {
            'content_security_policy': kwargs.get('content_security_policy',
                "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:"),
            'x_content_type_options': kwargs.get('x_content_type_options', 'nosniff'),
            'x_frame_options': kwargs.get('x_frame_options', 'DENY'),
            'x_xss_protection': kwargs.get('x_xss_protection', '1; mode=block'),
            'strict_transport_security': kwargs.get('strict_transport_security',
                'max-age=31536000; includeSubDomains'),
            'referrer_policy': kwargs.get('referrer_policy', 'strict-origin-when-cross-origin'),
            'permissions_policy': kwargs.get('permissions_policy',
                'geolocation=(), microphone=(), camera=()'),
            'feature_policy': kwargs.get('feature_policy',
                "geolocation 'none'; microphone 'none'; camera 'none'")
        }

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize security headers with Flask app"""
        app.security_headers = self
        app.after_request(self.after_request)

    def after_request(self, response):
        """Apply security headers to response"""
        # Skip security headers for development CORS preflight
        if request.method == 'OPTIONS':
            return response

        # Content Security Policy
        if self.config['content_security_policy']:
            response.headers['Content-Security-Policy'] = self.config['content_security_policy']

        # X-Content-Type-Options
        if self.config['x_content_type_options']:
            response.headers['X-Content-Type-Options'] = self.config['x_content_type_options']

        # X-Frame-Options
        if self.config['x_frame_options']:
            response.headers['X-Frame-Options'] = self.config['x_frame_options']

        # X-XSS-Protection
        if self.config['x_xss_protection']:
            response.headers['X-XSS-Protection'] = self.config['x_xss_protection']

        # Strict-Transport-Security (only over HTTPS)
        if request.is_secure and self.config['strict_transport_security']:
            response.headers['Strict-Transport-Security'] = self.config['strict_transport_security']

        # Referrer-Policy
        if self.config['referrer_policy']:
            response.headers['Referrer-Policy'] = self.config['referrer_policy']

        # Permissions-Policy
        if self.config['permissions_policy']:
            response.headers['Permissions-Policy'] = self.config['permissions_policy']

        # Feature-Policy (deprecated but still supported)
        if self.config['feature_policy']:
            response.headers['Feature-Policy'] = self.config['feature_policy']

        return response


def secure_headers(
    csp: str = None,
    frame_options: str = None,
    content_type_options: str = None
) -> Callable:
    """
    Decorator to apply custom security headers to specific routes

    Args:
        csp: Custom Content Security Policy
        frame_options: Custom X-Frame-Options
        content_type_options: Custom X-Content-Type-Options
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)

            # Apply custom headers if provided
            if csp:
                response.headers['Content-Security-Policy'] = csp

            if frame_options:
                response.headers['X-Frame-Options'] = frame_options

            if content_type_options:
                response.headers['X-Content-Type-Options'] = content_type_options

            return response

        return decorated_function
    return decorator


def setup_cors_and_security(app, cors_config: Dict = None, security_config: Dict = None):
    """
    Convenient function to set up both CORS and security headers

    Args:
        app: Flask application
        cors_config: CORS configuration dictionary
        security_config: Security headers configuration dictionary
    """
    # Default configurations
    default_cors = {
        'origins': ['http://localhost:3000', 'http://127.0.0.1:3000', 'https://workwavecoast.com'],
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        'allow_headers': [
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'Accept',
            'Origin',
            'X-Request-ID'
        ],
        'supports_credentials': True
    }

    default_security = {
        'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:",
        'x_frame_options': 'SAMEORIGIN',  # Less restrictive for embedded content
        'x_content_type_options': 'nosniff'
    }

    # Merge with provided configs
    final_cors_config = {**default_cors, **(cors_config or {})}
    final_security_config = {**default_security, **(security_config or {})}

    # Initialize middleware
    CORSMiddleware(app, **final_cors_config)
    SecurityHeaders(app, **final_security_config)

    logger.info("CORS and Security headers configured")
    logger.info(f"CORS origins: {final_cors_config['origins']}")
    logger.info(f"Security CSP: {final_security_config['content_security_policy']}")
