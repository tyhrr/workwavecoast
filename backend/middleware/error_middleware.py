"""
Error Handling Middleware
Centralized error handling and response formatting
"""
import logging
import traceback
from functools import wraps
from flask import request, jsonify, current_app
from typing import Dict, Any, Callable, Tuple, Union
from werkzeug.exceptions import HTTPException
from pymongo.errors import PyMongoError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class ErrorMiddleware:
    """Middleware for centralized error handling"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.error_middleware = self

        # Register error handlers
        app.register_error_handler(400, self.handle_bad_request)
        app.register_error_handler(401, self.handle_unauthorized)
        app.register_error_handler(403, self.handle_forbidden)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(405, self.handle_method_not_allowed)
        app.register_error_handler(422, self.handle_unprocessable_entity)
        app.register_error_handler(429, self.handle_rate_limit_exceeded)
        app.register_error_handler(500, self.handle_internal_server_error)
        app.register_error_handler(ValidationError, self.handle_validation_error)
        app.register_error_handler(PyMongoError, self.handle_database_error)
        app.register_error_handler(Exception, self.handle_generic_error)

    def handle_bad_request(self, error):
        """Handle 400 Bad Request errors"""
        return self._create_error_response(
            error_code=400,
            error_type='BadRequest',
            message='Bad request',
            details=str(error) if not isinstance(error, HTTPException) else error.description
        )

    def handle_unauthorized(self, error):
        """Handle 401 Unauthorized errors"""
        return self._create_error_response(
            error_code=401,
            error_type='Unauthorized',
            message='Authentication required',
            details=str(error) if not isinstance(error, HTTPException) else error.description
        )

    def handle_forbidden(self, error):
        """Handle 403 Forbidden errors"""
        return self._create_error_response(
            error_code=403,
            error_type='Forbidden',
            message='Access denied',
            details=str(error) if not isinstance(error, HTTPException) else error.description
        )

    def handle_not_found(self, error):
        """Handle 404 Not Found errors"""
        if request.path.startswith('/api/'):
            return self._create_error_response(
                error_code=404,
                error_type='NotFound',
                message='Endpoint not found',
                details=f'The requested endpoint {request.path} was not found'
            )
        else:
            # For non-API routes, return HTML or redirect
            return self._create_error_response(
                error_code=404,
                error_type='NotFound',
                message='Page not found',
                details=f'The requested page {request.path} was not found'
            )

    def handle_method_not_allowed(self, error):
        """Handle 405 Method Not Allowed errors"""
        return self._create_error_response(
            error_code=405,
            error_type='MethodNotAllowed',
            message='Method not allowed',
            details=f'Method {request.method} not allowed for {request.path}'
        )

    def handle_unprocessable_entity(self, error):
        """Handle 422 Unprocessable Entity errors"""
        return self._create_error_response(
            error_code=422,
            error_type='UnprocessableEntity',
            message='Unprocessable entity',
            details=str(error) if not isinstance(error, HTTPException) else error.description
        )

    def handle_rate_limit_exceeded(self, error):
        """Handle 429 Rate Limit Exceeded errors"""
        return self._create_error_response(
            error_code=429,
            error_type='RateLimitExceeded',
            message='Rate limit exceeded',
            details='Too many requests. Please try again later.'
        )

    def handle_internal_server_error(self, error):
        """Handle 500 Internal Server Error"""
        # Log the full error for debugging
        logger.error(f"Internal server error: {error}", exc_info=True)

        # Return generic error to client (don't expose internal details)
        return self._create_error_response(
            error_code=500,
            error_type='InternalServerError',
            message='Internal server error',
            details='An unexpected error occurred. Please try again later.'
        )

    def handle_validation_error(self, error):
        """Handle Pydantic validation errors"""
        logger.warning(f"Validation error: {error}")

        error_details = []
        if hasattr(error, 'errors'):
            for err in error.errors():
                field = err.get('loc', ['unknown'])[-1]
                message = err.get('msg', 'Invalid value')
                error_details.append(f"{field}: {message}")

        return self._create_error_response(
            error_code=422,
            error_type='ValidationError',
            message='Validation failed',
            details=error_details if error_details else [str(error)]
        )

    def handle_database_error(self, error):
        """Handle MongoDB/database errors"""
        logger.error(f"Database error: {error}", exc_info=True)

        return self._create_error_response(
            error_code=500,
            error_type='DatabaseError',
            message='Database operation failed',
            details='A database error occurred. Please try again later.'
        )

    def handle_generic_error(self, error):
        """Handle all other unhandled errors"""
        logger.error(f"Unhandled error: {error}", exc_info=True)

        # In development, include more details
        if current_app.debug:
            return self._create_error_response(
                error_code=500,
                error_type='UnhandledError',
                message=f'Unhandled error: {type(error).__name__}',
                details=str(error)
            )
        else:
            return self._create_error_response(
                error_code=500,
                error_type='InternalServerError',
                message='An unexpected error occurred',
                details='Please try again later.'
            )

    def _create_error_response(self, error_code: int, error_type: str,
                             message: str, details: Union[str, list] = None) -> Tuple[Dict[str, Any], int]:
        """Create standardized error response"""
        response = {
            'success': False,
            'error': message,
            'error_type': error_type,
            'timestamp': self._get_timestamp(),
            'path': request.path,
            'method': request.method
        }

        if details:
            response['details'] = details

        # Add request ID if available
        if hasattr(request, 'request_id'):
            response['request_id'] = request.request_id

        return jsonify(response), error_code

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


def handle_api_errors(f: Callable) -> Callable:
    """
    Decorator to handle API errors in route functions
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'error_type': 'ValidationError',
                'details': [err['msg'] for err in e.errors()] if hasattr(e, 'errors') else [str(e)]
            }), 422
        except ValueError as e:
            logger.warning(f"Value error in {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'ValueError'
            }), 400
        except KeyError as e:
            logger.warning(f"Key error in {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': f'Missing required field: {str(e)}',
                'error_type': 'KeyError'
            }), 400
        except PyMongoError as e:
            logger.error(f"Database error in {f.__name__}: {e}")
            return jsonify({
                'success': False,
                'error': 'Database operation failed',
                'error_type': 'DatabaseError'
            }), 500
        except HTTPException as e:
            # Re-raise HTTP exceptions to be handled by Flask
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'error_type': 'InternalError'
            }), 500

    return decorated_function


