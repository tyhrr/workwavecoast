"""
Service Tests
Unit tests for service layer components
"""
import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from services import ApplicationService, AdminService, FileService, EmailService


class TestApplicationService:
    """Test cases for ApplicationService"""

    def setup_method(self):
        """Setup test fixtures"""
        self.logger = Mock(spec=logging.Logger)
        self.service = ApplicationService(self.logger)

    def test_health_check(self):
        """Test service health check"""
        result = self.service.health_check()
        assert isinstance(result, dict)
        assert "status" in result
        assert "service" in result
        assert result["service"] == "ApplicationService"

    def test_validate_application_data_valid(self):
        """Test validation with valid data"""
        valid_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'juan@email.com',
            'telefono': '+1234567890',
            'nacionalidad': 'Argentina',
            'puesto': 'Developer',
            'ingles_nivel': 'Intermedio',
            'experiencia': 'Tengo 5 años de experiencia en desarrollo web'
        }

        result = self.service.validate_application_data(valid_data)
        assert result[0] is True  # Should be valid

    def test_validate_application_data_invalid(self):
        """Test validation with invalid data"""
        invalid_data = {
            'nombre': '',  # Empty name
            'email': 'invalid-email'  # Invalid email
        }

        result = self.service.validate_application_data(invalid_data)
        assert result[0] is False  # Should be invalid
        assert isinstance(result[1], str)  # Should have error message


class TestAdminService:
    """Test cases for AdminService"""

    def setup_method(self):
        """Setup test fixtures"""
        self.logger = Mock(spec=logging.Logger)
        self.service = AdminService(self.logger)

    def test_health_check(self):
        """Test service health check"""
        result = self.service.health_check()
        assert isinstance(result, dict)
        assert "status" in result
        assert "service" in result
        assert result["service"] == "AdminService"

    def test_authenticate_admin_valid(self):
        """Test admin authentication with valid credentials"""
        result = self.service.authenticate_admin("admin", "admin123")
        assert result["success"] is True
        assert "token" in result["data"]
        assert "admin" in result["data"]

    def test_authenticate_admin_invalid(self):
        """Test admin authentication with invalid credentials"""
        result = self.service.authenticate_admin("wrong", "credentials")
        assert result["success"] is False
        assert "error" in result


class TestFileService:
    """Test cases for FileService"""

    def setup_method(self):
        """Setup test fixtures"""
        self.logger = Mock(spec=logging.Logger)
        self.service = FileService(self.logger)

    def test_health_check(self):
        """Test service health check"""
        result = self.service.health_check()
        assert isinstance(result, dict)
        assert "status" in result
        assert "service" in result
        assert result["service"] == "FileService"


class TestEmailService:
    """Test cases for EmailService"""

    def setup_method(self):
        """Setup test fixtures"""
        self.logger = Mock(spec=logging.Logger)
        self.service = EmailService(self.logger)

    def test_health_check(self):
        """Test service health check"""
        result = self.service.health_check()
        assert isinstance(result, dict)
        assert "status" in result
        assert "service" in result
        assert result["service"] == "EmailService"


class TestBaseServiceFunctionality:
    """Test common base service functionality"""

    def test_success_response_format(self):
        """Test success response format"""
        logger = Mock(spec=logging.Logger)
        service = ApplicationService(logger)

        result = service.success_response({"test": "data"}, "Test message")

        assert result["success"] is True
        assert result["data"] == {"test": "data"}
        assert result["message"] == "Test message"

    def test_error_response_format(self):
        """Test error response format"""
        logger = Mock(spec=logging.Logger)
        service = ApplicationService(logger)

        result = service.error_response("Test error", "TestError")

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["error_type"] == "TestError"


# Integration tests
class TestServiceIntegration:
    """Integration tests between services"""

    def setup_method(self):
        """Setup test fixtures"""
        self.logger = Mock(spec=logging.Logger)
        self.app_service = ApplicationService(self.logger)
        self.admin_service = AdminService(self.logger)

    @pytest.mark.integration
    def test_services_initialization(self):
        """Test that all services can be initialized together"""
        services = [
            ApplicationService(self.logger),
            AdminService(self.logger),
            FileService(self.logger),
            EmailService(self.logger)
        ]

        for service in services:
            health = service.health_check()
            assert health["status"] == "healthy"
