"""
Tests for basic schemas
"""
import pytest
from pydantic import ValidationError
from schemas.basic_schemas import (
    StatusEnum,
    SortOrderEnum,
    ApplicationCreateSchemaBasic,
    ApplicationUpdateSchemaBasic,
    AdminLoginSchemaBasic,
    AdminCreateSchemaBasic,
    PaginationSchema,
    create_error_response,
    create_success_response
)


class TestEnums:
    """Test enumeration values"""

    def test_status_enum(self):
        """Test status enum values"""
        assert StatusEnum.PENDING == "pending"
        assert StatusEnum.APPROVED == "approved"
        assert StatusEnum.REJECTED == "rejected"
        assert StatusEnum.IN_REVIEW == "in_review"

    def test_sort_order_enum(self):
        """Test sort order enum values"""
        assert SortOrderEnum.ASC == "asc"
        assert SortOrderEnum.DESC == "desc"


class TestApplicationSchemas:
    """Test application schemas"""

    def test_application_create_valid(self):
        """Test valid application creation"""
        data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan@example.com",
            "telefono": "+52-55-1234-5678",
            "nacionalidad": "México",
            "puesto": "Desarrollador Frontend",
            "ingles_nivel": "Intermedio",
            "experiencia": "Tengo 3 años de experiencia desarrollando aplicaciones web."
        }

        schema = ApplicationCreateSchemaBasic(**data)
        assert schema.nombre == "Juan"
        assert schema.apellido == "Pérez"
        assert schema.email == "juan@example.com"
        assert schema.puesto == "Desarrollador Frontend"

    def test_application_create_invalid_email(self):
        """Test invalid email validation"""
        data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "invalid-email",
            "telefono": "+52-55-1234-5678",
            "nacionalidad": "México",
            "puesto": "Desarrollador",
            "ingles_nivel": "Intermedio",
            "experiencia": "Experiencia válida con más de 10 caracteres."
        }

        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateSchemaBasic(**data)

        errors = exc_info.value.errors()
        assert any(error['type'] == 'value_error' for error in errors)

    def test_application_create_short_experience(self):
        """Test short experience validation"""
        data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan@example.com",
            "telefono": "+52-55-1234-5678",
            "nacionalidad": "México",
            "puesto": "Desarrollador",
            "ingles_nivel": "Intermedio",
            "experiencia": "Corta"  # Too short
        }

        with pytest.raises(ValidationError) as exc_info:
            ApplicationCreateSchemaBasic(**data)

        errors = exc_info.value.errors()
        assert any(error['type'] == 'string_too_short' for error in errors)

    def test_application_update_valid(self):
        """Test valid application update"""
        data = {"status": "approved"}
        schema = ApplicationUpdateSchemaBasic(**data)
        assert schema.status == "approved"


class TestAdminSchemas:
    """Test admin schemas"""

    def test_admin_login_valid(self):
        """Test valid admin login"""
        data = {
            "username": "admin",
            "password": "password123",
            "remember_me": True
        }

        schema = AdminLoginSchemaBasic(**data)
        assert schema.username == "admin"
        assert schema.password == "password123"
        assert schema.remember_me is True

    def test_admin_login_short_username(self):
        """Test short username validation"""
        data = {
            "username": "ad",  # Too short
            "password": "password123"
        }

        with pytest.raises(ValidationError) as exc_info:
            AdminLoginSchemaBasic(**data)

        errors = exc_info.value.errors()
        assert any(error['type'] == 'string_too_short' for error in errors)

    def test_admin_login_short_password(self):
        """Test short password validation"""
        data = {
            "username": "admin",
            "password": "123"  # Too short
        }

        with pytest.raises(ValidationError) as exc_info:
            AdminLoginSchemaBasic(**data)

        errors = exc_info.value.errors()
        assert any(error['type'] == 'string_too_short' for error in errors)

    def test_admin_create_valid(self):
        """Test valid admin creation"""
        data = {
            "username": "newadmin",
            "email": "admin@example.com",
            "password": "SecurePass123",
            "full_name": "New Admin",
            "role": "admin"
        }

        schema = AdminCreateSchemaBasic(**data)
        assert schema.username == "newadmin"
        assert schema.email == "admin@example.com"
        assert schema.full_name == "New Admin"
        assert schema.role == "admin"
        assert schema.is_active is True


