"""
Validation Middleware
Request validation and JSON schema validation
"""
import logging
from functools import wraps
from flask import request, jsonify
from typing import Dict, Any, Optional, Callable, Union
from pydantic import BaseModel, ValidationError
from schemas.validators import validate_application_data, validate_admin_credentials, sanitize_input

logger = logging.getLogger(__name__)


class ValidationMiddleware:
    """Middleware for request validation"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.validation_middleware = self
        app.before_request(self.before_request)

    def before_request(self):
        """Validate request before processing"""
        # Skip validation for certain endpoints
        skip_validation = [
            'static',
            'health.health_check',
            'health.quick_health'
        ]

        if request.endpoint in skip_validation:
            return

        # Validate content type for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.endpoint not in ['api.submit_application']:  # Form data endpoints
                if not request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'Content-Type must be application/json',
                        'error_type': 'ValidationError'
                    }), 400

        return None


def validate_json_schema(schema_class: BaseModel = None, required_fields: list = None) -> Callable:
    """
    Decorator to validate JSON request data against a Pydantic schema

    Args:
        schema_class: Pydantic model class for validation
        required_fields: List of required field names (if no schema provided)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
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

                # Sanitize input data
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            data[key] = sanitize_input(value)

                # Validate with Pydantic schema if provided
                if schema_class:
                    try:
                        validated_data = schema_class(**data)
                        request.validated_data = validated_data.dict()
                    except ValidationError as e:
                        return jsonify({
                            'success': False,
                            'error': f'Validation error: {str(e)}',
                            'error_type': 'ValidationError',
                            'details': e.errors()
                        }), 400

                # Check required fields if specified
                elif required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in data or data[field] is None or data[field] == '':
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


def validate_application_form(f: Callable) -> Callable:
    """
    Decorator specifically for application form validation
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get form data
            if request.method == 'POST':
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()

                # Validate application data
                is_valid, errors = validate_application_data(data)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': f'Validation failed: {"; ".join(errors)}',
                        'error_type': 'ValidationError',
                        'details': errors
                    }), 400

                # Store validated data
                request.validated_data = data

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Application validation error: {e}")
            return jsonify({
                'success': False,
                'error': 'Application validation failed',
                'error_type': 'ValidationError'
            }), 400

    return decorated_function


def validate_admin_login(f: Callable) -> Callable:
    """
    Decorator for admin login validation
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Request must be JSON',
                    'error_type': 'ValidationError'
                }), 400

            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON data',
                    'error_type': 'ValidationError'
                }), 400

            username = data.get('username', '').strip()
            password = data.get('password', '')

            # Validate credentials format
            is_valid, errors = validate_admin_credentials(username, password)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': f'Validation failed: {"; ".join(errors)}',
                    'error_type': 'ValidationError',
                    'details': errors
                }), 400

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Admin login validation error: {e}")
            return jsonify({
                'success': False,
                'error': 'Login validation failed',
                'error_type': 'ValidationError'
            }), 400

    return decorated_function


def validate_pagination(f: Callable) -> Callable:
    """
    Decorator to validate pagination parameters
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Validate pagination bounds
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 10

            # Store validated pagination
            request.pagination = {
                'page': page,
                'per_page': per_page
            }

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Pagination validation error: {e}")
            return jsonify({
                'success': False,
                'error': 'Invalid pagination parameters',
                'error_type': 'ValidationError'
            }), 400

    return decorated_function


def validate_file_upload(allowed_extensions: list = None, max_size: int = 10485760) -> Callable:
    """
    Decorator to validate file uploads

    Args:
        allowed_extensions: List of allowed file extensions
        max_size: Maximum file size in bytes (default 10MB)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if 'file' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': 'No file provided',
                        'error_type': 'ValidationError'
                    }), 400

                file = request.files['file']
                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'error': 'No file selected',
                        'error_type': 'ValidationError'
                    }), 400

                # Check file extension
                if allowed_extensions:
                    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
                    if file_extension not in allowed_extensions:
                        return jsonify({
                            'success': False,
                            'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}',
                            'error_type': 'ValidationError'
                        }), 400

                # Check file size (approximate)
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning

                if file_size > max_size:
                    return jsonify({
                        'success': False,
                        'error': f'File too large. Maximum size: {max_size // 1048576}MB',
                        'error_type': 'ValidationError'
                    }), 400

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"File validation error: {e}")
                return jsonify({
                    'success': False,
                    'error': 'File validation failed',
                    'error_type': 'ValidationError'
                }), 400

        return decorated_function
    return decorator


def validate_object_id(param_name: str = 'id') -> Callable:
    """
    Decorator to validate MongoDB ObjectId parameters

    Args:
        param_name: Name of the URL parameter containing the ObjectId
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from bson import ObjectId

                object_id = kwargs.get(param_name)
                if not object_id:
                    return jsonify({
                        'success': False,
                        'error': f'Missing {param_name} parameter',
                        'error_type': 'ValidationError'
                    }), 400

                # Validate ObjectId format
                if not ObjectId.is_valid(object_id):
                    return jsonify({
                        'success': False,
                        'error': f'Invalid {param_name} format',
                        'error_type': 'ValidationError'
                    }), 400

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"ObjectId validation error: {e}")
                return jsonify({
                    'success': False,
                    'error': 'ID validation failed',
                    'error_type': 'ValidationError'
                }), 400

        return decorated_function
    return decorator
