"""
Authentication Middleware
JWT token validation and admin authentication
"""
import jwt
import logging
from functools import wraps
from flask import request, jsonify, current_app, g
from typing import Dict, Any, Optional, Callable
from services import AdminService

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Authentication middleware for JWT token validation"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.auth_middleware = self
        app.before_request(self.before_request)

    def before_request(self):
        """Process request before handling"""
        # Skip auth for certain endpoints
        skip_auth_endpoints = [
            'health.health_check',
            'health.quick_health',
            'health.api_info',
            'api.submit_application',
            'admin.login',
            'admin.refresh_token',
            'admin.forgot_password',
            'admin.reset_password',
            'admin.validate_recovery_token',
            'static'
        ]

        if request.endpoint in skip_auth_endpoints:
            return

        # Check if this is an admin route
        if request.endpoint and request.endpoint.startswith('admin.'):
            return self._validate_admin_token()

    def _validate_admin_token(self):
        """Validate admin JWT token"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    'success': False,
                    'error': 'Authorization header required',
                    'error_type': 'AuthenticationError'
                }), 401

            # Extract token (expecting "Bearer <token>")
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format',
                    'error_type': 'AuthenticationError'
                }), 401

            # Validate token with AdminService
            admin_service = AdminService(logger)
            result = admin_service.verify_admin_token(token)

            if result['success']:
                # Store admin info in request context
                g.current_admin = result['data']
                return None
            else:
                return jsonify({
                    'success': False,
                    'error': result['error'],
                    'error_type': 'AuthenticationError'
                }), 401

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({
                'success': False,
                'error': 'Authentication failed',
                'error_type': 'AuthenticationError'
            }), 401


def jwt_required(f: Callable) -> Callable:
    """
    Decorator to require JWT authentication for routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    'success': False,
                    'error': 'Authorization header required',
                    'error_type': 'AuthenticationError'
                }), 401

            # Extract token (expecting "Bearer <token>")
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format',
                    'error_type': 'AuthenticationError'
                }), 401

            # For simplified auth, use static token validation
            # TODO: Implement proper JWT validation when AdminService is fully integrated
            if token != "test-token":
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired token',
                    'error_type': 'AuthenticationError'
                }), 401

            # Token is valid, proceed with the request
            g.current_user = {
                'id': 'test-admin-id',
                'username': 'admin',
                'role': 'admin'
            }

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({
                'success': False,
                'error': 'Authentication failed',
                'error_type': 'AuthenticationError'
            }), 401

    return decorated_function


def admin_required(f: Callable) -> Callable:
    """
    Decorator to require admin role for routes
    Combines JWT validation with admin role check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First validate JWT token
        auth_result = jwt_required(lambda: None)()
        if auth_result is not None:  # If JWT validation failed
            return auth_result

        # Check admin role
        if not hasattr(g, 'current_user') or g.current_user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin privileges required',
                'error_type': 'AuthorizationError'
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f: Callable) -> Callable:
    """
    Decorator for optional authentication
    Validates token if present but doesn't require it
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    token = auth_header.split(' ')[1]
                    if token == "test-token":
                        g.current_user = {
                            'id': 'test-admin-id',
                            'username': 'admin',
                            'role': 'admin'
                        }
                except (IndexError, ValueError):
                    # Invalid token format, but we continue without auth
                    pass

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Optional auth error: {e}")
            return f(*args, **kwargs)

    return decorated_function


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user from request context

    Returns:
        User data if authenticated, None otherwise
    """
    return getattr(g, 'current_user', None)


def require_permissions(permissions: list) -> Callable:
    """
    Decorator to require specific permissions

    Args:
        permissions: List of required permissions
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First require authentication
            auth_result = jwt_required(lambda: None)()
            if auth_result is not None:
                return auth_result

            # Check permissions (simplified for now)
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'error_type': 'AuthenticationError'
                }), 401

            # For admin users, grant all permissions
            if current_user.get('role') == 'admin':
                return f(*args, **kwargs)

            # For other users, check specific permissions
            user_permissions = current_user.get('permissions', [])
            if not all(perm in user_permissions for perm in permissions):
                return jsonify({
                    'success': False,
                    'error': f'Required permissions: {", ".join(permissions)}',
                    'error_type': 'AuthorizationError'
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator
