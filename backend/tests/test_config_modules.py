"""
Tests for Configuration Modules
Testing the new modular configuration system
"""
import pytest
import os
from unittest.mock import patch, Mock


class TestConfigSettings:
    """Test the main settings configuration"""

    def test_config_from_env_with_all_variables(self):
        """Test config creation with all environment variables"""
        env_vars = {
            'SECRET_KEY': 'test-secret',
            'ADMIN_USERNAME': 'test_admin',
            'ADMIN_PASSWORD': 'test_pass',
            'MONGODB_URI': 'mongodb://test:27017/test',
            'CLOUDINARY_CLOUD_NAME': 'test_cloud',
            'CLOUDINARY_API_KEY': 'test_key',
            'CLOUDINARY_API_SECRET': 'test_secret',
            'MAIL_SERVER': 'smtp.test.com',
            'MAIL_PORT': '587',
            'MAIL_USE_TLS': 'True',
            'MAIL_USERNAME': 'test@test.com',
            'MAIL_PASSWORD': 'test_mail_pass',
            'PORT': '5000'
        }

        with patch.dict(os.environ, env_vars):
            from config.settings import Config
            config = Config.from_env()

            assert config.SECRET_KEY == 'test-secret'
            assert config.ADMIN_USERNAME == 'test_admin'
            assert config.MONGODB_URI == 'mongodb://test:27017/test'
            assert config.MAIL_PORT == 587
            assert config.MAIL_USE_TLS is True

    def test_config_validation_success(self):
        """Test config validation with valid data"""
        env_vars = {
            'SECRET_KEY': 'valid-secret',
            'ADMIN_USERNAME': 'admin',
            'ADMIN_PASSWORD': 'password',
            'MONGODB_URI': 'mongodb://localhost:27017/test',
            'MAIL_USERNAME': 'test@example.com',
            'MAIL_PASSWORD': 'mail_password'
        }

        with patch.dict(os.environ, env_vars):
            from config.settings import Config
            config = Config.from_env()

            assert config.validate() is True

    def test_config_validation_failure(self):
        """Test config validation with missing required fields"""
        env_vars = {
            'SECRET_KEY': '',  # Empty required field
            'ADMIN_USERNAME': 'admin',
            # Missing other required fields
        }

        with patch.dict(os.environ, env_vars):
            from config.settings import Config
            config = Config.from_env()

            assert config.validate() is False

    def test_cloudinary_configured_check(self):
        """Test Cloudinary configuration check"""
        env_vars = {
            'CLOUDINARY_CLOUD_NAME': 'valid_cloud',
            'CLOUDINARY_API_KEY': 'valid_key',
            'CLOUDINARY_API_SECRET': 'valid_secret'
        }

        with patch.dict(os.environ, env_vars):
            from config.settings import Config
            config = Config.from_env()

            assert config.is_cloudinary_configured() is True

    def test_email_configured_check(self):
        """Test email configuration check"""
        env_vars = {
            'MAIL_USERNAME': 'test@example.com',
            'MAIL_PASSWORD': 'password',
            'MAIL_SERVER': 'smtp.example.com'
        }

        with patch.dict(os.environ, env_vars):
            from config.settings import Config
            config = Config.from_env()

            assert config.is_email_configured() is True


class TestConfigConstants:
    """Test configuration constants"""

    def test_constants_are_imported(self):
        """Test that constants are properly imported"""
        from config.constants import (
            FILE_SIZE_LIMITS, ALLOWED_EXTENSIONS, REQUIRED_FIELDS,
            EMAIL_PATTERN, PHONE_PATTERNS, COUNTRY_ISO_MAPPING
        )

        assert isinstance(FILE_SIZE_LIMITS, dict)
        assert isinstance(ALLOWED_EXTENSIONS, dict)
        assert isinstance(REQUIRED_FIELDS, list)
        assert EMAIL_PATTERN is not None
        assert isinstance(PHONE_PATTERNS, dict)
        assert isinstance(COUNTRY_ISO_MAPPING, dict)

    def test_file_size_limits_structure(self):
        """Test file size limits structure"""
        from config.constants import FILE_SIZE_LIMITS

        # Should have limits for common file types
        assert 'cv' in FILE_SIZE_LIMITS
        assert 'carta_presentacion' in FILE_SIZE_LIMITS

        # Limits should be positive integers
        for field, limit in FILE_SIZE_LIMITS.items():
            assert isinstance(limit, int)
            assert limit > 0

    def test_allowed_extensions_structure(self):
        """Test allowed extensions structure"""
        from config.constants import ALLOWED_EXTENSIONS

        # Should have extensions for common file types
        assert 'cv' in ALLOWED_EXTENSIONS
        assert 'carta_presentacion' in ALLOWED_EXTENSIONS

        # Extensions should be lists with dot prefix
        for field, extensions in ALLOWED_EXTENSIONS.items():
            assert isinstance(extensions, list)
            for ext in extensions:
                assert ext.startswith('.')

    def test_required_fields_list(self):
        """Test required fields list"""
        from config.constants import REQUIRED_FIELDS

        expected_fields = ['nombre', 'apellido', 'email', 'telefono', 'puesto']

        for field in expected_fields:
            assert field in REQUIRED_FIELDS

    def test_country_iso_mapping(self):
        """Test country ISO mapping"""
        from config.constants import COUNTRY_ISO_MAPPING

        # Should have common countries
        assert 'México' in COUNTRY_ISO_MAPPING
        assert 'Estados Unidos' in COUNTRY_ISO_MAPPING
        assert 'España' in COUNTRY_ISO_MAPPING

        # ISO codes should be 2 characters
        for country, iso in COUNTRY_ISO_MAPPING.items():
            assert len(iso) == 2
            assert iso.isupper()


