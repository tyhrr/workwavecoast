"""
Admin Model
Data model for admin users and sessions
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from werkzeug.security import check_password_hash, generate_password_hash


@dataclass
class AdminUser:
    """Represents an admin user"""
    username: str
    password_hash: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    login_count: int = 0

    @classmethod
    def create(cls, username: str, password: str, email: Optional[str] = None,
               full_name: Optional[str] = None) -> 'AdminUser':
        """Create a new admin user with hashed password"""
        return cls(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            full_name=full_name
        )

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def update_password(self, new_password: str):
        """Update user password"""
        self.password_hash = generate_password_hash(new_password)

    def record_login(self):
        """Record a successful login"""
        self.last_login = datetime.now(timezone.utc)
        self.login_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdminUser':
        """Create AdminUser from database document"""
        # Parse timestamps
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                created_at = datetime.now(timezone.utc)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now(timezone.utc)

        last_login = data.get('last_login')
        if isinstance(last_login, str):
            try:
                last_login = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            except ValueError:
                last_login = None
        elif not isinstance(last_login, datetime):
            last_login = None

        return cls(
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            email=data.get('email'),
            full_name=data.get('full_name'),
            is_active=data.get('is_active', True),
            created_at=created_at,
            last_login=last_login,
            login_count=data.get('login_count', 0)
        )


@dataclass
class AdminSession:
    """Represents an admin session"""
    session_id: str
    username: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True

    def update_activity(self, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Update session activity"""
        self.last_activity = datetime.now(timezone.utc)
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent

    def invalidate(self):
        """Invalidate the session"""
        self.is_active = False

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session is expired"""
        if not self.is_active:
            return True

        timeout_delta = datetime.now(timezone.utc) - self.last_activity
        return timeout_delta.total_seconds() > (timeout_minutes * 60)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'session_id': self.session_id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdminSession':
        """Create AdminSession from database document"""
        # Parse timestamps
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                created_at = datetime.now(timezone.utc)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now(timezone.utc)

        last_activity = data.get('last_activity')
        if isinstance(last_activity, str):
            try:
                last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            except ValueError:
                last_activity = datetime.now(timezone.utc)
        elif not isinstance(last_activity, datetime):
            last_activity = datetime.now(timezone.utc)

        return cls(
            session_id=data.get('session_id', ''),
            username=data.get('username', ''),
            created_at=created_at,
            last_activity=last_activity,
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            is_active=data.get('is_active', True)
        )


@dataclass
class AdminAction:
    """Represents an admin action for audit logging"""
    username: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'username': self.username,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'error_message': self.error_message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdminAction':
        """Create AdminAction from database document"""
        # Parse timestamp
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.now(timezone.utc)
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.now(timezone.utc)

        return cls(
            username=data.get('username', ''),
            action=data.get('action', ''),
            resource_type=data.get('resource_type', ''),
            resource_id=data.get('resource_id'),
            details=data.get('details'),
            timestamp=timestamp,
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            success=data.get('success', True),
            error_message=data.get('error_message')
        )


@dataclass
class DashboardStats:
    """Dashboard statistics for admin panel"""
    total_applications: int = 0
    pending_applications: int = 0
    approved_applications: int = 0
    rejected_applications: int = 0
    recent_applications: List[Dict[str, Any]] = field(default_factory=list)
    applications_this_week: int = 0
    applications_this_month: int = 0
    popular_positions: List[Dict[str, Any]] = field(default_factory=list)
    english_levels_distribution: Dict[str, int] = field(default_factory=dict)
    countries_distribution: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_applications': self.total_applications,
            'pending_applications': self.pending_applications,
            'approved_applications': self.approved_applications,
            'rejected_applications': self.rejected_applications,
            'recent_applications': self.recent_applications,
            'applications_this_week': self.applications_this_week,
            'applications_this_month': self.applications_this_month,
            'popular_positions': self.popular_positions,
            'english_levels_distribution': self.english_levels_distribution,
            'countries_distribution': self.countries_distribution
        }
