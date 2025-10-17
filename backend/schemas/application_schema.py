"""
Application Schemas
Pydantic schemas for request/response validation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator, Field, ConfigDict
from datetime import datetime
import re
from config.constants import (
    AVAILABLE_POSITIONS, ENGLISH_LEVELS, COUNTRY_ISO_MAPPING,
    PHONE_PATTERNS, REQUIRED_FIELDS
)


class ApplicationCreateSchema(BaseModel):
    """Schema for creating a new application"""
    nombre: str = Field(..., min_length=1, max_length=100, description="First name")
    apellido: str = Field(..., min_length=1, max_length=100, description="Last name")
    email: str = Field(..., description="Email address", pattern=r'^[^@]+@[^@]+\.[^@]+$')
    telefono: str = Field(..., min_length=5, max_length=20, description="Phone number")
    nacionalidad: str = Field(..., description="Nationality")
    puesto: str = Field(..., description="Desired position")
    ingles_nivel: str = Field(..., description="English proficiency level")
    experiencia: str = Field(..., min_length=10, max_length=2000, description="Work experience")

    # Optional fields
    puestos_adicionales: Optional[str] = Field(None, max_length=500, description="Additional positions of interest")
    salario_esperado: Optional[str] = Field(None, max_length=100, description="Expected salary")
    disponibilidad: Optional[str] = Field(None, max_length=200, description="Availability")
    motivacion: Optional[str] = Field(None, max_length=1000, description="Motivation")

    @field_validator('nombre', 'apellido')
    @classmethod
    def validate_names(cls, v):
        """Validate name fields"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')

        # Check for valid characters (letters, spaces, some special chars)
        if not re.match(r'^[a-zA-ZÀ-ÿ\u0100-\u017F\s\'-\.]+$', v.strip()):
            raise ValueError('Name contains invalid characters')

        return v.strip()

    @field_validator('telefono')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number"""
        if not v or not v.strip():
            raise ValueError('Phone number is required')

        phone = v.strip()

        # Try different phone patterns
        for pattern_name, pattern in PHONE_PATTERNS.items():
            if pattern.match(phone):
                return phone

        raise ValueError('Teléfono: Formato de teléfono inválido. Use el formato: +código país número')

    @field_validator('nacionalidad')
    @classmethod
    def validate_nationality(cls, v):
        """Validate nationality"""
        if not v or not v.strip():
            raise ValueError('Nationality is required')

        if v.strip() not in COUNTRY_ISO_MAPPING:
            raise ValueError(f'Invalid nationality. Must be one of: {", ".join(COUNTRY_ISO_MAPPING.keys())}')

        return v.strip()

    @field_validator('puesto')
    @classmethod
    def validate_position(cls, v):
        """Validate job position"""
        if not v or not v.strip():
            raise ValueError('Position is required')

        # Allow flexible position names, not just predefined ones
        return v.strip()

    @field_validator('ingles_nivel')
    @classmethod
    def validate_english_level(cls, v):
        """Validate English level"""
        if not v or not v.strip():
            raise ValueError('English level is required')

        if v.strip() not in ENGLISH_LEVELS:
            raise ValueError(f'Invalid English level. Must be one of: {", ".join(ENGLISH_LEVELS)}')

        return v.strip()

    @field_validator('experiencia')
    @classmethod
    def validate_experience(cls, v):
        """Validate experience description"""
        if not v or not v.strip():
            raise ValueError('Experience description is required')

        if len(v.strip()) < 10:
            raise ValueError('Experience description must be at least 10 characters long')

        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "email": "juan.perez@example.com",
                "telefono": "+52-55-1234-5678",
                "nacionalidad": "México",
                "puesto": "Desarrollador Frontend",
                "ingles_nivel": "Intermedio",
                "experiencia": "Tengo 3 años de experiencia desarrollando aplicaciones web con React y Vue.js. He trabajado en equipos ágiles y tengo conocimientos en backend con Node.js."
            }
        }


class ApplicationUpdateSchema(BaseModel):
    """Schema for updating an application"""
    status: Optional[str] = Field(None, pattern="^(pending|approved|rejected|in_review)$")

    class Config:
        schema_extra = {
            "example": {
                "status": "approved"
            }
        }


class ApplicationResponseSchema(BaseModel):
    """Schema for application response"""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    id: str
    nombre: str
    apellido: str
    full_name: str
    email: str
    telefono: str
    nacionalidad: str
    puesto: str
    ingles_nivel: str
    experiencia: str
    puestos_adicionales: Optional[str] = None
    salario_esperado: Optional[str] = None
    disponibilidad: Optional[str] = None
    motivacion: Optional[str] = None
    status: str
    created_at: datetime
    files: Dict[str, Any] = {}
    has_cv: bool = False
    has_cover_letter: bool = False
    files_count: int = 0


class ApplicationListSchema(BaseModel):
    """Schema for application list response"""
    applications: List[ApplicationResponseSchema]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class ApplicationQuerySchema(BaseModel):
    """Schema for application query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, max_length=200, description="Search term")
    status: Optional[str] = Field(None, pattern="^(pending|approved|rejected|in_review)$")
    puesto: Optional[str] = Field(None, max_length=100)
    ingles_nivel: Optional[str] = Field(None, pattern="^(Básico|Intermedio|Avanzado|Nativo)$")
    nacionalidad: Optional[str] = Field(None, max_length=100)
    sort_by: str = Field("created_at", pattern="^(created_at|nombre|apellido|email|puesto|status)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class FileUploadSchema(BaseModel):
    """Schema for file upload information"""
    field_name: str = Field(..., pattern="^(cv|carta_presentacion|fotografia)$")
    filename: str
    size: int = Field(..., gt=0)

    @field_validator('size')
    @classmethod
    def validate_file_size(cls, v, info):
        """Validate file size based on field type"""
        from config.constants import FILE_SIZE_LIMITS

        data = info.data if hasattr(info, 'data') else {}
        field_name = data.get('field_name')
        if field_name and field_name in FILE_SIZE_LIMITS:
            max_size = FILE_SIZE_LIMITS[field_name]
            if v > max_size:
                max_mb = max_size / (1024 * 1024)
                raise ValueError(f'File size exceeds maximum of {max_mb}MB for {field_name}')

        return v


class ApplicationStatsSchema(BaseModel):
    """Schema for application statistics"""
    total_applications: int
    pending_applications: int
    approved_applications: int
    rejected_applications: int
    applications_this_week: int
    applications_this_month: int
    popular_positions: List[Dict[str, Any]]
    english_levels_distribution: Dict[str, int]
    countries_distribution: Dict[str, int]


class ErrorResponseSchema(BaseModel):
    """Schema for error responses"""
    success: bool = False
    message: str
    errors: Optional[List[str]] = None
    error_code: Optional[str] = None


class SuccessResponseSchema(BaseModel):
    """Schema for success responses"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
