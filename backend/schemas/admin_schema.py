"""
Admin Schemas
Pydantic schemas for admin authentication and management
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator, Field, ConfigDict
from datetime import datetime
import re


class AdminLoginSchema(BaseModel):
    """Schema for admin login"""
    username: str = Field(..., min_length=3, max_length=50, description="Admin username")
    password: str = Field(..., min_length=8, description="Admin password")
    remember_me: bool = Field(False, description="Remember login session")

    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v or not v.strip():
            raise ValueError('Username is required')

        # Allow alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError('Username can only contain letters, numbers, underscore and hyphen')

        return v.strip().lower()

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not v:
            raise ValueError('Password is required')

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "password": "secure_password123",
                "remember_me": False
            }
        }


class AdminCreateSchema(BaseModel):
    """Schema for creating a new admin"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Admin email address", pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8, description="Admin password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: str = Field("admin", regex="^(super_admin|admin|moderator)$", description="Admin role")
    is_active: bool = Field(True, description="Whether admin account is active")

    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v or not v.strip():
            raise ValueError('Username is required')

        # Allow alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError('Username can only contain letters, numbers, underscore and hyphen')

        return v.strip().lower()

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not v:
            raise ValueError('Password is required')

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        # Check for complexity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one number')

        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name"""
        if not v or not v.strip():
            raise ValueError('Full name is required')

        # Check for valid characters
        if not re.match(r'^[a-zA-ZÀ-ÿ\u0100-\u017F\s\'-\.]+$', v.strip()):
            raise ValueError('Full name contains invalid characters')

        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "username": "admin_user",
                "email": "admin@workwave.com",
                "password": "SecurePass123",
                "full_name": "Admin User",
                "role": "admin",
                "is_active": True
            }
        }


class AdminUpdateSchema(BaseModel):
    """Schema for updating admin information"""
    email: Optional[str] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[str] = Field(None, regex="^(super_admin|admin|moderator)$")
    is_active: Optional[bool] = None

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name if provided"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Full name cannot be empty')

            # Check for valid characters
            if not re.match(r'^[a-zA-ZÀ-ÿ\u0100-\u017F\s\'-\.]+$', v.strip()):
                raise ValueError('Full name contains invalid characters')

            return v.strip()
        return v


class AdminPasswordChangeSchema(BaseModel):
    """Schema for changing admin password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if not v:
            raise ValueError('New password is required')

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        # Check for complexity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one number')

        return v

    @validator('confirm_password')
    def validate_password_match(cls, v, values):
        """Validate password confirmation"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class AdminResponseSchema(BaseModel):
    """Schema for admin response"""
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    login_count: int = 0

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AdminSessionSchema(BaseModel):
    """Schema for admin session information"""
    admin_id: str
    username: str
    role: str
    is_authenticated: bool
    session_created: datetime
    last_activity: datetime
    expires_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AdminAuditLogSchema(BaseModel):
    """Schema for admin audit log entries"""
    id: str
    admin_id: str
    admin_username: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AdminListSchema(BaseModel):
    """Schema for admin list response"""
    admins: List[AdminResponseSchema]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class AdminDashboardStatsSchema(BaseModel):
    """Schema for admin dashboard statistics"""
    total_admins: int
    active_admins: int
    total_applications: int
    pending_applications: int
    approved_applications: int
    rejected_applications: int
    applications_today: int
    applications_this_week: int
    applications_this_month: int
    recent_activity: List[AdminAuditLogSchema]
    popular_positions: List[Dict[str, Any]]
    system_health: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AdminQuerySchema(BaseModel):
    """Schema for admin query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, max_length=100, description="Search term")
    role: Optional[str] = Field(None, regex="^(super_admin|admin|moderator)$")
    is_active: Optional[bool] = None
    sort_by: str = Field("created_at", regex="^(created_at|username|email|full_name|last_login)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class AdminPermissionSchema(BaseModel):
    """Schema for admin permissions"""
    can_create_admins: bool
    can_edit_admins: bool
    can_delete_admins: bool
    can_view_applications: bool
    can_edit_applications: bool
    can_delete_applications: bool
    can_view_audit_logs: bool
    can_manage_system: bool

    @classmethod
    def from_role(cls, role: str) -> 'AdminPermissionSchema':
        """Generate permissions based on role"""
        permissions = {
            'super_admin': {
                'can_create_admins': True,
                'can_edit_admins': True,
                'can_delete_admins': True,
                'can_view_applications': True,
                'can_edit_applications': True,
                'can_delete_applications': True,
                'can_view_audit_logs': True,
                'can_manage_system': True,
            },
            'admin': {
                'can_create_admins': False,
                'can_edit_admins': False,
                'can_delete_admins': False,
                'can_view_applications': True,
                'can_edit_applications': True,
                'can_delete_applications': False,
                'can_view_audit_logs': True,
                'can_manage_system': False,
            },
            'moderator': {
                'can_create_admins': False,
                'can_edit_admins': False,
                'can_delete_admins': False,
                'can_view_applications': True,
                'can_edit_applications': False,
                'can_delete_applications': False,
                'can_view_audit_logs': False,
                'can_manage_system': False,
            }
        }

        return cls(**permissions.get(role, permissions['moderator']))


class TokenResponseSchema(BaseModel):
    """Schema for token responses"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: AdminResponseSchema
