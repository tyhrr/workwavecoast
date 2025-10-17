"""
Audit Logging Service
Comprehensive audit logging for admin actions and system events
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from services.base_service import BaseService

class AuditEventType(Enum):
    """Audit event types"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"

    # Admin management
    ADMIN_CREATED = "admin_created"
    ADMIN_UPDATED = "admin_updated"
    ADMIN_DELETED = "admin_deleted"
    ADMIN_ROLE_CHANGED = "admin_role_changed"
    ADMIN_ACTIVATED = "admin_activated"
    ADMIN_DEACTIVATED = "admin_deactivated"

    # Application management
    APPLICATION_VIEWED = "application_viewed"
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"
    APPLICATION_DELETED = "application_deleted"
    APPLICATION_EXPORTED = "application_exported"

    # File management
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    FILE_DOWNLOADED = "file_downloaded"

    # System events
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    DATABASE_BACKUP = "database_backup"
    DATABASE_RESTORE = "database_restore"

    # Security events
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PERMISSION_DENIED = "permission_denied"

class AuditLogLevel(Enum):
    """Audit log levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditService(BaseService):
    """Audit logging service for tracking admin actions and system events"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        # In production, this would connect to a dedicated audit database
        self.audit_logs = []  # Temporary in-memory storage

    def log_event(self,
                  event_type: AuditEventType,
                  admin_id: Optional[str] = None,
                  username: Optional[str] = None,
                  role: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  level: AuditLogLevel = AuditLogLevel.INFO,
                  resource_type: Optional[str] = None,
                  resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Log an audit event"""
        try:
            timestamp = datetime.now(timezone.utc)

            audit_entry = {
                'id': f"audit_{timestamp.strftime('%Y%m%d_%H%M%S')}_{len(self.audit_logs) + 1}",
                'timestamp': timestamp.isoformat(),
                'event_type': event_type.value,
                'level': level.value,
                'admin_id': admin_id,
                'username': username,
                'role': role,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'details': details or {},
                'created_at': timestamp.isoformat()
            }

            # Store in memory (in production, store in database)
            self.audit_logs.append(audit_entry)

            # Also log to application logger
            log_message = f"AUDIT [{event_type.value}] User: {username or 'Unknown'} ({role or 'Unknown'}) - {details or {}}"

            if level == AuditLogLevel.INFO:
                self.logger.info(log_message)
            elif level == AuditLogLevel.WARNING:
                self.logger.warning(log_message)
            elif level == AuditLogLevel.ERROR:
                self.logger.error(log_message)
            elif level == AuditLogLevel.CRITICAL:
                self.logger.critical(log_message)

            return self.success_response({
                'audit_id': audit_entry['id'],
                'timestamp': audit_entry['timestamp'],
                'logged': True
            }, "Audit event logged successfully")

        except Exception as e:
            return self.handle_error("log_event", e)

    def log_authentication_success(self, admin_id: str, username: str, role: str,
                                 ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Log successful authentication"""
        return self.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            admin_id=admin_id,
            username=username,
            role=role,
            ip_address=ip_address,
            user_agent=user_agent,
            details={'authentication_method': 'jwt'}
        )

    def log_authentication_failure(self, username: str, reason: str,
                                 ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Log failed authentication"""
        return self.log_event(
            event_type=AuditEventType.LOGIN_FAILURE,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            level=AuditLogLevel.WARNING,
            details={'failure_reason': reason}
        )

    def log_logout(self, admin_id: str, username: str, role: str,
                   ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Log logout event"""
        return self.log_event(
            event_type=AuditEventType.LOGOUT,
            admin_id=admin_id,
            username=username,
            role=role,
            ip_address=ip_address
        )

    def log_password_change(self, admin_id: str, username: str, role: str,
                          changed_by_admin: Optional[str] = None,
                          ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Log password change"""
        details = {}
        if changed_by_admin:
            details['changed_by_admin'] = changed_by_admin

        return self.log_event(
            event_type=AuditEventType.PASSWORD_CHANGE,
            admin_id=admin_id,
            username=username,
            role=role,
            ip_address=ip_address,
            level=AuditLogLevel.WARNING,
            details=details
        )

    def log_permission_denied(self, admin_id: str, username: str, role: str,
                            required_permission: str, attempted_action: str,
                            ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Log permission denied events"""
        return self.log_event(
            event_type=AuditEventType.PERMISSION_DENIED,
            admin_id=admin_id,
            username=username,
            role=role,
            ip_address=ip_address,
            level=AuditLogLevel.WARNING,
            details={
                'required_permission': required_permission,
                'attempted_action': attempted_action
            }
        )

    def log_application_action(self, admin_id: str, username: str, role: str,
                             action: str, application_id: str,
                             application_details: Optional[Dict[str, Any]] = None,
                             ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Log application-related actions"""
        event_mapping = {
            'view': AuditEventType.APPLICATION_VIEWED,
            'approve': AuditEventType.APPLICATION_APPROVED,
            'reject': AuditEventType.APPLICATION_REJECTED,
            'delete': AuditEventType.APPLICATION_DELETED,
            'export': AuditEventType.APPLICATION_EXPORTED
        }

        event_type = event_mapping.get(action, AuditEventType.APPLICATION_VIEWED)

        return self.log_event(
            event_type=event_type,
            admin_id=admin_id,
            username=username,
            role=role,
            ip_address=ip_address,
            resource_type='application',
            resource_id=application_id,
            details=application_details or {}
        )

    def log_file_action(self, admin_id: str, username: str, role: str,
                       action: str, file_id: str, filename: str,
                       file_details: Optional[Dict[str, Any]] = None,
                       ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Log file-related actions"""
        event_mapping = {
            'upload': AuditEventType.FILE_UPLOADED,
            'delete': AuditEventType.FILE_DELETED,
            'download': AuditEventType.FILE_DOWNLOADED
        }

        event_type = event_mapping.get(action, AuditEventType.FILE_UPLOADED)

        details = {'filename': filename}
        if file_details:
            details.update(file_details)

        return self.log_event(
            event_type=event_type,
            admin_id=admin_id,
            username=username,
            role=role,
            ip_address=ip_address,
            resource_type='file',
            resource_id=file_id,
            details=details
        )

    def get_audit_logs(self,
                      admin_id: Optional[str] = None,
                      event_type: Optional[AuditEventType] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      limit: int = 100,
                      offset: int = 0) -> Dict[str, Any]:
        """Retrieve audit logs with filtering"""
        try:
            filtered_logs = self.audit_logs.copy()

            # Apply filters
            if admin_id:
                filtered_logs = [log for log in filtered_logs if log.get('admin_id') == admin_id]

            if event_type:
                filtered_logs = [log for log in filtered_logs if log.get('event_type') == event_type.value]

            if start_date:
                start_iso = start_date.isoformat()
                filtered_logs = [log for log in filtered_logs if log.get('timestamp', '') >= start_iso]

            if end_date:
                end_iso = end_date.isoformat()
                filtered_logs = [log for log in filtered_logs if log.get('timestamp', '') <= end_iso]

            # Sort by timestamp (newest first)
            filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            # Apply pagination
            total_count = len(filtered_logs)
            paginated_logs = filtered_logs[offset:offset + limit]

            return self.success_response({
                'logs': paginated_logs,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }, "Audit logs retrieved successfully")

        except Exception as e:
            return self.handle_error("get_audit_logs", e)

    def get_audit_statistics(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get audit log statistics"""
        try:
            filtered_logs = self.audit_logs.copy()

            # Apply date filters
            if start_date:
                start_iso = start_date.isoformat()
                filtered_logs = [log for log in filtered_logs if log.get('timestamp', '') >= start_iso]

            if end_date:
                end_iso = end_date.isoformat()
                filtered_logs = [log for log in filtered_logs if log.get('timestamp', '') <= end_iso]

            # Calculate statistics
            total_events = len(filtered_logs)
            events_by_type = {}
            events_by_level = {}
            events_by_admin = {}

            for log in filtered_logs:
                # By event type
                event_type = log.get('event_type', 'unknown')
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

                # By level
                level = log.get('level', 'info')
                events_by_level[level] = events_by_level.get(level, 0) + 1

                # By admin
                username = log.get('username', 'unknown')
                events_by_admin[username] = events_by_admin.get(username, 0) + 1

            return self.success_response({
                'total_events': total_events,
                'events_by_type': events_by_type,
                'events_by_level': events_by_level,
                'events_by_admin': events_by_admin,
                'date_range': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }, "Audit statistics retrieved successfully")

        except Exception as e:
            return self.handle_error("get_audit_statistics", e)

    def export_audit_logs(self,
                         format_type: str = 'json',
                         admin_id: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Export audit logs in specified format"""
        try:
            # Get filtered logs
            logs_result = self.get_audit_logs(
                admin_id=admin_id,
                start_date=start_date,
                end_date=end_date,
                limit=10000,  # High limit for export
                offset=0
            )

            if not logs_result['success']:
                return logs_result

            logs = logs_result['data']['logs']

            if format_type.lower() == 'json':
                return self.success_response({
                    'format': 'json',
                    'data': logs,
                    'total_exported': len(logs)
                }, "Audit logs exported successfully")

            elif format_type.lower() == 'csv':
                # Convert to CSV format (simplified)
                csv_data = []
                if logs:
                    # Headers
                    headers = ['timestamp', 'event_type', 'username', 'role', 'ip_address', 'details']
                    csv_data.append(','.join(headers))

                    # Data rows
                    for log in logs:
                        row = [
                            log.get('timestamp', ''),
                            log.get('event_type', ''),
                            log.get('username', ''),
                            log.get('role', ''),
                            log.get('ip_address', ''),
                            str(log.get('details', {}))
                        ]
                        csv_data.append(','.join(f'"{field}"' for field in row))

                return self.success_response({
                    'format': 'csv',
                    'data': '\n'.join(csv_data),
                    'total_exported': len(logs)
                }, "Audit logs exported as CSV successfully")

            else:
                return self.error_response(f"Unsupported format: {format_type}", "UnsupportedFormat")

        except Exception as e:
            return self.handle_error("export_audit_logs", e)

    def cleanup_old_logs(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """Clean up old audit logs (keep only recent logs)"""
        try:
            cutoff_date = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timezone.timedelta(days=days_to_keep)
            cutoff_iso = cutoff_date.isoformat()

            initial_count = len(self.audit_logs)
            self.audit_logs = [
                log for log in self.audit_logs
                if log.get('timestamp', '') >= cutoff_iso
            ]
            final_count = len(self.audit_logs)
            removed_count = initial_count - final_count

            return self.success_response({
                'removed_logs': removed_count,
                'remaining_logs': final_count,
                'cutoff_date': cutoff_iso,
                'days_kept': days_to_keep
            }, f"Cleaned up {removed_count} old audit logs")

        except Exception as e:
            return self.handle_error("cleanup_old_logs", e)
