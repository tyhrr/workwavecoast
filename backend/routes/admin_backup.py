"""
Admin Routes
Flask routes for admin operations and authentication
"""
import logging
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from functools import wraps
from services import AdminService, ApplicationService
from middleware import (
    admin_required,
    jwt_required,
    handle_api_errors,
    validate_admin_login,
    log_user_actions,
    log_requests
)

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
admin_service = AdminService(logger)
app_service = ApplicationService(logger)


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin is logged in via session
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            if request.is_json or request.endpoint.startswith('admin.api_'):
                return jsonify({
                    "success": False,
                    "message": "Authentication required"
                }), 401
            else:
                return redirect(url_for('admin.login'))

        # For API endpoints, also check JWT token
        if request.is_json or request.endpoint.startswith('admin.api_'):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    "success": False,
                    "message": "Invalid authorization header"
                }), 401

            token = auth_header.split(' ')[1]
            token_result = admin_service.verify_admin_token(token)
            if not token_result.get('success'):
                return jsonify(token_result), 401

            # Add admin info to request context
            request.admin = token_result['data']

        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'GET':
        # Check if already logged in
        if session.get('admin_logged_in'):
            return redirect(url_for('admin.dashboard'))

        return render_template('admin_login.html')

    elif request.method == 'POST':
        try:
            # Get credentials
            if request.is_json:
                data = request.get_json()
                username = data.get('username', '').strip()
                password = data.get('password', '')
            else:
                username = request.form.get('username', '').strip()
                password = request.form.get('password', '')

            logger.info("Admin login attempt", extra={
                "username": username,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get('User-Agent')
            })

            # Validate credentials
            if not username or not password:
                error_msg = "Username and password are required"
                if request.is_json:
                    return jsonify({
                        "success": False,
                        "message": error_msg
                    }), 400
                else:
                    flash(error_msg, 'error')
                    return render_template('admin_login.html')

            # Authenticate using service
            auth_result = admin_service.authenticate_admin(username, password)

            if auth_result.get('success'):
                # Set session
                session['admin_logged_in'] = True
                session['admin_id'] = auth_result['data']['admin']['_id']
                session['admin_username'] = auth_result['data']['admin']['username']

                logger.info("Admin login successful", extra={
                    "username": username,
                    "remote_addr": request.remote_addr
                })

                if request.is_json:
                    return jsonify(auth_result), 200
                else:
                    flash("Login successful", 'success')
                    return redirect(url_for('admin.dashboard'))

            else:
                logger.warning("Admin login failed", extra={
                    "username": username,
                    "remote_addr": request.remote_addr,
                    "reason": auth_result.get('message')
                })

                if request.is_json:
                    return jsonify(auth_result), 401
                else:
                    flash("Invalid credentials", 'error')
                    return render_template('admin_login.html')

        except Exception as e:
            logger.error("Error in admin login", extra={
                "error": str(e),
                "username": username if 'username' in locals() else 'unknown',
                "remote_addr": request.remote_addr
            })

            if request.is_json:
                return jsonify({
                    "success": False,
                    "message": "Internal server error"
                }), 500
            else:
                flash("An error occurred", 'error')
                return render_template('admin_login.html')


