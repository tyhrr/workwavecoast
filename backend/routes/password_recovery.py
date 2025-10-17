"""
Password Recovery Routes
Routes for admin password recovery functionality
"""
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

# Blueprint definition
password_recovery_bp = Blueprint('password_recovery', __name__, url_prefix='/api/admin/auth')

# Global services (will be injected from app.py)
admin_service = None
jwt_service = None
email_service = None
audit_service = None

def init_password_recovery_routes(admin_svc, jwt_svc, email_svc, audit_svc, logger: logging.Logger):
    """Initialize password recovery routes with services"""
    global admin_service, jwt_service, email_service, audit_service
    admin_service = admin_svc
    jwt_service = jwt_svc
    email_service = email_svc
    audit_service = audit_svc

@password_recovery_bp.route('/forgot-password', methods=['POST'])
def request_password_reset():
    """Request password reset token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required',
                'error_type': 'InvalidRequest'
            }), 400

        username = data.get('username')
        email = data.get('email')

        if not username or not email:
            return jsonify({
                'success': False,
                'message': 'Username and email are required',
                'error_type': 'MissingFields'
            }), 400

        # Generate recovery token
        recovery_result = admin_service.generate_recovery_token(username, email)
        if not recovery_result['success']:
            # Log failed attempt
            if audit_service:
                audit_service.log_event(
                    event_type=audit_service.AuditEventType.PASSWORD_RESET_REQUEST,
                    username=username,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    level=audit_service.AuditLogLevel.WARNING,
                    details={'success': False, 'reason': recovery_result.get('message')}
                )

            return jsonify(recovery_result), 400

        recovery_token = recovery_result['data']['recovery_token']
        expires_at = recovery_result['data']['expires_at']

        # Send recovery email
        try:
            if email_service:
                # Create recovery link (in production, this would be your frontend URL)
                recovery_link = f"https://workwave.com/admin/reset-password?token={recovery_token}"

                email_result = email_service.send_password_recovery_email(
                    email=email,
                    username=username,
                    recovery_link=recovery_link,
                    expires_at=expires_at
                )

                if not email_result['success']:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to send recovery email',
                        'error_type': 'EmailError',
                        'details': email_result.get('message')
                    }), 500
        except Exception as e:
            # Even if email fails, we don't want to reveal the token
            logging.error(f"Failed to send recovery email: {e}")

        # Log successful request
        if audit_service:
            audit_service.log_event(
                event_type=audit_service.AuditEventType.PASSWORD_RESET_REQUEST,
                username=username,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details={'success': True, 'email_sent': True}
            )

        # Return success without exposing the token
        return jsonify({
            'success': True,
            'message': 'If the username and email are correct, a password reset link has been sent to your email.',
            'data': {
                'email': email,
                'expires_in_minutes': 30  # Recovery tokens expire in 30 minutes
            }
        }), 200

    except Exception as e:
        logging.error(f"Password reset request error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@password_recovery_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using recovery token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required',
                'error_type': 'InvalidRequest'
            }), 400

        recovery_token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not recovery_token or not new_password or not confirm_password:
            return jsonify({
                'success': False,
                'message': 'Recovery token, new password, and password confirmation are required',
                'error_type': 'MissingFields'
            }), 400

        # Validate password confirmation
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Password confirmation does not match',
                'error_type': 'PasswordMismatch'
            }), 400

        # Validate password strength (basic validation)
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long',
                'error_type': 'WeakPassword'
            }), 400

        # Reset password using token
        reset_result = admin_service.reset_password_with_token(recovery_token, new_password)
        if not reset_result['success']:
            # Log failed attempt
            if audit_service:
                audit_service.log_event(
                    event_type=audit_service.AuditEventType.PASSWORD_RESET_SUCCESS,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    level=audit_service.AuditLogLevel.WARNING,
                    details={'success': False, 'reason': reset_result.get('message')}
                )

            return jsonify(reset_result), 400

        admin_data = reset_result['data']

        # Log successful password reset
        if audit_service:
            audit_service.log_event(
                event_type=audit_service.AuditEventType.PASSWORD_RESET_SUCCESS,
                admin_id=admin_data['admin_id'],
                username=admin_data['username'],
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                level=audit_service.AuditLogLevel.WARNING,
                details={'success': True}
            )

        # Send confirmation email
        try:
            if email_service:
                email_service.send_password_reset_confirmation_email(
                    email=admin_data.get('email', ''),
                    username=admin_data['username']
                )
        except Exception as e:
            logging.error(f"Failed to send password reset confirmation email: {e}")

        return jsonify({
            'success': True,
            'message': 'Password has been reset successfully. You can now log in with your new password.',
            'data': {
                'username': admin_data['username'],
                'reset_at': reset_result['data'].get('timestamp')
            }
        }), 200

    except Exception as e:
        logging.error(f"Password reset error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@password_recovery_bp.route('/validate-recovery-token', methods=['POST'])
def validate_recovery_token():
    """Validate recovery token without resetting password"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required',
                'error_type': 'InvalidRequest'
            }), 400

        recovery_token = data.get('token')
        if not recovery_token:
            return jsonify({
                'success': False,
                'message': 'Recovery token is required',
                'error_type': 'MissingToken'
            }), 400

        # Validate token using JWT service
        validation_result = jwt_service.validate_token(recovery_token, expected_type='recovery')
        if not validation_result['success']:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired recovery token',
                'error_type': 'InvalidToken',
                'details': validation_result.get('message')
            }), 400

        token_data = validation_result['data']

        return jsonify({
            'success': True,
            'message': 'Recovery token is valid',
            'data': {
                'valid': True,
                'username': token_data['username'],
                'email': token_data['email'],
                'expires_at': token_data['expires_at'],
                'time_remaining_seconds': validation_result['data'].get('time_until_expiry_seconds', 0)
            }
        }), 200

    except Exception as e:
        logging.error(f"Recovery token validation error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500

@password_recovery_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change password for authenticated admin"""
    try:
        # This endpoint requires authentication - will be handled by RBAC middleware
        from flask import g

        # For now, we'll implement a basic check since we don't have the decorator here
        # In production, this would use the require_admin_auth decorator
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error_type': 'NotAuthenticated'
            }), 401        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required',
                'error_type': 'InvalidRequest'
            }), 400

        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return jsonify({
                'success': False,
                'message': 'Current password, new password, and password confirmation are required',
                'error_type': 'MissingFields'
            }), 400

        # Validate password confirmation
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Password confirmation does not match',
                'error_type': 'PasswordMismatch'
            }), 400

        # Validate password strength
        if len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long',
                'error_type': 'WeakPassword'
            }), 400

        admin_id = g.current_admin['admin_id']
        username = g.current_admin['username']
        role = g.current_admin['role']

        # Change password
        change_result = admin_service.change_admin_password(admin_id, current_password, new_password)
        if not change_result['success']:
            # Log failed attempt
            if audit_service:
                audit_service.log_permission_denied(
                    admin_id=admin_id,
                    username=username,
                    role=role,
                    required_permission='change_password',
                    attempted_action='password_change',
                    ip_address=request.remote_addr
                )

            return jsonify(change_result), 400

        # Log successful password change
        if audit_service:
            audit_service.log_password_change(
                admin_id=admin_id,
                username=username,
                role=role,
                ip_address=request.remote_addr
            )

        return jsonify({
            'success': True,
            'message': 'Password changed successfully',
            'data': {
                'changed_at': change_result['data'].get('timestamp')
            }
        }), 200

    except Exception as e:
        logging.error(f"Password change error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error_type': 'ServerError'
        }), 500
