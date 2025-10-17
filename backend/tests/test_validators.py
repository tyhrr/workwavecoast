"""
Tests for Validation Functions
Testing the validation logic that must be preserved during refactoring
"""
import pytest
from unittest.mock import patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPhoneValidation:
    """Test phone number validation functions"""

    def test_validate_phone_number_valid_formats(self):
        """Test various valid phone number formats"""
        # Import the function from current app.py
        try:
            from app import validate_phone_number

            valid_phones = [
                '+1-555-123-4567',
                '+52-55-1234-5678',
                '+34-91-123-4567',
                '+44-20-1234-5678',
                '555-123-4567',
                '(555) 123-4567',
                '555.123.4567'
            ]

            for phone in valid_phones:
                is_valid, _ = validate_phone_number(phone)
                assert is_valid, f"Phone {phone} should be valid"

        except ImportError:
            pytest.skip("validate_phone_number function not found in app.py")

    def test_validate_phone_number_invalid_formats(self):
        """Test invalid phone number formats"""
        try:
            from app import validate_phone_number

            invalid_phones = [
                '',
                '123',
                'abc-def-ghij',
                '555-123',
                '555-123-456789',
                'not a phone'
            ]

            for phone in invalid_phones:
                is_valid, _ = validate_phone_number(phone)
                assert not is_valid, f"Phone {phone} should be invalid"

        except ImportError:
            pytest.skip("validate_phone_number function not found in app.py")


class TestEmailValidation:
    """Test email validation"""

    def test_email_validation_valid_emails(self):
        """Test valid email formats"""
        try:
            from app import validate_application_data

            valid_emails = [
                'test@example.com',
                'user.name@domain.co.uk',
                'user+tag@example.org',
                'firstname.lastname@company.com'
            ]

            base_data = {
                'nombre': 'Test',
                'apellido': 'User',
                'email': '',  # Will be replaced
                'telefono': '+1-555-123-4567',
                'puesto': 'Developer',
                'ingles_nivel': 'Avanzado',
                'experiencia': 'Test experience',
                'nacionalidad': 'México'
            }

            for email in valid_emails:
                data = base_data.copy()
                data['email'] = email

                is_valid, errors = validate_application_data(data)
                email_errors = [e for e in errors if 'email' in e.lower()]
                assert len(email_errors) == 0, f"Email {email} should be valid"

        except ImportError:
            pytest.skip("validate_application_data function not found in app.py")

    def test_email_validation_invalid_emails(self):
        """Test invalid email formats"""
        try:
            from app import validate_application_data

            invalid_emails = [
                '',
                'invalid',
                '@domain.com',
                'user@',
                'user..name@domain.com',
                'user@domain',
                'user name@domain.com'
            ]

            base_data = {
                'nombre': 'Test',
                'apellido': 'User',
                'email': '',  # Will be replaced
                'telefono': '+1-555-123-4567',
                'puesto': 'Developer',
                'ingles_nivel': 'Avanzado',
                'experiencia': 'Test experience',
                'nacionalidad': 'México'
            }

            for email in invalid_emails:
                data = base_data.copy()
                data['email'] = email

                is_valid, errors = validate_application_data(data)
                email_errors = [e for e in errors if 'email' in e.lower()]
                assert len(email_errors) > 0, f"Email {email} should be invalid"

        except ImportError:
            pytest.skip("validate_application_data function not found in app.py")


