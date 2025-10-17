"""
RBAC Middleware
Role-Based Access Control middleware for admin authentication and authorization
"""
import logging
from functools import wraps
from typing import Dict, Any, Optional, List, Callable
from flask import request, jsonify, g
from services.admin_service import AdminService
from services.jwt_service import JWTService

class RBACMiddleware:
    """Role-Based Access Control middleware"""

    def __init__(self, admin_service: AdminService, jwt_service: JWTService, logger: Optional[logging.Logger] = None):
        self.admin_service = admin_service
        self.jwt_service = jwt_service
        self.logger = logger or logging.getLogger(__name__)

    def extract_token_from_request(self) -> Optional[str]:
        """Extract JWT token from request headers"""
        try:
            # Check Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                return auth_header.split(' ')[1]

            # Check X-Access-Token header
            token = request.headers.get('X-Access-Token')
            if token:
                return token

            # Check query parameter (less secure, but useful for development)
            token = request.args.get('access_token')
            if token:
                return token

            return None

        except Exception as e:
            self.logger.error(f"Error extracting token: {e}")
            return None

    def validate_admin_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate admin token and return admin info"""
        try:
            # Verify token using admin service
            verification_result = self.admin_service.verify_admin_token(token)
            if not verification_result['success']:
                self.logger.warning(f"Token validation failed: {verification_result.get('message', 'Unknown error')}")
                return None

            return verification_result['data']

        except Exception as e:
            self.logger.error(f"Error validating admin token: {e}")
            return None

    def require_admin_auth(self, f: Callable) -> Callable:
        """Decorator to require admin authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Extract token
                token = self.extract_token_from_request()
                if not token:
                    return jsonify({
                        'success': False,
                        'message': 'Authentication token required',
                        'error_type': 'MissingToken'
                    }), 401

                # Validate token
                admin_info = self.validate_admin_token(token)
                if not admin_info:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid or expired token',
                        'error_type': 'InvalidToken'
                    }), 401

                # Store admin info in Flask's g object for use in route handlers
                g.current_admin = admin_info
                g.current_admin_id = admin_info['admin_id']
                g.current_admin_role = admin_info['role']
                g.current_admin_permissions = admin_info['permissions']

                return f(*args, **kwargs)

            except Exception as e:
                self.logger.error(f"Authentication error: {e}")
                return jsonify({
                    'success': False,
                    'message': 'Authentication failed',
                    'error_type': 'AuthenticationError'
                }), 500

        return decorated_function

    def require_permission(self, required_permission: str) -> Callable:
        """Decorator to require specific permission"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Check if admin is authenticated
                    if not hasattr(g, 'current_admin') or not g.current_admin:
                        return jsonify({
                            'success': False,
                            'message': 'Authentication required',
                            'error_type': 'NotAuthenticated'
                        }), 401

                    # Check permission
                    admin_role = g.current_admin_role
                    has_permission = self.admin_service.check_admin_permission(admin_role, required_permission)

                    if not has_permission:
                        return jsonify({
                            'success': False,
                            'message': f'Permission denied. Required: {required_permission}',
                            'error_type': 'InsufficientPermissions',
                            'required_permission': required_permission,
                            'user_role': admin_role
                        }), 403

                    return f(*args, **kwargs)

                except Exception as e:
                    self.logger.error(f"Permission check error: {e}")
                    return jsonify({
                        'success': False,
                        'message': 'Permission check failed',
                        'error_type': 'PermissionError'
                    }), 500

            return decorated_function
        return decorator

    def require_role(self, required_roles: List[str]) -> Callable:
        """Decorator to require specific role(s)"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Check if admin is authenticated
                    if not hasattr(g, 'current_admin') or not g.current_admin:
                        return jsonify({
                            'success': False,
                            'message': 'Authentication required',
                            'error_type': 'NotAuthenticated'
                        }), 401

                    # Check role
                    admin_role = g.current_admin_role
                    if admin_role not in required_roles:
                        return jsonify({
                            'success': False,
                            'message': f'Role access denied. Required roles: {", ".join(required_roles)}',
                            'error_type': 'InsufficientRole',
                            'required_roles': required_roles,
                            'user_role': admin_role
                        }), 403

                    return f(*args, **kwargs)

                except Exception as e:
                    self.logger.error(f"Role check error: {e}")
                    return jsonify({
                        'success': False,
                        'message': 'Role check failed',
                        'error_type': 'RoleError'
                    }), 500

            return decorated_function
        return decorator

    def require_super_admin(self, f: Callable) -> Callable:
        """Decorator to require super admin role"""
        return self.require_role(['super_admin'])(f)

    def optional_admin_auth(self, f: Callable) -> Callable:
        """Decorator for optional admin authentication (useful for public endpoints that can show extra info for admins)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Extract token (optional)
                token = self.extract_token_from_request()
                if token:
                    # Try to validate token
                    admin_info = self.validate_admin_token(token)
                    if admin_info:
                        g.current_admin = admin_info
                        g.current_admin_id = admin_info['admin_id']
                        g.current_admin_role = admin_info['role']
                        g.current_admin_permissions = admin_info['permissions']
                    else:
                        g.current_admin = None
                else:
                    g.current_admin = None

                return f(*args, **kwargs)

            except Exception as e:
                self.logger.error(f"Optional authentication error: {e}")
                g.current_admin = None
                return f(*args, **kwargs)

        return decorated_function

    def admin_or_self(self, f: Callable) -> Callable:
        """Decorator to allow access if user is admin or accessing their own data"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check if admin is authenticated
                if not hasattr(g, 'current_admin') or not g.current_admin:
                    return jsonify({
                        'success': False,
                        'message': 'Authentication required',
                        'error_type': 'NotAuthenticated'
                    }), 401

                # Get target admin ID from route parameters or request body
                target_admin_id = kwargs.get('admin_id') or request.json.get('admin_id') if request.json else None
                current_admin_id = g.current_admin_id

                # Allow if current admin is the target admin or has admin permissions
                is_self = target_admin_id == current_admin_id
                is_admin = self.admin_service.check_admin_permission(g.current_admin_role, 'manage_admins')

                if not (is_self or is_admin):
                    return jsonify({
                        'success': False,
                        'message': 'Access denied. You can only access your own data or need admin permissions.',
                        'error_type': 'AccessDenied'
                    }), 403

                return f(*args, **kwargs)

            except Exception as e:
                self.logger.error(f"Admin or self check error: {e}")
                return jsonify({
                    'success': False,
                    'message': 'Access check failed',
                    'error_type': 'AccessError'
                }), 500

        return decorated_function

    def log_admin_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log admin action for audit purposes"""
        try:
            if hasattr(g, 'current_admin') and g.current_admin:
                admin_info = g.current_admin
                log_entry = {
                    'timestamp': logging.Formatter().formatTime(logging.LogRecord(
                        name='audit', level=logging.INFO, pathname='', lineno=0,
                        msg='', args=(), exc_info=None
                    )),
                    'admin_id': admin_info['admin_id'],
                    'username': admin_info['username'],
                    'role': admin_info['role'],
                    'action': action,
                    'details': details or {},
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'Unknown')
                }

                self.logger.info(f"AUDIT: {log_entry}")
                # In production, also store in database audit log

        except Exception as e:
            self.logger.error(f"Error logging admin action: {e}")

# Global RBAC middleware instance (will be initialized in app.py)
rbac_middleware = None

def init_rbac_middleware(admin_service: AdminService, jwt_service: JWTService, logger: Optional[logging.Logger] = None):
    """Initialize global RBAC middleware"""
    global rbac_middleware
    rbac_middleware = RBACMiddleware(admin_service, jwt_service, logger)
    return rbac_middleware

# Decorator functions for easy import
def require_admin_auth(f: Callable) -> Callable:
    """Require admin authentication"""
    if rbac_middleware is None:
        raise RuntimeError("RBAC middleware not initialized")
    return rbac_middleware.require_admin_auth(f)

def require_permission(permission: str) -> Callable:
    """Require specific permission"""
    if rbac_middleware is None:
        raise RuntimeError("RBAC middleware not initialized")
    return rbac_middleware.require_permission(permission)

def require_role(roles: List[str]) -> Callable:
    """Require specific role(s)"""
    if rbac_middleware is None:
        raise RuntimeError("RBAC middleware not initialized")
    return rbac_middleware.require_role(roles)

def require_super_admin(f: Callable) -> Callable:
    """Require super admin role"""
    if rbac_middleware is None:
        raise RuntimeError("RBAC middleware not initialized")
    return rbac_middleware.require_super_admin(f)

def optional_admin_auth(f: Callable) -> Callable:
    """Optional admin authentication"""
    if rbac_middleware is None:
        raise RuntimeError("RBAC middleware not initialized")
    return rbac_middleware.optional_admin_auth(f)

def admin_or_self(f: Callable) -> Callable:
    """Admin or self access only"""
    if rbac_middleware is None:
        raise RuntimeError("RBAC middleware not initialized")
    return rbac_middleware.admin_or_self(f)
