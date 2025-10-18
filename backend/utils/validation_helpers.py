"""
Data Validation Utilities
Additional validation helpers and data processing
"""
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import mimetypes
import os


class ValidationUtils:
    """Collection of validation utility functions"""

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate email address format

        Args:
            email: Email address to validate

        Returns:
            True if valid email format
        """
        if not email or not isinstance(email, str):
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None

    @staticmethod
    def is_valid_phone(phone: str, country_code: str = None) -> bool:
        """
        Validate phone number format

        Args:
            phone: Phone number to validate
            country_code: Optional country code for specific validation

        Returns:
            True if valid phone format
        """
        if not phone or not isinstance(phone, str):
            return False

        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)

        # Basic validation: 7-15 digits
        if len(digits_only) < 7 or len(digits_only) > 15:
            return False

        # More specific validation for common formats
        patterns = [
            r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',  # US/CA
            r'^\+?[1-9]\d{6,14}$',  # International
            r'^[0-9]{7,15}$'  # Simple digits
        ]

        return any(re.match(pattern, phone.strip()) for pattern in patterns)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format

        Args:
            url: URL to validate

        Returns:
            True if valid URL format
        """
        if not url or not isinstance(url, str):
            return False

        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return re.match(pattern, url.strip()) is not None

    @staticmethod
    def is_valid_date(date_string: str) -> bool:
        """
        Validate date string format

        Args:
            date_string: Date string to validate

        Returns:
            True if valid date format
        """
        if not date_string or not isinstance(date_string, str):
            return False

        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y"
        ]

        for fmt in formats:
            try:
                datetime.strptime(date_string.strip(), fmt)
                return True
            except ValueError:
                continue

        return False

    @staticmethod
    def is_valid_file_type(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Validate file type by extension

        Args:
            filename: Filename to check
            allowed_extensions: List of allowed extensions (without dots)

        Returns:
            True if file type is allowed
        """
        if not filename or not isinstance(filename, str):
            return False

        if not allowed_extensions:
            return True

        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        allowed_lower = [ext.lower().lstrip('.') for ext in allowed_extensions]

        return file_ext in allowed_lower

    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """
        Check if filename is safe (no directory traversal, etc.)

        Args:
            filename: Filename to check

        Returns:
            True if filename is safe
        """
        if not filename or not isinstance(filename, str):
            return False

        # Check for directory traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False

        # Check for system files
        dangerous_names = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3',
                          'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
                          'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6',
                          'lpt7', 'lpt8', 'lpt9']

        name_without_ext = filename.lower().split('.')[0]
        if name_without_ext in dangerous_names:
            return False

        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        if any(char in filename for char in invalid_chars):
            return False

        return True

    @staticmethod
    def validate_file_size(file_size: int, max_size: int = 10 * 1024 * 1024) -> bool:
        """
        Validate file size

        Args:
            file_size: File size in bytes
            max_size: Maximum allowed size in bytes (default 10MB)

        Returns:
            True if file size is within limit
        """
        return 0 < file_size <= max_size

    @staticmethod
    def sanitize_text_input(text: str, max_length: int = None) -> str:
        """
        Sanitize text input

        Args:
            text: Text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')

        # Limit length if specified
        if max_length and len(text) > max_length:
            text = text[:max_length]

        return text

    @staticmethod
    def is_valid_json(json_string: str) -> bool:
        """
        Check if string is valid JSON

        Args:
            json_string: String to validate

        Returns:
            True if valid JSON
        """
        if not json_string or not isinstance(json_string, str):
            return False

        try:
            import json
            json.loads(json_string)
            return True
        except (ValueError, TypeError):
            return False


class DataCleaner:
    """Utility class for cleaning and processing data"""

    @staticmethod
    def clean_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize form data

        Args:
            form_data: Raw form data dictionary

        Returns:
            Cleaned form data
        """
        cleaned = {}

        for key, value in form_data.items():
            if isinstance(value, str):
                # Clean string values
                cleaned_value = ValidationUtils.sanitize_text_input(value)
                if cleaned_value:  # Only include non-empty values
                    cleaned[key] = cleaned_value
            elif isinstance(value, (list, tuple)):
                # Handle multiple values (checkboxes, etc.)
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        clean_item = ValidationUtils.sanitize_text_input(item)
                        if clean_item:
                            cleaned_list.append(clean_item)
                if cleaned_list:
                    cleaned[key] = cleaned_list
            elif value is not None:
                # Keep non-None values as-is
                cleaned[key] = value

        return cleaned

    @staticmethod
    def normalize_phone_number(phone: str) -> str:
        """
        Normalize phone number format

        Args:
            phone: Raw phone number

        Returns:
            Normalized phone number
        """
        if not phone or not isinstance(phone, str):
            return ""

        # Remove all non-digit characters except + at start
        if phone.startswith('+'):
            digits = '+' + re.sub(r'[^\d]', '', phone[1:])
        else:
            digits = re.sub(r'[^\d]', '', phone)

        return digits

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize email address

        Args:
            email: Raw email address

        Returns:
            Normalized email address
        """
        if not email or not isinstance(email, str):
            return ""

        return email.strip().lower()

    @staticmethod
    def extract_file_info(file) -> Dict[str, Any]:
        """
        Extract file information for validation

        Args:
            file: File object from request

        Returns:
            Dictionary with file information
        """
        if not file or not hasattr(file, 'filename'):
            return {}

        filename = file.filename or ""

        info = {
            'original_filename': filename,
            'safe_filename': ValidationUtils.sanitize_text_input(filename),
            'extension': filename.split('.')[-1].lower() if '.' in filename else '',
            'mime_type': mimetypes.guess_type(filename)[0] if filename else None,
            'size': 0
        }

        # Try to get file size
        try:
            if hasattr(file, 'content_length') and file.content_length:
                info['size'] = file.content_length
            elif hasattr(file, 'seek') and hasattr(file, 'tell'):
                # For file-like objects
                current_pos = file.tell()
                file.seek(0, 2)  # Seek to end
                info['size'] = file.tell()
                file.seek(current_pos)  # Restore position
        except (AttributeError, OSError):
            pass

        return info


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, List[str]]:
    """
    Validate that required fields are present and not empty

    Args:
        data: Data dictionary to validate
        required_fields: List of required field names

    Returns:
        Dictionary of field validation errors
    """
    errors = {}

    for field in required_fields:
        if field not in data:
            errors[field] = ["This field is required"]
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            errors[field] = ["This field cannot be empty"]

    return errors


def validate_field_lengths(data: Dict[str, Any], field_limits: Dict[str, int]) -> Dict[str, List[str]]:
    """
    Validate field length limits

    Args:
        data: Data dictionary to validate
        field_limits: Dictionary mapping field names to max lengths

    Returns:
        Dictionary of field validation errors
    """
    errors = {}

    for field, max_length in field_limits.items():
        if field in data and isinstance(data[field], str):
            if len(data[field]) > max_length:
                errors[field] = [f"This field cannot exceed {max_length} characters"]

    return errors


def merge_validation_errors(*error_dicts) -> Dict[str, List[str]]:
    """
    Merge multiple validation error dictionaries

    Args:
        *error_dicts: Multiple error dictionaries to merge

    Returns:
        Merged error dictionary
    """
    merged = {}

    for error_dict in error_dicts:
        if not error_dict:
            continue

        for field, errors in error_dict.items():
            if field in merged:
                merged[field].extend(errors)
            else:
                merged[field] = list(errors) if isinstance(errors, list) else [errors]

    return merged
