"""
Basic Schemas - Working version
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
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


class ErrorResponseSchema(BaseResponseSchema):
    """Schema for error responses"""
    success: bool = False
    errors: Optional[List[Dict[str, str]]] = None
    error_type: Optional[str] = None


class SuccessResponseSchema(BaseResponseSchema):
    """Schema for success responses"""
    success: bool = True
    data: Optional[Dict[str, Any]] = None


class ApplicationCreateSchemaBasic(BaseModel):
    """Basic schema for creating applications"""
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    telefono: str = Field(..., min_length=5, max_length=20)
    nacionalidad: str
    puesto: str
    ingles_nivel: str
    experiencia: str = Field(..., min_length=10, max_length=2000)

    # Optional fields
    puestos_adicionales: Optional[str] = None
    salario_esperado: Optional[str] = None
    disponibilidad: Optional[str] = None
    motivacion: Optional[str] = None


class ApplicationUpdateSchemaBasic(BaseModel):
    """Basic schema for updating applications"""
    status: Optional[str] = None


class AdminLoginSchemaBasic(BaseModel):
    """Basic schema for admin login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    remember_me: bool = False


class AdminCreateSchemaBasic(BaseModel):
    """Basic schema for creating admins"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = "admin"
    is_active: bool = True


class PaginationSchema(BaseModel):
    """Schema for pagination information"""
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)
    total: int = Field(0, ge=0)
    pages: int = Field(0, ge=0)
    has_next: bool = False
    has_prev: bool = False


class ApplicationQuerySchemaBasic(BaseModel):
    """Basic schema for application queries"""
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


def create_error_response(message: str, errors: Optional[List[Dict[str, str]]] = None,
                         error_type: Optional[str] = None) -> ErrorResponseSchema:
    """Create a standardized error response"""
    return ErrorResponseSchema(
        message=message,
        errors=errors or [],
        error_type=error_type
    )


def create_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> SuccessResponseSchema:
    """Create a standardized success response"""
    return SuccessResponseSchema(
        message=message,
        data=data
    )
