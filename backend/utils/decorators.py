"""
Decorators and Authentication Utilities
"""
import functools
import jwt
from flask import request, jsonify, current_app
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

def require_admin_auth(f: Callable) -> Callable:
    """
    Decorator to require admin authentication for routes
    """
    @functools.wraps(f)
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

            # For now, use simplified token validation
            # TODO: Implement proper JWT validation with AdminService
            if token != "test-token":
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired token',
                    'error_type': 'AuthenticationError'
                }), 401

            # Token is valid, proceed with the request
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({
                'success': False,
                'error': 'Authentication failed',
                'error_type': 'AuthenticationError'
            }), 401

    return decorated_function

def validate_json(required_fields: list = None) -> Callable:
    """
    Decorator to validate JSON request data

    Args:
        required_fields: List of required field names
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check if request has JSON data
                if not request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'Request must be JSON',
                        'error_type': 'ValidationError'
                    }), 400

                data = request.get_json()
                if data is None:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid JSON data',
                        'error_type': 'ValidationError'
                    }), 400

                # Check required fields
                if required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in data or data[field] is None:
                            missing_fields.append(field)

                    if missing_fields:
                        return jsonify({
                            'success': False,
                            'error': f'Missing required fields: {", ".join(missing_fields)}',
                            'error_type': 'ValidationError'
                        }), 400

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"Validation error: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Validation failed',
                    'error_type': 'ValidationError'
                }), 400

        return decorated_function
    return decorator

def handle_errors(f: Callable) -> Callable:
    """
    Decorator to handle common errors in route functions
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Value error in {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'ValueError'
            }), 400
        except KeyError as e:
            logger.error(f"Key error in {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': f'Missing key: {str(e)}',
                'error_type': 'KeyError'
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'error_type': 'InternalError'
            }), 500

    return decorated_function

def rate_limit_key() -> str:
    """
    Generate rate limit key based on client IP
    """
    return request.remote_addr or 'unknown'
