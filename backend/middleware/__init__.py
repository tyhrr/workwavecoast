"""
Middleware Package
Authentication, validation, error handling, CORS, logging, and request processing
"""

from .auth_middleware import AuthMiddleware, jwt_required, admin_required, optional_auth
from .validation_middleware import (
    ValidationMiddleware,
    validate_json_schema,
    validate_application_form,
    validate_file_upload,
    validate_pagination,
    validate_object_id,
    validate_admin_login
)
from .error_middleware import ErrorMiddleware, handle_api_errors
from .logging_middleware import (
    LoggingMiddleware,
    log_requests,
    log_performance,
    log_user_actions,
    log_api_usage
)
from .cors_middleware import (
    CORSMiddleware,
    SecurityHeaders,
    cors_enabled,
    no_cors,
    secure_headers,
    setup_cors_and_security
)

__all__ = [
    # Core middleware classes
    'AuthMiddleware',
    'ValidationMiddleware',
    'ErrorMiddleware',
    'LoggingMiddleware',
    'CORSMiddleware',
    'SecurityHeaders',

    # Authentication decorators
    'jwt_required',
    'admin_required',
    'optional_auth',

    # Validation decorators
    'validate_json_schema',
    'validate_application_form',
    'validate_file_upload',
    'validate_pagination',
    'validate_object_id',
    'validate_admin_login',

    # Error handling
    'handle_api_errors',

    # Logging decorators
    'log_requests',
    'log_performance',
    'log_user_actions',
    'log_api_usage',

    # CORS decorators and utilities
    'cors_enabled',
    'no_cors',
    'secure_headers',
    'setup_cors_and_security'
]
