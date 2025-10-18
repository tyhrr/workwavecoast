"""
Base Schemas
Common base classes and utilities for all schemas
"""
from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """Enumeration for application status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_REVIEW = "in_review"


class SortOrderEnum(str, Enum):
    """Enumeration for sort order"""
    ASC = "asc"
    DESC = "desc"


class BaseResponseSchema(BaseModel):
    """Base schema for all responses"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    success: bool
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorDetail(BaseModel):
    """Schema for detailed error information"""
    field: Optional[str] = None
    message: str
    error_code: Optional[str] = None


class ErrorResponseSchema(BaseResponseSchema):
    """Schema for error responses"""
    success: bool = False
    errors: Optional[List[ErrorDetail]] = None
    error_type: Optional[str] = None


class SuccessResponseSchema(BaseResponseSchema):
    """Schema for success responses"""
    success: bool = True
    data: Optional[Union[Dict[str, Any], List[Any]]] = None


class PaginationSchema(BaseModel):
    """Schema for pagination information"""
    page: int = Field(1, ge=1, description="Current page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    total: int = Field(0, ge=0, description="Total number of items")
    pages: int = Field(0, ge=0, description="Total number of pages")
    has_next: bool = Field(False, description="Whether there is a next page")
    has_prev: bool = Field(False, description="Whether there is a previous page")

    @field_validator('pages', mode='before')
    @classmethod
    def calculate_pages(cls, v, info):
        """Calculate total pages based on total and per_page"""
        data = info.data if hasattr(info, 'data') else {}
        total = data.get('total', 0)
        per_page = data.get('per_page', 10)
        if total == 0 or per_page == 0:
            return 0
        return (total + per_page - 1) // per_page

    @field_validator('has_next', mode='before')
    @classmethod
    def calculate_has_next(cls, v, info):
        """Calculate if there is a next page"""
        data = info.data if hasattr(info, 'data') else {}
        page = data.get('page', 1)
        pages = data.get('pages', 0)
        return page < pages

    @field_validator('has_prev', mode='before')
    @classmethod
    def calculate_has_prev(cls, v, info):
        """Calculate if there is a previous page"""
        data = info.data if hasattr(info, 'data') else {}
        page = data.get('page', 1)
        return page > 1


class PaginatedResponseSchema(BaseResponseSchema):
    """Schema for paginated responses"""
    success: bool = True
    pagination: PaginationSchema
    data: List[Any]


class BaseQuerySchema(BaseModel):
    """Base schema for query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, max_length=200, description="Search term")
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: SortOrderEnum = Field(SortOrderEnum.DESC, description="Sort order")

    @field_validator('search')
    @classmethod
    def validate_search(cls, v):
        """Validate search term"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            # Remove excessive whitespace
            v = ' '.join(v.split())
        return v


class FileInfoSchema(BaseModel):
    """Schema for file information"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    filename: str
    original_filename: str
    url: str
    public_id: str
    size: int
    format: str
    uploaded_at: datetime


class ValidationErrorSchema(BaseModel):
    """Schema for validation errors"""
    field: str
    message: str
    value: Optional[Any] = None


class HealthCheckSchema(BaseModel):
    """Schema for health check responses"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    status: str = Field(..., pattern="^(healthy|unhealthy|degraded)$")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime: int  # seconds
    database: Dict[str, Any]
    storage: Dict[str, Any]
    email: Dict[str, Any]
    memory_usage: Dict[str, Any]


class BulkOperationSchema(BaseModel):
    """Schema for bulk operations"""
    ids: Annotated[List[str], Field(min_length=1, max_length=100)]
    action: str = Field(..., description="Action to perform")
    parameters: Optional[Dict[str, Any]] = None

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v):
        """Validate list of IDs"""
        if not v:
            raise ValueError('At least one ID is required')

        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for id_val in v:
            if id_val not in seen:
                seen.add(id_val)
                unique_ids.append(id_val)

        return unique_ids


class BulkOperationResultSchema(BaseModel):
    """Schema for bulk operation results"""
    total: int
    success: int
    failed: int
    errors: List[Dict[str, Any]] = []
    results: List[Dict[str, Any]] = []


class ConfigSchema(BaseModel):
    """Schema for configuration responses"""
    available_positions: List[str]
    english_levels: List[str]
    countries: List[str]
    file_size_limits: Dict[str, int]
    allowed_file_types: Dict[str, List[str]]
    contact_info: Dict[str, str]
    system_settings: Dict[str, Any]


class MetricsSchema(BaseModel):
    """Schema for system metrics"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    applications: Dict[str, int]
    admins: Dict[str, int]
    files: Dict[str, int]
    performance: Dict[str, Any]
    errors: Dict[str, int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLogSchema(BaseModel):
    """Base schema for audit logging"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    id: str
    admin_id: Optional[str] = None
    admin_username: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Helper functions for schema validation
def create_error_response(message: str, errors: Optional[List[ErrorDetail]] = None,
                         error_type: Optional[str] = None) -> ErrorResponseSchema:
    """Create a standardized error response"""
    return ErrorResponseSchema(
        message=message,
        errors=errors or [],
        error_type=error_type
    )


def create_success_response(message: str, data: Optional[Any] = None) -> SuccessResponseSchema:
    """Create a standardized success response"""
    return SuccessResponseSchema(
        message=message,
        data=data
    )


def create_paginated_response(items: List[Any], pagination: PaginationSchema,
                            message: str = "Data retrieved successfully") -> PaginatedResponseSchema:
    """Create a paginated response"""
    return PaginatedResponseSchema(
        message=message,
        data=items,
        pagination=pagination
    )
