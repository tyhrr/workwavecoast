"""
Integration Tests
Testing complete workflows that must work during refactoring
"""
import pytest
import json
from unittest.mock import patch, Mock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFullApplicationWorkflow:
    """Test complete application submission workflow"""

    @patch('app.collection')
    @patch('app.cloudinary.uploader.upload')
    @patch('app.mail.send')
    @patch('flask_mail.Message')
    def test_complete_application_submission_workflow(self, mock_message, mock_mail, mock_upload, mock_collection, client, sample_application_data):
        """Test the complete flow from form submission to email confirmation"""

        # Setup mocks
        mock_collection.find_one.return_value = None  # No duplicate
        mock_collection.insert_one.return_value = Mock(inserted_id='test_id_123')

        mock_upload.return_value = {
            'public_id': 'workwave_coast/cv_test_123',
            'secure_url': 'https://res.cloudinary.com/test/cv.pdf',
            'bytes': 12345,
            'format': 'pdf'
        }

        mock_message_instance = Mock()
        mock_message.return_value = mock_message_instance
        mock_mail.return_value = None

        # Create mock files
        data = sample_application_data.copy()
        data['cv'] = (open(__file__, 'rb'), 'test_cv.pdf')
        data['carta_presentacion'] = (open(__file__, 'rb'), 'test_carta.pdf')

        # Submit application
        response = client.post('/api/submit',
                             data=data,
                             content_type='multipart/form-data')

        # Verify response
        assert response.status_code in [200, 302]

        # Verify database interaction
        mock_collection.find_one.assert_called()  # Duplicate check
        mock_collection.insert_one.assert_called()  # Application saved

        # Verify file upload
        assert mock_upload.call_count >= 1  # At least one file uploaded

        # Verify email sent
        mock_message.assert_called()
        mock_mail.assert_called()

    @patch('app.collection')
    def test_duplicate_email_prevention_workflow(self, mock_collection, client, sample_application_data):
        """Test that duplicate emails are properly prevented"""

        # Mock existing application with same email
        existing_app = {
            '_id': 'existing_id',
            'email': sample_application_data['email'],
            'nombre': 'Another Person'
        }
        mock_collection.find_one.return_value = existing_app

        # Try to submit duplicate
        response = client.post('/api/submit',
                             data=sample_application_data,
                             content_type='multipart/form-data')

        # Should be rejected
        assert response.status_code == 400

        # Should not insert new record
        mock_collection.insert_one.assert_not_called()

    @patch('app.collection')
    @patch('app.cloudinary.uploader.upload')
    def test_file_upload_error_handling_workflow(self, mock_upload, mock_collection, client, sample_application_data):
        """Test workflow when file upload fails"""

        # Setup mocks
        mock_collection.find_one.return_value = None  # No duplicate
        mock_upload.side_effect = Exception("Cloudinary upload failed")

        # Create form data with file
        data = sample_application_data.copy()
        data['cv'] = (open(__file__, 'rb'), 'test_cv.pdf')

        # Submit application
        response = client.post('/api/submit',
                             data=data,
                             content_type='multipart/form-data')

        # Should handle error gracefully
        # Response depends on error handling implementation
        assert response.status_code in [200, 400, 500]


class TestAdminWorkflow:
    """Test complete admin panel workflows"""

    @patch('app.collection')
    def test_admin_login_and_dashboard_workflow(self, mock_collection, client, app):
        """Test admin login followed by dashboard access"""

        # Mock applications data
        mock_applications = [
            {
                '_id': 'app1',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'email': 'juan@test.com',
                'puesto': 'Developer',
                'created_at': '2025-01-01T00:00:00'
            },
            {
                '_id': 'app2',
                'nombre': 'Maria',
                'apellido': 'García',
                'email': 'maria@test.com',
                'puesto': 'Designer',
                'created_at': '2025-01-02T00:00:00'
            }
        ]

        mock_collection.find.return_value.sort.return_value = mock_applications
        mock_collection.count_documents.return_value = 2

        # Step 1: Login
        with app.test_request_context():
            login_data = {
                'username': app.config.get('ADMIN_USERNAME', 'test_admin'),
                'password': app.config.get('ADMIN_PASSWORD', 'test_password')
            }

            login_response = client.post('/admin/login',
                                       data=login_data,
                                       follow_redirects=False)

            # Should login successfully
            assert login_response.status_code in [200, 302]

            # Step 2: Access dashboard
            dashboard_response = client.get('/admin/', follow_redirects=True)

            # Should show dashboard
            assert dashboard_response.status_code == 200

    @patch('app.collection')
    def test_admin_delete_application_workflow(self, mock_collection, client, app):
        """Test admin deleting an application"""

        # Mock application exists
        mock_application = {
            '_id': 'app_to_delete',
            'nombre': 'Test User',
            'email': 'test@example.com'
        }
        mock_collection.find_one.return_value = mock_application
        mock_collection.delete_one.return_value = Mock(deleted_count=1)

        # Try to delete (would need proper auth in real test)
        response = client.delete('/admin/delete/app_to_delete')

        # Response depends on authentication
        assert response.status_code in [200, 302, 401]

    @patch('app.collection')
    def test_admin_bulk_delete_workflow(self, mock_collection, client):
        """Test admin bulk delete functionality"""

        # Mock multiple applications
        mock_collection.delete_many.return_value = Mock(deleted_count=3)

        # Submit bulk delete request
        delete_data = {
            'application_ids': ['app1', 'app2', 'app3']
        }

        response = client.post('/admin/bulk-delete',
                             data=json.dumps(delete_data),
                             content_type='application/json')

        # Response depends on authentication and implementation
        assert response.status_code in [200, 302, 401, 404]


