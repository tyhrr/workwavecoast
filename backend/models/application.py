"""
Application Model
Data model for job applications
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
import json


@dataclass
class ApplicationFile:
    """Represents an uploaded file for an application"""
    filename: str
    public_id: str
    secure_url: str
    bytes: int
    format: Optional[str] = None
    status: str = 'success'
    error: Optional[str] = None

    @classmethod
    def from_cloudinary_result(cls, result: Dict[str, Any]) -> 'ApplicationFile':
        """Create ApplicationFile from Cloudinary upload result"""
        return cls(
            filename=result.get('filename', 'unknown'),
            public_id=result.get('public_id', ''),
            secure_url=result.get('secure_url', ''),
            bytes=result.get('bytes', 0),
            format=result.get('format'),
            status=result.get('status', 'success'),
            error=result.get('error')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'filename': self.filename,
            'public_id': self.public_id,
            'secure_url': self.secure_url,
            'bytes': self.bytes,
            'format': self.format,
            'status': self.status,
            'error': self.error
        }


@dataclass
class Application:
    """Represents a job application"""

    # Required personal information
    nombre: str
    apellido: str
    email: str
    telefono: str
    nacionalidad: str

    # Job-related information
    puesto: str
    ingles_nivel: str
    experiencia: str

    # Additional fields
    puestos_adicionales: Optional[str] = None
    salario_esperado: Optional[str] = None
    disponibilidad: Optional[str] = None
    motivacion: Optional[str] = None

    # System fields
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = 'pending'

    # File attachments
    files: Dict[str, ApplicationFile] = field(default_factory=dict)

    # Database ID (set when saved to database)
    _id: Optional[ObjectId] = None

    def __post_init__(self):
        """Post-initialization processing"""
        # Normalize email to lowercase
        self.email = self.email.lower().strip()

        # Strip whitespace from string fields
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, str) and field_name != '_id':
                setattr(self, field_name, field_value.strip())

    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.nombre} {self.apellido}".strip()

    @property
    def id(self) -> Optional[str]:
        """Get string representation of database ID"""
        return str(self._id) if self._id else None

    def add_file(self, field_name: str, file_info: ApplicationFile):
        """Add a file to the application"""
        self.files[field_name] = file_info

    def get_file(self, field_name: str) -> Optional[ApplicationFile]:
        """Get a specific file from the application"""
        return self.files.get(field_name)

    def has_file(self, field_name: str) -> bool:
        """Check if application has a specific file"""
        return field_name in self.files and self.files[field_name].status == 'success'

    def get_file_urls(self) -> Dict[str, str]:
        """Get dictionary of file URLs for easy access"""
        return {
            field_name: file_info.secure_url
            for field_name, file_info in self.files.items()
            if file_info.status == 'success'
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert application to dictionary for database storage"""
        data = {
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'telefono': self.telefono,
            'nacionalidad': self.nacionalidad,
            'puesto': self.puesto,
            'ingles_nivel': self.ingles_nivel,
            'experiencia': self.experiencia,
            'created_at': self.created_at.isoformat(),
            'status': self.status
        }

        # Add optional fields if they have values
        if self.puestos_adicionales:
            data['puestos_adicionales'] = self.puestos_adicionales
        if self.salario_esperado:
            data['salario_esperado'] = self.salario_esperado
        if self.disponibilidad:
            data['disponibilidad'] = self.disponibilidad
        if self.motivacion:
            data['motivacion'] = self.motivacion

        # Add files as JSON string (compatible with current database format)
        if self.files:
            files_dict = {}
            for field_name, file_info in self.files.items():
                # Handle both ApplicationFile objects and plain dictionaries
                if isinstance(file_info, ApplicationFile):
                    files_dict[field_name] = file_info.to_dict()
                elif isinstance(file_info, dict):
                    # Already a dictionary, just copy the serializable fields
                    files_dict[field_name] = {
                        k: v for k, v in file_info.items()
                        if not callable(v) and not hasattr(v, 'read')  # Exclude file objects and callables
                    }
                else:
                    # Skip non-serializable objects
                    continue
            data['files'] = json.dumps(files_dict)
        else:
            data['files'] = "{}"

        # Add database ID if it exists (don't include in dict, MongoDB handles this)
        # if self._id:
        #     data['_id'] = self._id

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Application':
        """Create Application from database document"""
        # Extract files
        files = {}
        files_data = data.get('files', '{}')
        if files_data:
            try:
                files_dict = json.loads(files_data) if isinstance(files_data, str) else files_data
                for field_name, file_data in files_dict.items():
                    if isinstance(file_data, dict):
                        files[field_name] = ApplicationFile(**file_data)
            except (json.JSONDecodeError, TypeError):
                # Handle legacy or malformed file data
                pass

        # Parse created_at
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                created_at = datetime.now(timezone.utc)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now(timezone.utc)

        # Extract database ID
        db_id = data.get('_id')
        if isinstance(db_id, str):
            try:
                db_id = ObjectId(db_id)
            except:
                db_id = None

        return cls(
            # Required fields
            nombre=data.get('nombre', ''),
            apellido=data.get('apellido', ''),
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            nacionalidad=data.get('nacionalidad', ''),
            puesto=data.get('puesto', ''),
            ingles_nivel=data.get('ingles_nivel', ''),
            experiencia=data.get('experiencia', ''),

            # Optional fields
            puestos_adicionales=data.get('puestos_adicionales'),
            salario_esperado=data.get('salario_esperado'),
            disponibilidad=data.get('disponibilidad'),
            motivacion=data.get('motivacion'),

            # System fields
            created_at=created_at,
            status=data.get('status', 'pending'),
            files=files,
            _id=db_id
        )

    @classmethod
    def from_form_data(cls, form_data: Dict[str, Any]) -> 'Application':
        """Create Application from form submission data"""
        return cls(
            nombre=form_data.get('nombre', ''),
            apellido=form_data.get('apellido', ''),
            email=form_data.get('email', ''),
            telefono=form_data.get('telefono', ''),
            nacionalidad=form_data.get('nacionalidad', ''),
            puesto=form_data.get('puesto', ''),
            ingles_nivel=form_data.get('ingles_nivel', ''),
            experiencia=form_data.get('experiencia', ''),
            puestos_adicionales=form_data.get('puestos_adicionales'),
            salario_esperado=form_data.get('salario_esperado'),
            disponibilidad=form_data.get('disponibilidad'),
            motivacion=form_data.get('motivacion')
        )

    def update_status(self, new_status: str):
        """Update application status"""
        self.status = new_status

    def is_complete(self) -> bool:
        """Check if application has all required information"""
        required_fields = [
            self.nombre, self.apellido, self.email, self.telefono,
            self.nacionalidad, self.puesto, self.ingles_nivel, self.experiencia
        ]
        return all(field.strip() for field in required_fields)

    def get_summary(self) -> Dict[str, Any]:
        """Get application summary for display"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'telefono': self.telefono,
            'puesto': self.puesto,
            'ingles_nivel': self.ingles_nivel,
            'nacionalidad': self.nacionalidad,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'has_cv': self.has_file('cv'),
            'has_cover_letter': self.has_file('carta_presentacion'),
            'files_count': len([f for f in self.files.values() if f.status == 'success'])
        }


@dataclass
class ApplicationQuery:
    """Query parameters for filtering applications"""
    page: int = 1
    per_page: int = 10
    search: Optional[str] = None
    status: Optional[str] = None
    puesto: Optional[str] = None
    ingles_nivel: Optional[str] = None
    nacionalidad: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: str = 'created_at'
    sort_order: str = 'desc'  # 'asc' or 'desc'

    def to_mongo_query(self) -> Dict[str, Any]:
        """Convert to MongoDB query"""
        query = {}

        # Text search
        if self.search:
            query['$or'] = [
                {'nombre': {'$regex': self.search, '$options': 'i'}},
                {'apellido': {'$regex': self.search, '$options': 'i'}},
                {'email': {'$regex': self.search, '$options': 'i'}},
                {'puesto': {'$regex': self.search, '$options': 'i'}},
                {'experiencia': {'$regex': self.search, '$options': 'i'}}
            ]

        # Exact match filters
        if self.status:
            query['status'] = self.status
        if self.puesto:
            query['puesto'] = self.puesto
        if self.ingles_nivel:
            query['ingles_nivel'] = self.ingles_nivel
        if self.nacionalidad:
            query['nacionalidad'] = self.nacionalidad

        # Date range filter
        if self.date_from or self.date_to:
            date_query = {}
            if self.date_from:
                date_query['$gte'] = self.date_from.isoformat()
            if self.date_to:
                date_query['$lte'] = self.date_to.isoformat()
            query['created_at'] = date_query

        return query

    def get_sort_spec(self) -> List[tuple]:
        """Get MongoDB sort specification"""
        direction = -1 if self.sort_order == 'desc' else 1
        return [(self.sort_by, direction)]

    def get_skip(self) -> int:
        """Get skip value for pagination"""
        return (self.page - 1) * self.per_page

    def get_limit(self) -> int:
        """Get limit value for pagination"""
        return self.per_page
