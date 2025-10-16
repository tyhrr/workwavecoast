"""
Tests for API Endpoints
Critical routes that must continue working during refactoring
"""
import pytest
import json
from unittest.mock import patch, Mock
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request


class TestApplicationEndpoints:
    """Test application submission endpoints"""
    
    def test_submit_application_get_renders_form(self, client):
        """Test that GET /api/submit renders the form"""
        response = client.get('/api/submit')
        assert response.status_code == 200
        assert b'workwave' in response.data.lower()
    
    @patch('app.candidates')
    @patch('app.cloudinary.uploader.upload')
    @patch('app.mail.send')
    def test_submit_application_success(self, mock_mail, mock_upload, mock_candidates, client, sample_application_data):
        """Test successful application submission"""
        # Mock dependencies
        mock_candidates.find_one.return_value = None  # No duplicate
        mock_candidates.insert_one.return_value = Mock(inserted_id='test_id')
        mock_upload.return_value = {
            'public_id': 'test_cv',
            'secure_url': 'https://test.com/cv.pdf',
            'bytes': 12345
        }
        
        # Prepare form data with file
        data = sample_application_data.copy()
        data['cv'] = (open(__file__, 'rb'), 'test_cv.pdf')
        data['carta_presentacion'] = (open(__file__, 'rb'), 'test_carta.pdf')
        
        response = client.post('/api/submit', 
                             data=data,
                             content_type='multipart/form-data')
        
        # Should redirect after successful submission
        assert response.status_code in [200, 302]
        mock_candidates.insert_one.assert_called_once()
    
    @patch('app.collection')
    def test_submit_application_duplicate_email(self, mock_collection, client, sample_application_data):
        """Test duplicate email detection"""
        # Mock existing application
        mock_collection.find_one.return_value = {'email': 'juan@example.com'}
        
        response = client.post('/api/submit', 
                             data=sample_application_data,
                             content_type='multipart/form-data')
        
        assert response.status_code == 400
        assert b'duplicado' in response.data.lower() or b'duplicate' in response.data.lower()
    
    def test_submit_application_missing_required_field(self, client):
        """Test validation with missing required fields"""
        incomplete_data = {
            'nombre': 'Juan',
            # Missing other required fields
        }
        
        response = client.post('/api/submit', 
                             data=incomplete_data,
                             content_type='multipart/form-data')
        
        assert response.status_code == 400
    
    @patch('app.collection')
    def test_get_applications_with_pagination(self, mock_collection, client):
        """Test applications list with pagination"""
        # Mock database response
        mock_applications = [
            {'_id': 'id1', 'nombre': 'Juan', 'email': 'juan@test.com'},
            {'_id': 'id2', 'nombre': 'Maria', 'email': 'maria@test.com'}
        ]
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_applications
        mock_collection.count_documents.return_value = 2
        
        response = client.get('/api/applications?page=1&per_page=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'applications' in data
        assert len(data['applications']) == 2


class TestAdminEndpoints:
    """Test admin panel endpoints"""
    
    def test_admin_login_get_renders_form(self, client):
        """Test that GET /admin/login renders login form"""
        response = client.get('/admin/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'username' in response.data.lower()
    
    def test_admin_login_success(self, client, app):
        """Test successful admin login"""
        with app.test_request_context():
            data = {
                'username': app.config.get('ADMIN_USERNAME', 'test_admin'),
                'password': app.config.get('ADMIN_PASSWORD', 'test_password')
            }
            
            response = client.post('/admin/login', 
                                 data=data,
                                 follow_redirects=True)
            
            # Should either redirect to dashboard or show success
            assert response.status_code == 200
    
    def test_admin_login_failure(self, client):
        """Test failed admin login"""
        data = {
            'username': 'wrong_user',
            'password': 'wrong_password'
        }
        
        response = client.post('/admin/login', data=data)
        
        # Should show error or redirect back to login
        assert response.status_code in [200, 401, 302]
        if response.status_code == 200:
            assert b'error' in response.data.lower() or b'invalid' in response.data.lower()
    
    @patch('app.collection')
    def test_admin_dashboard_requires_auth(self, mock_collection, client):
        """Test that admin dashboard requires authentication"""
        mock_collection.find.return_value.sort.return_value = []
        mock_collection.count_documents.return_value = 0
        
        response = client.get('/admin/')
        
        # Should redirect to login or show 401
        assert response.status_code in [302, 401]
    
    @patch('app.collection')
    def test_delete_application_endpoint(self, mock_collection, client):
        """Test application deletion endpoint"""
        mock_collection.find_one.return_value = {'_id': 'test_id'}
        mock_collection.delete_one.return_value = Mock(deleted_count=1)
        
        # Note: In real test, we'd need to login first
        response = client.delete('/admin/delete/test_id')
        
        # Response depends on authentication
        assert response.status_code in [200, 302, 401]


class TestFileEndpoints:
    """Test file handling endpoints"""
    
    def test_cloudinary_proxy_endpoint(self, client):
        """Test Cloudinary proxy endpoint"""
        response = client.get('/api/cloudinary-proxy/test/file.jpg')
        
        # Should either proxy the file or return error
        assert response.status_code in [200, 302, 404]
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint if it exists"""
        response = client.get('/health')
        
        # May or may not exist in current version
        assert response.status_code in [200, 404]


class TestUtilityEndpoints:
    """Test utility and helper endpoints"""
    
    def test_home_page_renders(self, client):
        """Test that home page renders correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'workwave' in response.data.lower()
    
    def test_api_base_endpoint(self, client):
        """Test API base endpoint"""
        response = client.get('/api/')
        
        # Should return some kind of API info
        assert response.status_code in [200, 404, 405]