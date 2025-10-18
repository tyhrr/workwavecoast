"""
Response Utilities
Standardized response formatting and helpers
"""
from typing import Dict, Any, Optional, List, Union
from flask import jsonify, Response
import json


class APIResponse:
    """Standardized API response handler"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Dict[str, Any] = None
    ) -> tuple[Response, int]:
        """
        Create standardized success response

        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata

        Returns:
            Tuple of (response, status_code)
        """
        response_body = {
            "success": True,
            "message": message,
            "data": data
        }

        if meta:
            response_body["meta"] = meta

        return jsonify(response_body), status_code

    @staticmethod
    def error(
        message: str = "An error occurred",
        status_code: int = 400,
        error_code: str = None,
        details: Any = None
    ) -> tuple[Response, int]:
        """
        Create standardized error response

        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Custom error code
            details: Additional error details

        Returns:
            Tuple of (response, status_code)
        """
        response_body = {
            "success": False,
            "message": message,
            "error": {
                "code": error_code or f"ERROR_{status_code}",
                "details": details
            }
        }

        return jsonify(response_body), status_code

    @staticmethod
    def validation_error(
        errors: Union[Dict[str, List[str]], List[str]],
        message: str = "Validation failed"
    ) -> tuple[Response, int]:
        """
        Create standardized validation error response

        Args:
            errors: Validation errors
            message: Error message

        Returns:
            Tuple of (response, status_code)
        """
        return APIResponse.error(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"validation_errors": errors}
        )

    @staticmethod
    def paginated(
        data: List[Any],
        page: int,
        per_page: int,
        total: int,
        message: str = "Success"
    ) -> tuple[Response, int]:
        """
        Create paginated response

        Args:
            data: Paginated data
            page: Current page
            per_page: Items per page
            total: Total items
            message: Success message

        Returns:
            Tuple of (response, status_code)
        """
        total_pages = (total + per_page - 1) // per_page

        meta = {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": total_pages,
                "has_prev": page > 1,
                "has_next": page < total_pages
            }
        }

        return APIResponse.success(
            data=data,
            message=message,
            meta=meta
        )

    @staticmethod
    def created(
        data: Any = None,
        message: str = "Created successfully",
        location: str = None
    ) -> tuple[Response, int]:
        """
        Create 201 Created response

        Args:
            data: Created resource data
            message: Success message
            location: Location header value

        Returns:
            Tuple of (response, status_code)
        """
        response, status = APIResponse.success(data, message, 201)

        if location:
            response.headers['Location'] = location

        return response, status

    @staticmethod
    def no_content(message: str = "No content") -> tuple[Response, int]:
        """
        Create 204 No Content response

        Args:
            message: Response message

        Returns:
            Tuple of (response, status_code)
        """
        return jsonify({"success": True, "message": message}), 204

    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> tuple[Response, int]:
        """Create 401 Unauthorized response"""
        return APIResponse.error(message, 401, "UNAUTHORIZED")

    @staticmethod
    def forbidden(message: str = "Forbidden") -> tuple[Response, int]:
        """Create 403 Forbidden response"""
        return APIResponse.error(message, 403, "FORBIDDEN")

    @staticmethod
    def not_found(message: str = "Resource not found") -> tuple[Response, int]:
        """Create 404 Not Found response"""
        return APIResponse.error(message, 404, "NOT_FOUND")

    @staticmethod
    def conflict(message: str = "Conflict") -> tuple[Response, int]:
        """Create 409 Conflict response"""
        return APIResponse.error(message, 409, "CONFLICT")

    @staticmethod
    def server_error(message: str = "Internal server error") -> tuple[Response, int]:
        """Create 500 Internal Server Error response"""
        return APIResponse.error(message, 500, "INTERNAL_ERROR")


def format_validation_errors(errors: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Format Pydantic validation errors for API response

    Args:
        errors: Pydantic validation errors

    Returns:
        Formatted errors dictionary
    """
    formatted = {}

    if isinstance(errors, dict):
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                formatted[field] = [str(err) for err in error_list]
            else:
                formatted[field] = [str(error_list)]
    elif isinstance(errors, list):
        # Handle list of errors
        formatted['general'] = [str(err) for err in errors]
    else:
        formatted['general'] = [str(errors)]

    return formatted


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string

    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, ValueError):
        return default


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re
    import os

    # Remove directory path
    filename = os.path.basename(filename)

    # Replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove multiple dots except the last one
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts
        name = re.sub(r'\.+', '_', name)
        filename = f"{name}.{ext}"
    else:
        filename = re.sub(r'\.+', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_length = 255 - len(ext)
        filename = name[:max_name_length] + ext

    return filename


def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """
    Generate unique identifier

    Args:
        prefix: Prefix for the ID
        length: Length of random part

    Returns:
        Unique identifier string
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))

    if prefix:
        return f"{prefix}_{random_part}"
    return random_part


def format_datetime(dt, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string

    Args:
        dt: Datetime object
        format_string: Format string

    Returns:
        Formatted datetime string
    """
    if dt is None:
        return None

    try:
        return dt.strftime(format_string)
    except (AttributeError, ValueError):
        return str(dt)


def parse_datetime(date_string: str):
    """
    Parse datetime string to datetime object

    Args:
        date_string: Date string to parse

    Returns:
        Datetime object or None
    """
    from datetime import datetime

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return None


def extract_pagination_params(args: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract pagination parameters from request args

    Args:
        args: Request arguments

    Returns:
        Dictionary with page and per_page
    """
    try:
        page = int(args.get('page', 1))
        per_page = int(args.get('per_page', 20))

        # Validate ranges
        page = max(1, page)
        per_page = max(1, min(100, per_page))  # Limit to 100 items per page

        return {"page": page, "per_page": per_page}
    except (ValueError, TypeError):
        return {"page": 1, "per_page": 20}


def calculate_offset(page: int, per_page: int) -> int:
    """
    Calculate database offset for pagination

    Args:
        page: Page number (1-based)
        per_page: Items per page

    Returns:
        Database offset (0-based)
    """
    return (page - 1) * per_page