class TestFileValidation:
    """Test file validation functions"""

    def test_validate_file_allowed_extensions(self):
        """Test file validation with allowed extensions"""
        try:
            from app import validate_file

            # Mock file objects
            class MockFile:
                def __init__(self, filename, size=1024):
                    self.filename = filename
                    self.content_length = size

                def seek(self, pos):
                    pass

                def tell(self):
                    return self.content_length

            allowed_files = [
                ('cv', MockFile('resume.pdf')),
                ('carta_presentacion', MockFile('cover.pdf')),
                ('cv', MockFile('resume.doc')),
                ('carta_presentacion', MockFile('cover.docx'))
            ]

            for field_name, file_obj in allowed_files:
                is_valid, error, file_size = validate_file(file_obj, field_name)
                assert is_valid, f"File {file_obj.filename} should be valid for {field_name}"

        except ImportError:
            pytest.skip("validate_file function not found in app.py")

    def test_validate_file_disallowed_extensions(self):
        """Test file validation with disallowed extensions"""
        try:
            from app import validate_file

            class MockFile:
                def __init__(self, filename, size=1024):
                    self.filename = filename
                    self.content_length = size

                def seek(self, pos):
                    pass

                def tell(self):
                    return self.content_length

            disallowed_files = [
                ('cv', MockFile('virus.exe')),
                ('carta_presentacion', MockFile('script.js')),
                ('cv', MockFile('image.jpg')),
                ('carta_presentacion', MockFile('file.txt'))
            ]

            for field_name, file_obj in disallowed_files:
                is_valid, error, file_size = validate_file(file_obj, field_name)
                assert not is_valid, f"File {file_obj.filename} should be invalid for {field_name}"

        except ImportError:
            pytest.skip("validate_file function not found in app.py")

    def test_validate_file_size_limits(self):
        """Test file size validation"""
        try:
            from app import validate_file

            class MockFile:
                def __init__(self, filename, size):
                    self.filename = filename
                    self.content_length = size

                def seek(self, pos):
                    pass

                def tell(self):
                    return self.content_length

            # Test oversized file (>5MB)
            oversized_file = MockFile('large.pdf', 6 * 1024 * 1024)  # 6MB
            is_valid, error, file_size = validate_file(oversized_file, 'cv')
            assert not is_valid, "Oversized file should be invalid"
            assert error and ('tamaño' in error.lower() or 'size' in error.lower() or 'grande' in error.lower())

            # Test normal sized file
            normal_file = MockFile('normal.pdf', 1024 * 1024)  # 1MB
            is_valid, error, file_size = validate_file(normal_file, 'cv')
            assert is_valid, "Normal sized file should be valid"

        except ImportError:
            pytest.skip("validate_file function not found in app.py")


class TestApplicationDataValidation:
    """Test complete application data validation"""

    def test_validate_application_data_complete_valid(self):
        """Test validation with complete valid data"""
        try:
            from app import validate_application_data

            valid_data = {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'email': 'juan@example.com',
                'telefono': '+1-555-123-4567',
                'puesto': 'Desarrollador',
                'ingles_nivel': 'Avanzado',
                'experiencia': 'Tengo 5 años de experiencia en desarrollo web',
                'nacionalidad': 'México'
            }

            is_valid, errors = validate_application_data(valid_data)
            assert is_valid, f"Valid data should pass validation. Errors: {errors}"
            assert len(errors) == 0, f"No errors expected for valid data. Got: {errors}"

        except ImportError:
            pytest.skip("validate_application_data function not found in app.py")

    def test_validate_application_data_missing_required(self):
        """Test validation with missing required fields"""
        try:
            from app import validate_application_data

            # Test missing nombre
            incomplete_data = {
                'apellido': 'Pérez',
                'email': 'juan@example.com',
                'telefono': '+1-555-123-4567',
                'puesto': 'Desarrollador',
                'ingles_nivel': 'Avanzado',
                'experiencia': 'Experience',
                'nacionalidad': 'México'
            }

            is_valid, errors = validate_application_data(incomplete_data)
            assert not is_valid, "Data with missing required field should be invalid"
            assert len(errors) > 0, "Should have validation errors"

            # Check if error mentions the missing field
            error_text = ' '.join(errors).lower()
            assert 'nombre' in error_text or 'name' in error_text

        except ImportError:
            pytest.skip("validate_application_data function not found in app.py")

    def test_validate_application_data_invalid_field_values(self):
        """Test validation with invalid field values"""
        try:
            from app import validate_application_data

            invalid_data = {
                'nombre': '',  # Empty name
                'apellido': 'Pérez',
                'email': 'invalid-email',  # Invalid email
                'telefono': '123',  # Invalid phone
                'puesto': 'Desarrollador',
                'ingles_nivel': 'Avanzado',
                'experiencia': 'Experience',
                'nacionalidad': 'México'
            }

            is_valid, errors = validate_application_data(invalid_data)
            assert not is_valid, "Data with invalid field values should be invalid"
            assert len(errors) > 0, "Should have validation errors"

        except ImportError:
            pytest.skip("validate_application_data function not found in app.py")
