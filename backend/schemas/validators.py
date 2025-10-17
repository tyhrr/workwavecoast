"""
Validators
Custom validation functions and validators for the application
"""
import re
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    return True, None

def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format

    Args:
        phone: Phone number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"

    # Remove spaces, dashes, and parentheses
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)

    # Check if it contains only digits and optional + at the beginning
    if not re.match(r'^\+?\d{7,15}$', clean_phone):
        return False, "Invalid phone number format"

    return True, None

def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, Optional[str]]:
    """
    Validate name fields (first name, last name)

    Args:
        name: Name to validate
        field_name: Name of the field for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, f"{field_name} is required"

    if len(name.strip()) < 2:
        return False, f"{field_name} must be at least 2 characters long"

    if len(name.strip()) > 50:
        return False, f"{field_name} must be less than 50 characters"

    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s\-']+$", name.strip()):
        return False, f"{field_name} contains invalid characters"

    return True, None

def validate_position(position: str) -> Tuple[bool, Optional[str]]:
    """
    Validate job position

    Args:
        position: Position to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not position:
        return False, "Position is required"

    if len(position.strip()) < 2:
        return False, "Position must be at least 2 characters long"

    if len(position.strip()) > 100:
        return False, "Position must be less than 100 characters"

    return True, None

def validate_experience(experience: str) -> Tuple[bool, Optional[str]]:
    """
    Validate experience description

    Args:
        experience: Experience text to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not experience:
        return False, "Experience description is required"

    if len(experience.strip()) < 10:
        return False, "Experience description must be at least 10 characters long"

    if len(experience.strip()) > 2000:
        return False, "Experience description must be less than 2000 characters"

    return True, None

def validate_english_level(level: str) -> Tuple[bool, Optional[str]]:
    """
    Validate English proficiency level

    Args:
        level: English level to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_levels = [
        'Básico', 'Intermedio', 'Avanzado', 'Nativo',
        'Basic', 'Intermediate', 'Advanced', 'Native'
    ]

    if not level:
        return False, "English level is required"

    if level not in valid_levels:
        return False, f"Invalid English level. Must be one of: {', '.join(valid_levels)}"

    return True, None

def validate_nationality(nationality: str) -> Tuple[bool, Optional[str]]:
    """
    Validate nationality

    Args:
        nationality: Nationality to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not nationality:
        return False, "Nationality is required"

    if len(nationality.strip()) < 2:
        return False, "Nationality must be at least 2 characters long"

    if len(nationality.strip()) > 50:
        return False, "Nationality must be less than 50 characters"

    return True, None

def validate_application_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate complete application data

    Args:
        data: Application data dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Validate required fields
    required_fields = ['nombre', 'apellido', 'email', 'telefono', 'nacionalidad', 'puesto', 'ingles_nivel', 'experiencia']

    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")

    # If we have missing required fields, return early
    if errors:
        return False, errors

    # Validate individual fields
    validations = [
        (validate_name(data['nombre'], 'First name')),
        (validate_name(data['apellido'], 'Last name')),
        (validate_email(data['email'])),
        (validate_phone(data['telefono'])),
        (validate_nationality(data['nacionalidad'])),
        (validate_position(data['puesto'])),
        (validate_english_level(data['ingles_nivel'])),
        (validate_experience(data['experiencia']))
    ]

    for is_valid, error_msg in validations:
        if not is_valid and error_msg:
            errors.append(error_msg)

    return len(errors) == 0, errors

def validate_admin_credentials(username: str, password: str) -> Tuple[bool, List[str]]:
    """
    Validate admin credentials

    Args:
        username: Username to validate
        password: Password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Validate username
    if not username:
        errors.append("Username is required")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters long")
    elif len(username) > 50:
        errors.append("Username must be less than 50 characters")

    # Validate password
    if not password:
        errors.append("Password is required")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) > 128:
        errors.append("Password must be less than 128 characters")

    return len(errors) == 0, errors

def validate_file_upload(filename: str, file_size: int, allowed_extensions: List[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate file upload

    Args:
        filename: Name of the uploaded file
        file_size: Size of the file in bytes
        allowed_extensions: List of allowed file extensions

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is required"

    # Check file extension
    if allowed_extensions:
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        if file_extension not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    # Check file size (limit to 10MB by default)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file_size > max_size:
        return False, "File size too large. Maximum size is 10MB"

    return True, None

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potential script tags and other harmful content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = text.strip()

    return text