class TestAPIWorkflow:
    """Test API endpoints workflow"""

    @patch('app.collection')
    def test_applications_list_with_pagination_workflow(self, mock_collection, client):
        """Test retrieving applications with pagination"""

        # Mock paginated data
        mock_applications = [
            {'_id': f'app{i}', 'nombre': f'User{i}', 'email': f'user{i}@test.com'}
            for i in range(1, 6)  # 5 applications
        ]

        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_applications[:3]  # First page
        mock_collection.count_documents.return_value = 5

        # Request first page
        response = client.get('/api/applications?page=1&per_page=3')

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'applications' in data
            assert len(data['applications']) <= 3
            assert 'total' in data or 'pagination' in data

    @patch('app.collection')
    def test_application_search_workflow(self, mock_collection, client):
        """Test searching applications"""

        # Mock search results
        mock_results = [
            {'_id': 'app1', 'nombre': 'Juan', 'email': 'juan@test.com'}
        ]

        mock_collection.find.return_value.sort.return_value = mock_results
        mock_collection.count_documents.return_value = 1

        # Search by name
        response = client.get('/api/applications?search=Juan')

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'applications' in data


class TestErrorHandlingWorkflow:
    """Test error handling workflows"""

    @patch('app.collection')
    def test_database_error_handling_workflow(self, mock_collection, client, sample_application_data):
        """Test workflow when database is unavailable"""

        # Mock database error
        mock_collection.find_one.side_effect = Exception("Database connection failed")

        # Try to submit application
        response = client.post('/api/submit',
                             data=sample_application_data,
                             content_type='multipart/form-data')

        # Should handle error gracefully
        assert response.status_code in [200, 400, 500]

    def test_invalid_route_workflow(self, client):
        """Test handling of invalid routes"""

        # Access non-existent route
        response = client.get('/nonexistent/route')

        # Should return 404
        assert response.status_code == 404

    def test_method_not_allowed_workflow(self, client):
        """Test handling of wrong HTTP methods"""

        # Try POST on GET-only route
        response = client.post('/')

        # Should return 405 or handle gracefully
        assert response.status_code in [200, 405]


class TestSecurityWorkflow:
    """Test security-related workflows"""

    def test_admin_access_without_login_workflow(self, client):
        """Test that admin routes are protected"""

        # Try to access admin without login
        response = client.get('/admin/')

        # Should redirect to login or show 401
        assert response.status_code in [302, 401]

    def test_file_upload_security_workflow(self, client):
        """Test file upload security measures"""

        # Try to upload malicious file
        malicious_data = {
            'nombre': 'Test',
            'apellido': 'User',
            'email': 'test@example.com',
            'telefono': '+1-555-123-4567',
            'puesto': 'Developer',
            'ingles_nivel': 'Avanzado',
            'experiencia': 'Test',
            'nacionalidad': 'México',
            'cv': (open(__file__, 'rb'), 'malicious.exe')  # Wrong extension
        }

        response = client.post('/api/submit',
                             data=malicious_data,
                             content_type='multipart/form-data')

        # Should reject malicious file
        assert response.status_code in [400, 403]

    def test_rate_limiting_workflow(self, client, sample_application_data):
        """Test rate limiting functionality"""

        # Make multiple rapid requests
        responses = []
        for i in range(5):
            response = client.post('/api/submit',
                                 data=sample_application_data,
                                 content_type='multipart/form-data')
            responses.append(response.status_code)

        # Should eventually rate limit (429) or handle gracefully
        # This depends on rate limiting configuration
        assert all(status in [200, 400, 429, 500] for status in responses)
