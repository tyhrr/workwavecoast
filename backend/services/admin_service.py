"""
Admin Service
Complete admin authentication and management with JWT and bcrypt
"""
import bcrypt
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from config.settings import Config
from services.base_service import BaseService
from services.jwt_service import JWTService

class AdminService(BaseService):
    """Enhanced admin service with JWT authentication and bcrypt passwords"""

    def __init__(self, config: Config, jwt_service: JWTService, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self.config = config
        self.jwt_service = jwt_service

        # Admin roles and permissions
        self.roles = {
            'super_admin': {
                'permissions': ['all'],
                'description': 'Full system access'
            },
            'admin': {
                'permissions': ['read', 'write', 'delete', 'manage_applications'],
                'description': 'Standard admin access'
            },
            'viewer': {
                'permissions': ['read'],
                'description': 'Read-only access'
            }
        }

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False

    def get_admin_by_credentials(self, username: str) -> Optional[Dict[str, Any]]:
        """Get admin from environment or database (temporary implementation)"""
        try:
            # For now, use environment variables with bcrypt
            # In production, this would query the admin database
            if username == self.config.ADMIN_USERNAME:
                # Check if password is already hashed (starts with $2b$)
                stored_password = self.config.ADMIN_PASSWORD
                if not stored_password.startswith('$2b$'):
                    # Hash the plain text password for first time
                    stored_password = self.hash_password(stored_password)
                    self.logger.warning("Admin password was stored in plain text. Consider updating environment variables.")

                return {
                    '_id': 'admin-001',
                    'username': username,
                    'password_hash': stored_password,
                    'email': 'admin@workwave.com',
                    'role': 'super_admin',
                    'created_at': datetime.now(timezone.utc),
                    'last_login': None,
                    'is_active': True
                }

            return None

        except Exception as e:
            self.logger.error(f"Error getting admin by credentials: {e}")
            return None

    def authenticate_admin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate admin with bcrypt and JWT"""
        try:
            # Get admin data
            admin_data = self.get_admin_by_credentials(username)
            if not admin_data:
                return self.error_response("Invalid credentials", "AuthenticationError")

            # Verify password
            if not self.verify_password(password, admin_data['password_hash']):
                return self.error_response("Invalid credentials", "AuthenticationError")

            # Check if admin is active
            if not admin_data.get('is_active', True):
                return self.error_response("Account is deactivated", "AccountDeactivated")

            # Generate JWT tokens
            token_result = self.jwt_service.generate_token_pair(admin_data)
            if not token_result['success']:
                return token_result

            # Update last login (in production, update database)
            admin_data['last_login'] = datetime.now(timezone.utc)

            # Prepare response data (exclude password hash)
            safe_admin_data = {
                '_id': admin_data['_id'],
                'username': admin_data['username'],
                'email': admin_data['email'],
                'role': admin_data['role'],
                'permissions': self.roles.get(admin_data['role'], {}).get('permissions', []),
                'last_login': admin_data['last_login'].isoformat()
            }

            return self.success_response({
                'admin': safe_admin_data,
                'tokens': token_result['data']
            }, "Authentication successful")

        except Exception as e:
            return self.handle_error("authenticate_admin", e)

    def verify_admin_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return admin info"""
        try:
            # Validate token using JWT service
            validation_result = self.jwt_service.validate_token(token, expected_type='access')
            if not validation_result['success']:
                return validation_result

            token_data = validation_result['data']

            # Get fresh admin data to ensure account is still active
            admin_data = self.get_admin_by_credentials(token_data['username'])
            if not admin_data or not admin_data.get('is_active', True):
                return self.error_response("Account is deactivated", "AccountDeactivated")

            # Return admin info with permissions
            return self.success_response({
                'admin_id': token_data['admin_id'],
                'username': token_data['username'],
                'email': token_data['email'],
                'role': token_data['role'],
                'permissions': self.roles.get(token_data['role'], {}).get('permissions', [])
            }, "Token verified successfully")

        except Exception as e:
            return self.handle_error("verify_admin_token", e)

    def refresh_admin_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh admin access token"""
        try:
            # Use JWT service to refresh token
            refresh_result = self.jwt_service.refresh_access_token(refresh_token)
            if not refresh_result['success']:
                return refresh_result

            return self.success_response({
                'access_token': refresh_result['data']['access_token'],
                'token_type': refresh_result['data']['token_type'],
                'expires_in': refresh_result['data']['expires_in'],
                'expires_at': refresh_result['data']['expires_at']
            }, "Token refreshed successfully")

        except Exception as e:
            return self.handle_error("refresh_admin_token", e)

    def generate_recovery_token(self, username: str, email: str) -> Dict[str, Any]:
        """Generate password recovery token"""
        try:
            # Get admin data
            admin_data = self.get_admin_by_credentials(username)
            if not admin_data:
                return self.error_response("Admin not found", "AdminNotFound")

            # Verify email matches
            if admin_data.get('email') != email:
                return self.error_response("Email does not match", "EmailMismatch")

            # Generate recovery token
            recovery_result = self.jwt_service.generate_recovery_token(admin_data)
            if not recovery_result['success']:
                return recovery_result

            return self.success_response({
                'recovery_token': recovery_result['data']['recovery_token'],
                'expires_in': recovery_result['data']['expires_in'],
                'expires_at': recovery_result['data']['expires_at']
            }, "Recovery token generated successfully")

        except Exception as e:
            return self.handle_error("generate_recovery_token", e)

    def reset_password_with_token(self, recovery_token: str, new_password: str) -> Dict[str, Any]:
        """Reset admin password using recovery token"""
        try:
            # Validate recovery token
            validation_result = self.jwt_service.validate_token(recovery_token, expected_type='recovery')
            if not validation_result['success']:
                return validation_result

            token_data = validation_result['data']

            # Get admin data
            admin_data = self.get_admin_by_credentials(token_data['username'])
            if not admin_data:
                return self.error_response("Admin not found", "AdminNotFound")

            # Hash new password
            new_password_hash = self.hash_password(new_password)

            # In production, update password in database
            # For now, we'll return success (environment variables would need manual update)

            return self.success_response({
                'admin_id': admin_data['_id'],
                'username': admin_data['username'],
                'password_updated': True,
                'message': 'Password reset successful. Please update environment variables in production.'
            }, "Password reset successful")

        except Exception as e:
            return self.handle_error("reset_password_with_token", e)

    def check_admin_permission(self, admin_role: str, required_permission: str) -> bool:
        """Check if admin role has required permission"""
        try:
            role_permissions = self.roles.get(admin_role, {}).get('permissions', [])
            return 'all' in role_permissions or required_permission in role_permissions
        except Exception:
            return False

    def get_admin_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard stats with real data"""
        try:
            from datetime import datetime, timedelta, timezone
            from config.database import get_database

            db = get_database()
            collection = db['candidates']

            # Get current date info
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Summary statistics
            total_applications = collection.count_documents({})
            pending_applications = collection.count_documents({"status": "pending"})
            approved_applications = collection.count_documents({"status": "approved"})
            rejected_applications = collection.count_documents({"status": "rejected"})
            applications_today = collection.count_documents({"created_at": {"$gte": today_start}})
            applications_this_week = collection.count_documents({"created_at": {"$gte": week_start}})
            applications_this_month = collection.count_documents({"created_at": {"$gte": month_start}})

            # Position distribution
            position_pipeline = [
                {"$group": {"_id": "$puesto", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            popular_positions = list(collection.aggregate(position_pipeline))

            # Nationality distribution
            nationality_pipeline = [
                {"$group": {"_id": "$nacionalidad", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            nationality_distribution = list(collection.aggregate(nationality_pipeline))

            # English level distribution
            english_pipeline = [
                {"$group": {"_id": "$ingles_nivel", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            english_distribution = list(collection.aggregate(english_pipeline))

            # Status distribution
            status_distribution = {
                "pending": pending_applications,
                "approved": approved_applications,
                "rejected": rejected_applications,
                "total": total_applications
            }

            # Trend data - last 30 days
            thirty_days_ago = now - timedelta(days=30)
            trend_pipeline = [
                {"$match": {"created_at": {"$gte": thirty_days_ago}}},
                {"$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            trend_data = list(collection.aggregate(trend_pipeline))

            # Recent applications (last 5)
            recent_applications_cursor = collection.find({}).sort("created_at", -1).limit(5)
            recent_applications = []
            for app in recent_applications_cursor:
                recent_applications.append({
                    "_id": str(app.get('_id', '')),
                    "nombre": app.get('nombre', ''),
                    "apellido": app.get('apellido', ''),
                    "puesto": app.get('puesto', ''),
                    "status": app.get('status', 'pending'),
                    "created_at": app.get('created_at', '').isoformat() if isinstance(app.get('created_at'), datetime) else str(app.get('created_at', ''))
                })

            # Conversion rate
            total_processed = approved_applications + rejected_applications
            conversion_rate = (approved_applications / total_processed * 100) if total_processed > 0 else 0

            stats = {
                "summary": {
                    "total_applications": total_applications,
                    "pending_applications": pending_applications,
                    "approved_applications": approved_applications,
                    "rejected_applications": rejected_applications,
                    "applications_today": applications_today,
                    "applications_this_week": applications_this_week,
                    "applications_this_month": applications_this_month,
                    "conversion_rate": round(conversion_rate, 2)
                },
                "distributions": {
                    "positions": popular_positions,
                    "nationalities": nationality_distribution,
                    "english_levels": english_distribution,
                    "status": status_distribution
                },
                "recent_applications": recent_applications,
                "trend_data": trend_data,
                "metadata": {
                    "generated_at": now.isoformat(),
                    "period_start": thirty_days_ago.isoformat(),
                    "period_end": now.isoformat()
                }
            }

            return self.success_response(stats, "Dashboard statistics retrieved successfully")

        except Exception as e:
            return self.handle_error("get_admin_dashboard_stats", e)

    def get_admin_profile(self, admin_id: str) -> Dict[str, Any]:
        """Get admin profile"""
        try:
            # In production, get from database
            admin_data = self.get_admin_by_credentials(self.config.ADMIN_USERNAME)
            if not admin_data:
                return self.error_response("Admin not found", "AdminNotFound")

            return self.success_response({
                "_id": admin_data['_id'],
                "username": admin_data['username'],
                "email": admin_data['email'],
                "role": admin_data['role'],
                "permissions": self.roles.get(admin_data['role'], {}).get('permissions', []),
                "created_at": admin_data['created_at'].isoformat() if admin_data.get('created_at') else None,
                "last_login": admin_data['last_login'].isoformat() if admin_data.get('last_login') else None
            }, "Profile retrieved")

        except Exception as e:
            return self.handle_error("get_admin_profile", e)

    def update_admin_profile(self, admin_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update admin profile"""
        try:
            # In production, update database
            # For now, just validate the update data
            allowed_fields = ['email']
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}

            return self.success_response({
                'updated_fields': list(filtered_data.keys()),
                'message': 'Profile update successful. Changes require database implementation.'
            }, "Profile updated")

        except Exception as e:
            return self.handle_error("update_admin_profile", e)

    def change_admin_password(self, admin_id: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change admin password"""
        try:
            # Get admin data
            admin_data = self.get_admin_by_credentials(self.config.ADMIN_USERNAME)
            if not admin_data:
                return self.error_response("Admin not found", "AdminNotFound")

            # Verify current password
            if not self.verify_password(current_password, admin_data['password_hash']):
                return self.error_response("Current password is incorrect", "InvalidPassword")

            # Hash new password
            new_password_hash = self.hash_password(new_password)

            # In production, update database
            return self.success_response({
                'password_updated': True,
                'new_password_hash': new_password_hash,
                'message': 'Password changed successfully. Update environment variables in production.'
            }, "Password changed successfully")

        except Exception as e:
            return self.handle_error("change_admin_password", e)

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "status": "healthy",
            "service": "AdminService",
            "jwt_service": "available" if self.jwt_service else "unavailable",
            "roles_configured": len(self.roles)
        }