class TestPaginationSchema:
    """Test pagination schema"""

    def test_pagination_valid(self):
        """Test valid pagination"""
        data = {
            "page": 2,
            "per_page": 20,
            "total": 100,
            "pages": 5,
            "has_next": True,
            "has_prev": True
        }

        schema = PaginationSchema(**data)
        assert schema.page == 2
        assert schema.per_page == 20
        assert schema.total == 100
        assert schema.pages == 5
        assert schema.has_next is True
        assert schema.has_prev is True

    def test_pagination_defaults(self):
        """Test pagination defaults"""
        schema = PaginationSchema()
        assert schema.page == 1
        assert schema.per_page == 10
        assert schema.total == 0
        assert schema.pages == 0
        assert schema.has_next is False
        assert schema.has_prev is False

    def test_pagination_boundaries(self):
        """Test pagination boundary conditions"""
        # Valid page numbers
        schema = PaginationSchema(page=1)
        assert schema.page == 1

        schema = PaginationSchema(page=100)
        assert schema.page == 100

        # Valid per_page values
        schema = PaginationSchema(per_page=1)
        assert schema.per_page == 1

        schema = PaginationSchema(per_page=100)
        assert schema.per_page == 100

        # Invalid page numbers
        with pytest.raises(ValidationError):
            PaginationSchema(page=0)

        # Invalid per_page values
        with pytest.raises(ValidationError):
            PaginationSchema(per_page=0)

        with pytest.raises(ValidationError):
            PaginationSchema(per_page=101)


class TestHelperFunctions:
    """Test helper functions"""

    def test_create_error_response(self):
        """Test error response helper function"""
        response = create_error_response(
            message="Validation error"
        )

        assert response.success is False
        assert response.message == "Validation error"
        assert response.errors == []

    def test_create_success_response(self):
        """Test success response helper function"""
        response = create_success_response(
            message="Created successfully",
            data={"id": "123"}
        )

        assert response.success is True
        assert response.message == "Created successfully"
        assert response.data["id"] == "123"

    def test_create_error_response_with_errors(self):
        """Test error response with errors list"""
        errors = [{"field": "email", "message": "Invalid format"}]
        response = create_error_response(
            message="Validation failed",
            errors=errors,
            error_type="validation_error"
        )

        assert response.success is False
        assert response.message == "Validation failed"
        assert len(response.errors) == 1
        assert response.errors[0]["field"] == "email"
        assert response.error_type == "validation_error"


class TestSchemaFields:
    """Test schema field validation"""

    def test_required_fields(self):
        """Test required field validation"""
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            ApplicationCreateSchemaBasic()

        with pytest.raises(ValidationError):
            AdminLoginSchemaBasic()

    def test_optional_fields(self):
        """Test optional field handling"""
        data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan@example.com",
            "telefono": "+52-55-1234-5678",
            "nacionalidad": "México",
            "puesto": "Desarrollador",
            "ingles_nivel": "Intermedio",
            "experiencia": "Experiencia válida con más de 10 caracteres.",
            "puestos_adicionales": "Backend Developer",
            "salario_esperado": "$50,000",
            "disponibilidad": "Inmediata",
            "motivacion": "Me interesa trabajar en proyectos innovadores"
        }

        schema = ApplicationCreateSchemaBasic(**data)
        assert schema.puestos_adicionales == "Backend Developer"
        assert schema.salario_esperado == "$50,000"
        assert schema.disponibilidad == "Inmediata"
        assert schema.motivacion == "Me interesa trabajar en proyectos innovadores"

        # Without optional fields
        data_minimal = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan@example.com",
            "telefono": "+52-55-1234-5678",
            "nacionalidad": "México",
            "puesto": "Desarrollador",
            "ingles_nivel": "Intermedio",
            "experiencia": "Experiencia válida con más de 10 caracteres."
        }

        schema_minimal = ApplicationCreateSchemaBasic(**data_minimal)
        assert schema_minimal.puestos_adicionales is None
        assert schema_minimal.salario_esperado is None
        assert schema_minimal.disponibilidad is None
        assert schema_minimal.motivacion is None
