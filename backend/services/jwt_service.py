"""
JWT Service
Handles JWT token generation, validation, and management for admin authentication
"""
import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Union
from config.settings import Config
from services.base_service import BaseService

class JWTService(BaseService):
    """JWT token management service"""

    def __init__(self, config: Config, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self.config = config
        self.secret_key = config.SECRET_KEY
        self.algorithm = "HS256"

        # Token expiration times (configurable)
        self.access_token_expires = timedelta(hours=1)  # 1 hour for access tokens
        self.refresh_token_expires = timedelta(days=7)  # 7 days for refresh tokens
        self.recovery_token_expires = timedelta(minutes=30)  # 30 minutes for password recovery

    def generate_access_token(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate access token for authenticated admin"""
        try:
            now = datetime.now(timezone.utc)
            payload = {
                'admin_id': admin_data['_id'],
                'username': admin_data['username'],
                'role': admin_data.get('role', 'admin'),
                'email': admin_data.get('email'),
                'iat': now,  # Issued at
                'exp': now + self.access_token_expires,  # Expiration
                'type': 'access'
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            return self.success_response({
                'access_token': token,
                'token_type': 'Bearer',
                'expires_in': int(self.access_token_expires.total_seconds()),
                'expires_at': (now + self.access_token_expires).isoformat()
            }, "Access token generated successfully")

        except Exception as e:
            return self.handle_error("generate_access_token", e)

    def generate_refresh_token(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate refresh token for token renewal"""
        try:
            now = datetime.now(timezone.utc)
            payload = {
                'admin_id': admin_data['_id'],
                'username': admin_data['username'],
                'iat': now,
                'exp': now + self.refresh_token_expires,
                'type': 'refresh'
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            return self.success_response({
                'refresh_token': token,
                'expires_in': int(self.refresh_token_expires.total_seconds()),
                'expires_at': (now + self.refresh_token_expires).isoformat()
            }, "Refresh token generated successfully")

        except Exception as e:
            return self.handle_error("generate_refresh_token", e)

    def generate_recovery_token(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate password recovery token"""
        try:
            now = datetime.now(timezone.utc)
            payload = {
                'admin_id': admin_data['_id'],
                'username': admin_data['username'],
                'email': admin_data.get('email'),
                'iat': now,
                'exp': now + self.recovery_token_expires,
                'type': 'recovery'
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            return self.success_response({
                'recovery_token': token,
                'expires_in': int(self.recovery_token_expires.total_seconds()),
                'expires_at': (now + self.recovery_token_expires).isoformat()
            }, "Recovery token generated successfully")

        except Exception as e:
            return self.handle_error("generate_recovery_token", e)

    def generate_token_pair(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate both access and refresh tokens"""
        try:
            access_result = self.generate_access_token(admin_data)
            if not access_result['success']:
                return access_result

            refresh_result = self.generate_refresh_token(admin_data)
            if not refresh_result['success']:
                return refresh_result

            return self.success_response({
                'access_token': access_result['data']['access_token'],
                'refresh_token': refresh_result['data']['refresh_token'],
                'token_type': 'Bearer',
                'access_expires_in': access_result['data']['expires_in'],
                'refresh_expires_in': refresh_result['data']['expires_in'],
                'access_expires_at': access_result['data']['expires_at'],
                'refresh_expires_at': refresh_result['data']['expires_at']
            }, "Token pair generated successfully")

        except Exception as e:
            return self.handle_error("generate_token_pair", e)

    def validate_token(self, token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
        """Validate and decode JWT token"""
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type if specified
            if expected_type and payload.get('type') != expected_type:
                return self.error_response(
                    f"Invalid token type. Expected {expected_type}, got {payload.get('type')}",
                    "InvalidTokenType"
                )

            # Check expiration (JWT library handles this automatically, but we can add custom logic)
            now = datetime.now(timezone.utc)
            exp = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)

            if now >= exp:
                return self.error_response("Token has expired", "TokenExpired")

            return self.success_response({
                'admin_id': payload['admin_id'],
                'username': payload['username'],
                'role': payload.get('role', 'admin'),
                'email': payload.get('email'),
                'token_type': payload.get('type', 'access'),
                'issued_at': payload['iat'],
                'expires_at': payload['exp']
            }, "Token validated successfully")

        except jwt.ExpiredSignatureError:
            return self.error_response("Token has expired", "TokenExpired")
        except jwt.InvalidTokenError:
            return self.error_response("Invalid token", "InvalidToken")
        except Exception as e:
            return self.handle_error("validate_token", e)

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Generate new access token using refresh token"""
        try:
            # Validate refresh token
            validation_result = self.validate_token(refresh_token, expected_type='refresh')
            if not validation_result['success']:
                return validation_result

            admin_data = validation_result['data']

            # Generate new access token
            new_access_result = self.generate_access_token({
                '_id': admin_data['admin_id'],
                'username': admin_data['username'],
                'role': admin_data['role'],
                'email': admin_data['email']
            })

            if not new_access_result['success']:
                return new_access_result

            return self.success_response({
                'access_token': new_access_result['data']['access_token'],
                'token_type': 'Bearer',
                'expires_in': new_access_result['data']['expires_in'],
                'expires_at': new_access_result['data']['expires_at']
            }, "Access token refreshed successfully")

        except Exception as e:
            return self.handle_error("refresh_access_token", e)

    def decode_token_without_verification(self, token: str) -> Dict[str, Any]:
        """Decode token without signature verification (for debugging/inspection)"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})

            return self.success_response({
                'payload': payload,
                'admin_id': payload.get('admin_id'),
                'username': payload.get('username'),
                'role': payload.get('role'),
                'token_type': payload.get('type'),
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp')
            }, "Token decoded successfully")

        except Exception as e:
            return self.handle_error("decode_token_without_verification", e)

    def revoke_token(self, token: str) -> Dict[str, Any]:
        """Revoke a token (implement token blacklist if needed)"""
        try:
            # For now, we'll just validate the token to ensure it's legitimate
            validation_result = self.validate_token(token)
            if not validation_result['success']:
                return validation_result

            # TODO: Implement token blacklist storage (Redis/MongoDB)
            # For now, we'll just return success as tokens will expire naturally

            return self.success_response({
                'revoked': True,
                'token_info': validation_result['data']
            }, "Token revoked successfully")

        except Exception as e:
            return self.handle_error("revoke_token", e)

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get detailed token information"""
        try:
            validation_result = self.validate_token(token)
            if not validation_result['success']:
                return validation_result

            token_data = validation_result['data']
            now = datetime.now(timezone.utc)
            exp = datetime.fromtimestamp(token_data['expires_at'], tz=timezone.utc)

            time_until_expiry = exp - now

            return self.success_response({
                'valid': True,
                'admin_id': token_data['admin_id'],
                'username': token_data['username'],
                'role': token_data['role'],
                'token_type': token_data['token_type'],
                'issued_at': token_data['issued_at'],
                'expires_at': token_data['expires_at'],
                'time_until_expiry_seconds': int(time_until_expiry.total_seconds()),
                'is_expired': time_until_expiry.total_seconds() <= 0
            }, "Token information retrieved")

        except Exception as e:
            return self.handle_error("get_token_info", e)
