"""
Utils Package
Utility functions, decorators, and helper modules
"""

# Legacy decorators (kept for compatibility)
from .decorators import require_admin_auth, validate_json, handle_errors

# Core utilities
from .logging_config import setup_logging
from .rate_limiter import init_rate_limiter
from .country_flags import get_country_flag

# New FASE 6 utilities
from .response_helpers import (
    APIResponse,
    format_validation_errors,
    safe_json_loads,
    sanitize_filename,
    generate_unique_id,
    format_datetime,
    parse_datetime,
    extract_pagination_params,
    calculate_offset
)
from .validation_helpers import (
    ValidationUtils,
    DataCleaner,
    validate_required_fields,
    validate_field_lengths,
    merge_validation_errors
)
from .security_helpers import (
    SecurityUtils,
    RateLimitUtils,
    generate_session_id,
    validate_input_length,
    sanitize_filename_for_security,
    check_file_signature
)

__all__ = [
    # Legacy functions
    'require_admin_auth',
    'validate_json',
    'handle_errors',
    'setup_logging',
    'init_rate_limiter',
    'get_country_flag',

    # Response utilities
    'APIResponse',
    'format_validation_errors',
    'safe_json_loads',
    'sanitize_filename',
    'generate_unique_id',
    'format_datetime',
    'parse_datetime',
    'extract_pagination_params',
    'calculate_offset',

    # Validation utilities
    'ValidationUtils',
    'DataCleaner',
    'validate_required_fields',
    'validate_field_lengths',
    'merge_validation_errors',

    # Security utilities
    'SecurityUtils',
    'RateLimitUtils',
    'generate_session_id',
    'validate_input_length',
    'sanitize_filename_for_security',
    'check_file_signature'
]