def handle_service_errors(f: Callable) -> Callable:
    """
    Decorator to handle service layer errors
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)

            # If service returns a dict with success/error pattern
            if isinstance(result, dict) and 'success' in result:
                if not result['success']:
                    error_code = 400
                    error_type = result.get('error_type', 'ServiceError')

                    # Map error types to HTTP status codes
                    if error_type in ['NotFoundError', 'ResourceNotFound']:
                        error_code = 404
                    elif error_type in ['AuthenticationError', 'InvalidCredentials']:
                        error_code = 401
                    elif error_type in ['AuthorizationError', 'PermissionDenied']:
                        error_code = 403
                    elif error_type in ['ValidationError', 'InvalidInput']:
                        error_code = 422
                    elif error_type in ['DuplicateError', 'ConflictError']:
                        error_code = 409
                    elif error_type in ['DatabaseError', 'InternalError']:
                        error_code = 500

                    return jsonify(result), error_code

            return result

        except Exception as e:
            logger.error(f"Service error in {f.__name__}: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Service operation failed',
                'error_type': 'ServiceError'
            }), 500

    return decorated_function


def log_errors(f: Callable) -> Callable:
    """
    Decorator to log errors without handling them
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in {f.__name__}: {str(e)}",
                extra={
                    'function': f.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs),
                    'traceback': traceback.format_exc()
                }
            )
            raise  # Re-raise the exception

    return decorated_function