class TestDatabaseConfig:
    """Test database configuration"""

    @patch('config.database.MongoClient')
    def test_database_config_creation(self, mock_client):
        """Test database configuration creation"""
        from config.database import DatabaseConfig

        # Mock client
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.admin.command.return_value = True

        db_config = DatabaseConfig('mongodb://test:27017/test')

        assert db_config.uri == 'mongodb://test:27017/test'

    @patch('config.database.MongoClient')
    def test_database_collections_access(self, mock_client):
        """Test database collections access"""
        from config.database import DatabaseConfig

        # Mock client and database
        mock_client_instance = Mock()
        mock_db = Mock()
        mock_collection = Mock()

        mock_client.return_value = mock_client_instance
        mock_client_instance.admin.command.return_value = True
        # Mock the database access properly
        mock_client_instance.__getitem__ = Mock(return_value=mock_db)
        mock_db.__getitem__ = Mock(return_value=mock_collection)

        db_config = DatabaseConfig('mongodb://test:27017/test')

        # Access collections should not raise errors
        candidates = db_config.candidates
        admin_logs = db_config.admin_logs
        email_logs = db_config.email_logs

        assert candidates is not None
        assert admin_logs is not None
        assert email_logs is not None


class TestCloudinaryConfig:
    """Test Cloudinary configuration"""

    def test_cloudinary_config_creation(self):
        """Test Cloudinary configuration creation"""
        from config.cloudinary_config import CloudinaryConfig

        config = CloudinaryConfig('test_cloud', 'test_key', 'test_secret')

        assert config.cloud_name == 'test_cloud'
        assert config.api_key == 'test_key'
        assert config.api_secret == 'test_secret'

    def test_cloudinary_is_configured_check(self):
        """Test Cloudinary configuration check"""
        from config.cloudinary_config import CloudinaryConfig

        # Valid configuration
        valid_config = CloudinaryConfig('valid_cloud', 'valid_key', 'valid_secret')
        assert valid_config.is_configured() is True

        # Invalid configuration (missing values)
        invalid_config = CloudinaryConfig('', '', '')
        assert invalid_config.is_configured() is False

        # Invalid configuration (default cloud name)
        default_config = CloudinaryConfig('tu_cloud_name', 'key', 'secret')
        assert default_config.is_configured() is False

    def test_cloudinary_get_info(self):
        """Test Cloudinary info retrieval"""
        from config.cloudinary_config import CloudinaryConfig

        config = CloudinaryConfig('test_cloud', 'test_key', 'test_secret')
        info = config.get_info()

        assert isinstance(info, dict)
        assert 'configured' in info
        assert 'cloud_name' in info
        assert 'api_key_set' in info
        assert 'api_secret_set' in info


class TestEmailConfig:
    """Test email configuration"""

    def test_email_config_creation(self):
        """Test email configuration creation"""
        from config.email import EmailConfig

        config = EmailConfig('smtp.test.com', 587, True, 'test@test.com', 'password')

        assert config.server == 'smtp.test.com'
        assert config.port == 587
        assert config.use_tls is True
        assert config.username == 'test@test.com'
        assert config.password == 'password'

    def test_email_is_configured_check(self):
        """Test email configuration check"""
        from config.email import EmailConfig

        # Valid configuration
        valid_config = EmailConfig('smtp.test.com', 587, True, 'test@test.com', 'password')
        assert valid_config.is_configured() is True

        # Invalid configuration (missing values)
        invalid_config = EmailConfig('', 587, True, '', '')
        assert invalid_config.is_configured() is False

    def test_email_get_info(self):
        """Test email info retrieval"""
        from config.email import EmailConfig

        config = EmailConfig('smtp.test.com', 587, True, 'test@test.com', 'password')
        info = config.get_info()

        assert isinstance(info, dict)
        assert 'configured' in info
        assert 'server' in info
        assert 'port' in info
        assert 'username_set' in info
        assert 'password_set' in info


class TestConfigurationIntegration:
    """Test integration between configuration modules"""

    def test_get_config_function(self):
        """Test the main get_config function"""
        env_vars = {
            'SECRET_KEY': 'test-secret',
            'ADMIN_USERNAME': 'admin',
            'ADMIN_PASSWORD': 'password',
            'MONGODB_URI': 'mongodb://test:27017/test',
            'MAIL_USERNAME': 'test@test.com',
            'MAIL_PASSWORD': 'password'
        }

        with patch.dict(os.environ, env_vars):
            from config.settings import get_config

            config = get_config()
            assert config is not None
            assert config.SECRET_KEY == 'test-secret'

    def test_managers_singleton_pattern(self):
        """Test that managers follow singleton pattern"""
        from config.database import DatabaseManager
        from config.cloudinary_config import CloudinaryManager
        from config.email import EmailManager

        # Test that multiple calls return same instance
        db_manager1 = DatabaseManager()
        db_manager2 = DatabaseManager()
        assert db_manager1 is db_manager2

        cloudinary_manager1 = CloudinaryManager()
        cloudinary_manager2 = CloudinaryManager()
        assert cloudinary_manager1 is cloudinary_manager2

        email_manager1 = EmailManager()
        email_manager2 = EmailManager()
        assert email_manager1 is email_manager2