@admin_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Admin logout"""
    session.clear()

    if request.is_json:
        return jsonify({
            "success": True,
            "message": "Logged out successfully"
        }), 200
    else:
        flash("You have been logged out", 'info')
        return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    try:
        logger.info("Admin dashboard accessed", extra={
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent')
        })

        # Get dashboard statistics
        stats_result = admin_service.get_admin_dashboard_stats()

        if stats_result.get('success'):
            stats = stats_result['data']
        else:
            logger.error("Failed to get dashboard stats", extra={
                "error": stats_result.get('message')
            })
            stats = {}

        return render_template('admin_dashboard.html', stats=stats)

    except Exception as e:
        logger.error("Error in admin dashboard", extra={
            "error": str(e),
            "admin_id": session.get('admin_id'),
            "remote_addr": request.remote_addr
        })
        flash("Error loading dashboard", 'error')
        return render_template('admin_dashboard.html', stats={})


# API Routes for admin operations
@admin_bp.route('/api/stats', methods=['GET'])
@admin_required
def api_get_stats():
    """Get dashboard statistics via API"""
    try:
        result = admin_service.get_admin_dashboard_stats()

        if result.get('success'):
            return jsonify(result['data']), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error getting admin stats", extra={
            "error": str(e),
            "admin_id": getattr(request, 'admin', {}).get('admin_id')
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@admin_bp.route('/api/profile', methods=['GET'])
@admin_required
def api_get_profile():
    """Get admin profile via API"""
    try:
        admin_id = getattr(request, 'admin', {}).get('admin_id')
        if not admin_id:
            return jsonify({
                "success": False,
                "message": "Admin ID not found"
            }), 400

        result = admin_service.get_admin_profile(admin_id)

        if result.get('success'):
            return jsonify(result['data']), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error getting admin profile", extra={
            "error": str(e),
            "admin_id": getattr(request, 'admin', {}).get('admin_id')
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@admin_bp.route('/api/profile', methods=['PUT'])
@admin_required
def api_update_profile():
    """Update admin profile via API"""
    try:
        admin_id = getattr(request, 'admin', {}).get('admin_id')
        if not admin_id:
            return jsonify({
                "success": False,
                "message": "Admin ID not found"
            }), 400

        update_data = request.get_json()
        if not update_data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        result = admin_service.update_admin_profile(admin_id, update_data)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error updating admin profile", extra={
            "error": str(e),
            "admin_id": getattr(request, 'admin', {}).get('admin_id')
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@admin_bp.route('/api/change-password', methods=['POST'])
@admin_required
def api_change_password():
    """Change admin password via API"""
    try:
        admin_id = getattr(request, 'admin', {}).get('admin_id')
        if not admin_id:
            return jsonify({
                "success": False,
                "message": "Admin ID not found"
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({
                "success": False,
                "message": "Current and new passwords are required"
            }), 400

        result = admin_service.change_admin_password(admin_id, current_password, new_password)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error changing admin password", extra={
            "error": str(e),
            "admin_id": getattr(request, 'admin', {}).get('admin_id')
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@admin_bp.route('/api/applications/<string:application_id>', methods=['DELETE'])
@admin_required
def api_delete_application(application_id):
    """Delete an application via API"""
    try:
        result = app_service.delete_application(application_id)

        if result.get('success'):
            logger.info("Application deleted by admin", extra={
                "application_id": application_id,
                "admin_id": getattr(request, 'admin', {}).get('admin_id')
            })
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error deleting application via admin", extra={
            "error": str(e),
            "application_id": application_id,
            "admin_id": getattr(request, 'admin', {}).get('admin_id')
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@admin_bp.route('/api/applications/bulk-delete', methods=['POST'])
@admin_required
def api_bulk_delete_applications():
    """Bulk delete applications via API"""
    try:
        data = request.get_json()
        if not data or not data.get('application_ids'):
            return jsonify({
                "success": False,
                "message": "No application IDs provided"
            }), 400

        application_ids = data['application_ids']
        if not isinstance(application_ids, list):
            return jsonify({
                "success": False,
                "message": "Application IDs must be a list"
            }), 400

        result = app_service.delete_multiple_applications(application_ids)

        if result.get('success'):
            logger.info("Applications bulk deleted by admin", extra={
                "count": len(application_ids),
                "admin_id": getattr(request, 'admin', {}).get('admin_id')
            })
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error in admin bulk delete", extra={
            "error": str(e),
            "admin_id": getattr(request, 'admin', {}).get('admin_id')
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


# Error handlers for this blueprint
@admin_bp.errorhandler(401)
def unauthorized(error):
    if request.is_json:
        return jsonify({
            "success": False,
            "message": "Authentication required"
        }), 401
    else:
        return redirect(url_for('admin.login'))


@admin_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "message": "Access forbidden"
    }), 403


@admin_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "Resource not found"
    }), 404


@admin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500
