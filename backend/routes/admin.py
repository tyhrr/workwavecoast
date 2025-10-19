"""
Updated Admin Routes
Flask routes for admin operations with JWT authentication
"""
import logging
from flask import Blueprint, request, jsonify, g
from typing import Dict, Any

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Global services (will be injected from app.py)
admin_service = None
application_service = None
audit_service = None
rbac_middleware = None

def init_admin_routes(admin_svc, app_svc, audit_svc, rbac_mw, logger: logging.Logger):
    """Initialize admin routes with services"""
    global admin_service, application_service, audit_service, rbac_middleware
    admin_service = admin_svc
    application_service = app_svc
    audit_service = audit_svc
    rbac_middleware = rbac_mw

def require_admin_auth(f):
    """Decorator wrapper for rbac_middleware.require_admin_auth"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if rbac_middleware is None:
            raise RuntimeError("RBAC middleware not initialized")
        return rbac_middleware.require_admin_auth(f)(*args, **kwargs)
    return decorated_function

def require_permission(permission):
    """Decorator wrapper for rbac_middleware.require_permission"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if rbac_middleware is None:
                raise RuntimeError("RBAC middleware not initialized")
            return rbac_middleware.require_permission(permission)(f)(*args, **kwargs)
        return decorated_function
    return decorator

def optional_admin_auth(f):
    """Decorator wrapper for rbac_middleware.optional_admin_auth"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if rbac_middleware is None:
            raise RuntimeError("RBAC middleware not initialized")
        return rbac_middleware.optional_admin_auth(f)(*args, **kwargs)
    return decorated_function

@admin_bp.route('/auth/login', methods=['POST'])
def login():
    """Admin login with JWT authentication"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required',
                'error_type': 'InvalidRequest'
            }), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required',
                'error_type': 'MissingCredentials'
            }), 400

        # Authenticate admin
        auth_result = admin_service.authenticate_admin(username, password)
        if not auth_result['success']:
            # Log failed login attempt
            if audit_service:
                audit_service.log_authentication_failure(
                    username=username,
                    reason=auth_result.get('message', 'Unknown error'),
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )

            return jsonify(auth_result), 401

        auth_data = auth_result['data']
        admin_info = auth_data['admin']
        tokens = auth_data['tokens']

        # Log successful login
        if audit_service:
            audit_service.log_authentication_success(
                admin_id=admin_info['_id'],
                username=admin_info['username'],
                role=admin_info['role'],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'admin': admin_info,
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'token_type': tokens['token_type'],
                'access_expires_in': tokens['access_expires_in'],
                'refresh_expires_in': tokens['refresh_expires_in']
            }
        }), 200

    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required',
                'error_type': 'InvalidRequest'
            }), 400

        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify({
                'success': False,
                'message': 'Refresh token is required',
                'error_type': 'MissingToken'
            }), 400

        # Refresh token
        refresh_result = admin_service.refresh_admin_token(refresh_token)
        if not refresh_result['success']:
            return jsonify(refresh_result), 401

        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'data': refresh_result['data']
        }), 200

    except Exception as e:
        logging.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/auth/logout', methods=['POST'])
