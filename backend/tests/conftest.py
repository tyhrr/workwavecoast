"""
Test Configuration and Fixtures
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

@pytest.fixture
def app():
    """Create application for testing"""
    # Mock environment variables to avoid loading real .env
    env_vars = {
        'SECRET_KEY': 'test-secret-key',
        'ADMIN_USERNAME': 'test_admin',
        'ADMIN_PASSWORD': 'test_password',
        'MONGODB_URI': 'mongodb://localhost:27017/test_db',
        'CLOUDINARY_CLOUD_NAME': 'test_cloud',
        'CLOUDINARY_API_KEY': 'test_key',
        'CLOUDINARY_API_SECRET': 'test_secret',
        'MAIL_SERVER': 'smtp.example.com',
        'MAIL_PORT': '587',
        'MAIL_USE_TLS': 'True',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test_password'
    }

    with patch.dict(os.environ, env_vars):
        import app as app_module
        app = app_module.app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

        with app.app_context():
            yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def mock_db():
    """Mock database for testing"""
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.candidates = mock_collection
    return mock_db

@pytest.fixture
def mock_cloudinary():
    """Mock Cloudinary for testing"""
    with patch('cloudinary.uploader.upload') as mock_upload:
        mock_upload.return_value = {
            'public_id': 'test_public_id',
            'secure_url': 'https://test.cloudinary.com/test.jpg',
            'bytes': 12345
        }
        yield mock_upload

@pytest.fixture
def mock_mail():
    """Mock email sending for testing"""
    with patch('flask_mail.Message') as mock_message, \
         patch('flask_mail.Mail.send') as mock_send:
        yield mock_send

@pytest.fixture
def sample_application_data():
    """Sample application data for testing"""
    return {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'email': 'juan@example.com',
        'telefono': '+1-555-123-4567',
        'puesto': 'Desarrollador',
        'ingles_nivel': 'Avanzado',
        'experiencia': 'Tengo 5 años de experiencia en desarrollo web',
        'nacionalidad': 'México'
    }
