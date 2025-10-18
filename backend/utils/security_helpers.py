"""
Security Utilities
Security-related helper functions
"""
import hashlib
import secrets
import string
import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import re


class SecurityUtils:
    """Collection of security utility functions"""

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate cryptographically secure random token

        Args:
            length: Length of the token

        Returns:
            Secure random token
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_api_key(prefix: str = "ww", length: int = 24) -> str:
        """
        Generate API key with prefix

        Args:
            prefix: Prefix for the API key
            length: Length of random part

        Returns:
            API key string
        """
        random_part = SecurityUtils.generate_secure_token(length)
        return f"{prefix}_{random_part}"

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify password against hash

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """
        Generate random salt

        Args:
            length: Length of salt

        Returns:
            Random salt string
        """
        return secrets.token_hex(length)

    @staticmethod
    def hash_string(text: str, salt: str = "") -> str:
        """
        Hash string with optional salt

        Args:
            text: Text to hash
            salt: Optional salt

        Returns:
            SHA-256 hash
        """
        combined = text + salt
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    @staticmethod
    def is_strong_password(password: str) -> Dict[str, bool]:
        """
        Check password strength

        Args:
            password: Password to check

        Returns:
            Dictionary with strength criteria results
        """
        if not password:
            return {
                'length': False,
                'uppercase': False,
                'lowercase': False,
                'digits': False,
                'special': False,
                'no_common': False,
                'is_strong': False
            }

        criteria = {
            'length': len(password) >= 8,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'digits': bool(re.search(r'\d', password)),
            'special': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password)),
            'no_common': password.lower() not in [
                'password', '123456', 'password123', 'admin', 'qwerty',
                'letmein', 'welcome', 'monkey', '1234567890'
            ]
        }

        criteria['is_strong'] = all(criteria.values())
        return criteria

    @staticmethod
    def sanitize_html_input(text: str) -> str:
        """
        Basic HTML sanitization

        Args:
            text: Text that might contain HTML

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Replace HTML entities
        html_entities = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;',
            '&': '&amp;'  # This should be last
        }

        sanitized = text
        for char, entity in html_entities.items():
            if char != '&':  # Don't double-escape &
                sanitized = sanitized.replace(char, entity)

        # Handle & last to avoid double-escaping
        sanitized = re.sub(r'&(?!(?:amp|lt|gt|quot|#x27|#x2F);)', '&amp;', sanitized)

        return sanitized

    @staticmethod
    def validate_csrf_token(token: str, session_token: str) -> bool:
        """
        Validate CSRF token

        Args:
            token: Token from request
            session_token: Token from session

        Returns:
            True if tokens match
        """
        if not token or not session_token:
            return False

        return secrets.compare_digest(token, session_token)

    @staticmethod
    def generate_csrf_token() -> str:
        """
        Generate CSRF token

        Returns:
            CSRF token string
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", show_last: int = 4) -> str:
        """
        Mask sensitive data (emails, phone numbers, etc.)

        Args:
            data: Sensitive data to mask
            mask_char: Character to use for masking
            show_last: Number of characters to show at the end

        Returns:
            Masked string
        """
        if not data or len(data) <= show_last:
            return mask_char * len(data) if data else ""

        visible_part = data[-show_last:] if show_last > 0 else ""
        masked_length = len(data) - show_last
        masked_part = mask_char * min(masked_length, 8)  # Limit mask length

        return masked_part + visible_part

    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: list = None) -> bool:
        """
        Check if redirect URL is safe (no open redirect)

        Args:
            url: URL to check
            allowed_hosts: List of allowed host names

        Returns:
            True if URL is safe for redirect
        """
        if not url:
            return False

        # Relative URLs are generally safe
        if url.startswith('/') and not url.startswith('//'):
            return True

        # Check against allowed hosts
        if allowed_hosts:
            from urllib.parse import urlparse
            try:
                parsed = urlparse(url)
                return parsed.hostname in allowed_hosts
            except (ValueError, AttributeError):
                return False

        # If no allowed hosts specified, only allow relative URLs
        return False


class RateLimitUtils:
    """Rate limiting utilities"""

    @staticmethod
    def generate_rate_limit_key(identifier: str, endpoint: str = "") -> str:
        """
        Generate key for rate limiting

        Args:
            identifier: User identifier (IP, user ID, etc.)
            endpoint: Optional endpoint identifier

        Returns:
            Rate limit key
        """
        if endpoint:
            return f"rate_limit:{endpoint}:{identifier}"
        return f"rate_limit:{identifier}"

    @staticmethod
    def calculate_reset_time(window_seconds: int) -> datetime:
        """
        Calculate when rate limit resets

        Args:
            window_seconds: Rate limit window in seconds

        Returns:
            Reset datetime
        """
        return datetime.utcnow() + timedelta(seconds=window_seconds)


def generate_session_id() -> str:
    """Generate secure session ID"""
    return SecurityUtils.generate_secure_token(48)


def validate_input_length(text: str, max_length: int = 1000) -> bool:
    """
    Validate input length to prevent DoS

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        True if length is within limit
    """
    return len(text or "") <= max_length


def sanitize_filename_for_security(filename: str) -> str:
    """
    Sanitize filename for security (remove dangerous patterns)

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"

    # Remove directory traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')

    # Remove null bytes and control characters
    filename = ''.join(c for c in filename if ord(c) >= 32)

    # Replace dangerous characters
    dangerous_chars = '<>:"|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Ensure filename is not empty
    if not filename.strip():
        filename = "sanitized_file"

    return filename.strip()


def check_file_signature(file_content: bytes, expected_extensions: list) -> bool:
    """
    Check file signature (magic bytes) to verify file type

    Args:
        file_content: First few bytes of the file
        expected_extensions: List of expected file extensions

    Returns:
        True if file signature matches expected type
    """
    if not file_content or not expected_extensions:
        return False

    # Common file signatures
    signatures = {
        'pdf': [b'%PDF'],
        'jpg': [b'\xFF\xD8\xFF'],
        'jpeg': [b'\xFF\xD8\xFF'],
        'png': [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'],
        'gif': [b'GIF87a', b'GIF89a'],
        'zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
        'docx': [b'PK\x03\x04'],  # DOCX is a ZIP file
        'xlsx': [b'PK\x03\x04'],  # XLSX is a ZIP file
        'txt': [],  # Text files don't have reliable signatures
        'csv': []   # CSV files don't have reliable signatures
    }

    for ext in expected_extensions:
        ext_lower = ext.lower().lstrip('.')
        if ext_lower in signatures:
            expected_sigs = signatures[ext_lower]
            if not expected_sigs:  # No signature check for text files
                return True

            for sig in expected_sigs:
                if file_content.startswith(sig):
                    return True

    return False