@require_admin_auth
def logout():
    """Admin logout (revoke tokens)"""
    try:
        # Get current admin info
        admin_info = g.current_admin

        # Log logout
        if audit_service:
            audit_service.log_logout(
                admin_id=admin_info['admin_id'],
                username=admin_info['username'],
                role=admin_info['role'],
                ip_address=request.remote_addr
            )

        # In a production system, we would add the token to a blacklist
        # For now, we'll just return success
        return jsonify({
            'success': True,
            'message': 'Logout successful',
            'data': {
                'logged_out_at': auth_result['data'].get('timestamp')
            }
        }), 200

    except Exception as e:
        logging.error(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/auth/verify', methods=['POST'])
@require_admin_auth
def verify_token():
    """Verify current token and return admin info"""
    try:
        admin_info = g.current_admin

        return jsonify({
            'success': True,
            'message': 'Token is valid',
            'data': {
                'admin': admin_info,
                'authenticated': True
            }
        }), 200

    except Exception as e:
        logging.error(f"Token verification error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/dashboard', methods=['GET'])
@require_admin_auth
def dashboard():
    """Get admin dashboard data"""
    try:
        # Get dashboard statistics
        stats_result = admin_service.get_admin_dashboard_stats()
        if not stats_result['success']:
            return jsonify(stats_result), 500

        # Log dashboard access
        if audit_service:
            rbac_middleware.log_admin_action('dashboard_access', {
                'endpoint': '/admin/dashboard',
                'method': 'GET'
            })

        return jsonify({
            'success': True,
            'message': 'Dashboard data retrieved successfully',
            'data': {
                'admin': g.current_admin,
                'stats': stats_result['data']
            }
        }), 200

    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/profile', methods=['GET'])
@require_admin_auth
def get_profile():
    """Get admin profile"""
    try:
        admin_id = g.current_admin_id

        profile_result = admin_service.get_admin_profile(admin_id)
        if not profile_result['success']:
            return jsonify(profile_result), 500

        return jsonify({
            'success': True,
            'message': 'Profile retrieved successfully',
            'data': profile_result['data']
        }), 200

    except Exception as e:
        logging.error(f"Get profile error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/profile', methods=['PUT'])
@require_admin_auth
def update_profile():
    """Update admin profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required',
                'error_type': 'InvalidRequest'
            }), 400

        admin_id = g.current_admin_id

        # Update profile
        update_result = admin_service.update_admin_profile(admin_id, data)
        if not update_result['success']:
            return jsonify(update_result), 400

        # Log profile update
        if audit_service:
            rbac_middleware.log_admin_action('profile_update', {
                'updated_fields': list(data.keys()),
                'admin_id': admin_id
            })

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': update_result['data']
        }), 200

    except Exception as e:
        logging.error(f"Update profile error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/applications', methods=['GET'])
@require_admin_auth
@require_permission('read')
def get_applications():
    """Get applications with admin-specific filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 100, type=int), 100)
        status = request.args.get('status')
        position = request.args.get('position')

        # Build query params for ApplicationService
        query_params = {
            'page': page,
            'per_page': per_page
        }

        if status:
            query_params['status'] = status
        if position:
            query_params['puesto'] = position

        # Get applications from database using application_service
        if application_service:
            result = application_service.get_applications(query_params=query_params)

            if not result['success']:
                return jsonify(result), 500

            # Log applications access
            if audit_service:
                rbac_middleware.log_admin_action('applications_access', {
                    'page': page,
                    'per_page': per_page,
                    'status': status,
                    'position': position,
                    'total_found': result.get('data', {}).get('total', 0)
                })

            return jsonify(result), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Application service not available',
                'error_type': 'ServiceError'
            }), 500

    except Exception as e:
        logging.error(f"Get applications error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/applications/<application_id>', methods=['GET'])
@require_admin_auth
@require_permission('read')
def get_application(application_id: str):
    """Get single application with admin details"""
    try:
        # Log application access
        if audit_service:
            audit_service.log_application_action(
                admin_id=g.current_admin_id,
                username=g.current_admin['username'],
                role=g.current_admin_role,
                action='view',
                application_id=application_id,
                ip_address=request.remote_addr
            )

        # For now, return mock data structure
        return jsonify({
            'success': True,
            'message': 'Application retrieved successfully',
            'data': {
                'application_id': application_id,
                'status': 'pending',
                'details': 'Application details would be here'
            }
        }), 200

    except Exception as e:
        logging.error(f"Get application error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/audit/logs', methods=['GET'])
@require_admin_auth
@require_permission('read')
def get_audit_logs():
    """Get audit logs (admin only)"""
    try:
        # Parse query parameters
        admin_id = request.args.get('admin_id')
        event_type = request.args.get('event_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = min(request.args.get('limit', 100, type=int), 1000)
        offset = request.args.get('offset', 0, type=int)

        # Convert date strings to datetime if provided
        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                from datetime import datetime
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_date format. Use ISO format.',
                    'error_type': 'InvalidDate'
                }), 400

        if end_date:
            try:
                from datetime import datetime
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_date format. Use ISO format.',
                    'error_type': 'InvalidDate'
                }), 400

        # Get audit logs
        if audit_service:
            logs_result = audit_service.get_audit_logs(
                admin_id=admin_id,
                event_type=getattr(audit_service.AuditEventType, event_type) if event_type else None,
                start_date=start_datetime,
                end_date=end_datetime,
                limit=limit,
                offset=offset
            )

            if not logs_result['success']:
                return jsonify(logs_result), 500

            # Log audit access
            rbac_middleware.log_admin_action('audit_logs_access', {
                'filters': {
                    'admin_id': admin_id,
                    'event_type': event_type,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'pagination': {'limit': limit, 'offset': offset}
            })

            return jsonify({
                'success': True,
                'message': 'Audit logs retrieved successfully',
                'data': logs_result['data']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Audit service not available',
                'error_type': 'ServiceUnavailable'
            }), 503

    except Exception as e:
        logging.error(f"Get audit logs error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/health', methods=['GET'])
@optional_admin_auth
def health_check():
    """Health check endpoint"""
    try:
        # Check if admin is authenticated (optional)
        is_authenticated = hasattr(g, 'current_admin') and g.current_admin is not None

        health_data = {
            'status': 'healthy',
            'timestamp': '2024-01-01T00:00:00Z',
            'services': {
                'admin_service': admin_service.health_check() if admin_service else None,
                'audit_service': 'available' if audit_service else 'unavailable'
            },
            'authenticated': is_authenticated
        }

        if is_authenticated:
            health_data['admin_info'] = {
                'username': g.current_admin['username'],
                'role': g.current_admin['role']
            }

        return jsonify({
            'success': True,
            'message': 'Admin service is healthy',
            'data': health_data
        }), 200

    except Exception as e:
        logging.error(f"Health check error: {e}")
        return jsonify({
            'success': False,
            'message': 'Health check failed',
            'error_type': 'HealthCheckError'
        }), 500

@admin_bp.route('/applications/search', methods=['GET'])
@require_admin_auth
@require_permission('read')
def search_applications():
    """Search applications with full-text search and filters"""
    try:
        # Get search query and filters
        search_query = request.args.get('q', '').strip()

        filters = {
            'status': request.args.get('status'),
            'position': request.args.get('position'),
            'nationality': request.args.get('nationality'),
            'english_level': request.args.get('english_level'),
            'from_date': request.args.get('from_date'),
            'to_date': request.args.get('to_date'),
            'page': request.args.get('page', 1, type=int),
            'per_page': min(request.args.get('per_page', 20, type=int), 100)
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        # Perform search
        result = application_service.search_applications(search_query, filters)

        if result['success']:
            # Log search action
            if audit_service:
                rbac_middleware.log_admin_action('applications_search', {
                    'search_query': search_query,
                    'filters': filters,
                    'results_count': len(result['data']['applications'])
                })

            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logging.error(f"Search applications error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/applications/export', methods=['GET'])
@require_admin_auth
@require_permission('read')
def export_applications():
    """Export applications to CSV or Excel"""
    try:
        # Get export format and filters
        format = request.args.get('format', 'excel').lower()

        filters = {
            'status': request.args.get('status'),
            'position': request.args.get('position'),
            'nationality': request.args.get('nationality'),
            'english_level': request.args.get('english_level'),
            'from_date': request.args.get('from_date'),
            'to_date': request.args.get('to_date')
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        # Perform export
        result = application_service.export_applications(format, filters)

        if result['success']:
            # Log export action
            if audit_service:
                rbac_middleware.log_admin_action('applications_export', {
                    'format': format,
                    'filters': filters,
                    'count': result['data']['count']
                })

            return jsonify(result), 200
        else:
            return jsonify(result), 400 if result.get('error_type') == 'NoDataFound' else 500

    except Exception as e:
        logging.error(f"Export applications error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/applications/filters', methods=['GET'])
@require_admin_auth
@require_permission('read')
def get_filter_options():
    """Get available options for advanced filters"""
    try:
        result = application_service.get_advanced_filters_options()

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logging.error(f"Get filter options error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/applications/<application_id>/status', methods=['PUT'])
@require_admin_auth
@require_permission('write')
def update_application_status(application_id):
    """Update application status and send notification email"""
    try:
        from services.email_service import EmailService

        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'message': 'Status is required',
                'error_type': 'InvalidRequest'
            }), 400

        new_status = data['status']
        send_notification = data.get('send_notification', True)  # Default to True

        # Get current application data
        app_result = application_service.get_application_by_id(application_id)
        if not app_result['success']:
            return jsonify(app_result), 404

        application_data = app_result['data']
        old_status = application_data.get('status', 'pending')

        # Update status
        update_result = application_service.update_application_status(application_id, new_status)

        if not update_result['success']:
            return jsonify(update_result), 400

        # Send notification email if requested and status changed
        email_sent = False
        if send_notification and old_status != new_status:
            email_service = EmailService()
            email_result = email_service.send_application_status_change_email(
                application_data,
                new_status,
                old_status
            )
            email_sent = email_result.get('success', False)

        # Log status change
        if audit_service:
            rbac_middleware.log_admin_action('application_status_update', {
                'application_id': application_id,
                'old_status': old_status,
                'new_status': new_status,
                'notification_sent': email_sent
            })

        return jsonify({
            'success': True,
            'message': 'Application status updated successfully',
            'data': {
                'application_id': application_id,
                'old_status': old_status,
                'new_status': new_status,
                'notification_sent': email_sent,
                'updated_at': update_result['data'].get('updated_at')
            }
        }), 200

    except Exception as e:
        logging.error(f"Update application status error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/applications/<application_id>/approve', methods=['POST'])
@require_admin_auth
@require_permission('write')
def approve_application(application_id):
    """Approve application and send notification"""
    try:
        from services.email_service import EmailService

        data = request.get_json() or {}
        send_notification = data.get('send_notification', True)
        notes = data.get('notes', '')

        # Get application data
        app_result = application_service.get_application_by_id(application_id)
        if not app_result['success']:
            return jsonify(app_result), 404

        application_data = app_result['data']

        # Update status to approved
        update_result = application_service.update_application_status(application_id, 'approved')

        if not update_result['success']:
            return jsonify(update_result), 400

        # Send notification email
        email_sent = False
        if send_notification:
            email_service = EmailService()
            email_result = email_service.send_application_approved_email(application_data)
            email_sent = email_result.get('success', False)

        # Log approval
        if audit_service:
            rbac_middleware.log_admin_action('application_approved', {
                'application_id': application_id,
                'candidate_email': application_data.get('email'),
                'notification_sent': email_sent,
                'notes': notes
            })

        return jsonify({
            'success': True,
            'message': 'Application approved successfully',
            'data': {
                'application_id': application_id,
                'status': 'approved',
                'notification_sent': email_sent,
                'approved_by': g.current_admin['username'],
                'approved_at': update_result['data'].get('updated_at')
            }
        }), 200

    except Exception as e:
        logging.error(f"Approve application error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@admin_bp.route('/applications/<application_id>/reject', methods=['POST'])
@require_admin_auth
@require_permission('write')
def reject_application(application_id):
    """Reject application and send notification"""
    try:
        from services.email_service import EmailService

        data = request.get_json() or {}
        send_notification = data.get('send_notification', True)
        notes = data.get('notes', '')

        # Get application data
        app_result = application_service.get_application_by_id(application_id)
        if not app_result['success']:
            return jsonify(app_result), 404

        application_data = app_result['data']

        # Update status to rejected
        update_result = application_service.update_application_status(application_id, 'rejected')

        if not update_result['success']:
            return jsonify(update_result), 400

        # Send notification email
        email_sent = False
        if send_notification:
            email_service = EmailService()
            email_result = email_service.send_application_rejected_email(application_data)
            email_sent = email_result.get('success', False)

        # Log rejection
        if audit_service:
            rbac_middleware.log_admin_action('application_rejected', {
                'application_id': application_id,
                'candidate_email': application_data.get('email'),
                'notification_sent': email_sent,
                'notes': notes
            })

        return jsonify({
            'success': True,
            'message': 'Application rejected',
            'data': {
                'application_id': application_id,
                'status': 'rejected',
                'notification_sent': email_sent,
                'rejected_by': g.current_admin['username'],
                'rejected_at': update_result['data'].get('updated_at')
            }
        }), 200

    except Exception as e:
        logging.error(f"Reject application error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

