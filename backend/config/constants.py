"""
Application Constants
All hardcoded values and configuration constants
"""
import re

# =================== FILE UPLOAD CONSTANTS ===================

# File size limits (in bytes)
FILE_SIZE_LIMITS = {
    'cv': 5 * 1024 * 1024,  # 5MB for CV
    'foto': 2 * 1024 * 1024,  # 2MB for photos
    'carta_presentacion': 5 * 1024 * 1024,  # 5MB for cover letters
    'referencias': 5 * 1024 * 1024,  # 5MB for references
    'certificados': 5 * 1024 * 1024,  # 5MB for certificates
}

# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS = {
    'cv': ['.pdf'],  # Only PDF for CV
    'foto': ['.jpg', '.jpeg', '.png'],  # Standard image formats
    'carta_presentacion': ['.pdf', '.doc', '.docx'],
    'referencias': ['.pdf', '.doc', '.docx'],
    'certificados': ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'],
}

# Allowed MIME types for additional validation
ALLOWED_MIME_TYPES = {
    'cv': ['application/pdf'],
    'foto': ['image/jpeg', 'image/jpg', 'image/png'],
    'carta_presentacion': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ],
    'referencias': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ],
    'certificados': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/jpg',
        'image/png'
    ],
}

# =================== FORM VALIDATION CONSTANTS ===================

# Required form fields
REQUIRED_FIELDS = [
    'nombre', 'apellido', 'email', 'telefono',
    'puesto', 'ingles_nivel', 'experiencia', 'nacionalidad'
]

# Email validation pattern
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# General validation patterns for form fields
VALIDATION_PATTERNS = {
    'nombre': re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'\-]{2,50}$'),
    'apellido': re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'\-]{2,50}$'),
    'email': EMAIL_PATTERN,
    'nacionalidad': re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'\-]{2,50}$'),
    'puesto': re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'\-\/]{2,100}$'),
    'ingles_nivel': re.compile(r'^.{1,50}$'),  # Accept any character, 1-50 chars
    'experiencia': re.compile(r'^.{1,5000}$', re.DOTALL),  # Accept any character including newlines, 1-5000 chars
}

# Phone validation patterns by country
PHONE_PATTERNS = {
    'us': re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'),
    'mx': re.compile(r'^\+?52[-.\s]?([0-9]{2,3})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{4})$'),
    'es': re.compile(r'^\+?34[-.\s]?([0-9]{2,3})[-.\s]?([0-9]{3})[-.\s]?([0-9]{3})$'),
    'ar': re.compile(r'^\+?54[-.\s]?([0-9]{2,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{4})$'),
    'co': re.compile(r'^\+?57[-.\s]?([0-9]{1,3})[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'),
    'generic': re.compile(r'^\+?[0-9]{1,4}[-.\s]?[\(\)]?[0-9]{1,4}[\)\-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}$')
}

# =================== POSITION CONSTANTS ===================

# Available job positions
AVAILABLE_POSITIONS = [
    'Desarrollador Frontend',
    'Desarrollador Backend',
    'Desarrollador Full Stack',
    'Diseñador UX/UI',
    'Product Manager',
    'QA Tester',
    'DevOps Engineer',
    'Data Scientist',
    'Marketing Digital',
    'Ventas',
    'Otro'
]

# English proficiency levels
ENGLISH_LEVELS = [
    'Básico',
    'Intermedio',
    'Avanzado',
    'Nativo'
]

# =================== DATABASE CONSTANTS ===================

# Database collection names
COLLECTIONS = {
    'candidates': 'candidates',
    'admin_logs': 'admin_logs',
    'email_logs': 'email_logs'
}

# Database indexes configuration
DATABASE_INDEXES = [
    # Candidates collection indexes
    {'collection': 'candidates', 'index': [("created_at", -1)], 'options': {}},
    {'collection': 'candidates', 'index': [("email", 1)], 'options': {'unique': True, 'name': 'email_unique_idx'}},
    {'collection': 'candidates', 'index': [("puesto", 1), ("created_at", -1)], 'options': {}},
    {'collection': 'candidates', 'index': [("status", 1)], 'options': {}},
    {'collection': 'candidates', 'index': [("telefono", 1)], 'options': {}},
    {'collection': 'candidates', 'index': [("ingles_nivel", 1)], 'options': {}},
    {'collection': 'candidates', 'index': [("nacionalidad", 1)], 'options': {}},
    # Compound index for search
    {'collection': 'candidates', 'index': [
        ("nombre", "text"),
        ("apellido", "text"),
        ("email", "text"),
        ("puesto", "text"),
        ("experiencia", "text")
    ], 'options': {'name': 'search_idx'}},
]

# =================== API CONSTANTS ===================

# Rate limiting configuration
RATE_LIMITS = {
    'submit_application': "5 per minute",
    'api_general': "60 per minute",
    'admin_login': "10 per minute",
    'admin_general': "120 per minute"
}

# Pagination defaults
PAGINATION = {
    'default_per_page': 10,
    'max_per_page': 100,
    'default_page': 1
}

# =================== EMAIL CONSTANTS ===================

# Email templates configuration
EMAIL_TEMPLATES = {
    'confirmation': {
        'subject': 'Confirmación de Aplicación - WorkWave Coast',
        'template_name': 'confirmation_email'
    },
    'admin_notification': {
        'subject': 'Nueva Aplicación Recibida - WorkWave Coast',
        'template_name': 'admin_notification'
    }
}

# =================== CLOUDINARY CONSTANTS ===================

# Cloudinary upload configuration
CLOUDINARY_CONFIG = {
    'folder_prefix': 'workwave_coast',
    'use_filename': True,
    'unique_filename': True,
    'type': 'upload',
    'access_mode': 'public',
    'sign_url': False,
    'secure': True,
    'quality': 'auto',
    'fetch_format': 'auto'
}

# =================== LOGGING CONSTANTS ===================

# Log configuration
LOG_CONFIG = {
    'format': '{"asctime": "%(asctime)s", "name": "%(name)s", "levelname": "%(levelname)s", "message": "%(message)s"}',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'level': 'INFO',
    'file_max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# =================== COUNTRY MAPPINGS ===================

# Country name to ISO code mapping
COUNTRY_ISO_MAPPING = {
    'México': 'MX',
    'Estados Unidos': 'US',
    'España': 'ES',
    'Argentina': 'AR',
    'Colombia': 'CO',
    'Chile': 'CL',
    'Perú': 'PE',
    'Ecuador': 'EC',
    'Venezuela': 'VE',
    'Uruguay': 'UY',
    'Paraguay': 'PY',
    'Bolivia': 'BO',
    'Brasil': 'BR',
    'Canada': 'CA',
    'Reino Unido': 'GB',
    'Francia': 'FR',
    'Alemania': 'DE',
    'Italia': 'IT',
    'Portugal': 'PT',
    'Holanda': 'NL',
    'Bélgica': 'BE',
    'Suiza': 'CH',
    'Austria': 'AT',
    'Suecia': 'SE',
    'Noruega': 'NO',
    'Dinamarca': 'DK',
    'Finlandia': 'FI',
    'Polonia': 'PL',
    'República Checa': 'CZ',
    'Hungría': 'HU',
    'Rumania': 'RO',
    'Bulgaria': 'BG',
    'Grecia': 'GR',
    'Turquía': 'TR',
    'Rusia': 'RU',
    'China': 'CN',
    'Japón': 'JP',
    'Corea del Sur': 'KR',
    'India': 'IN',
    'Australia': 'AU',
    'Nueva Zelanda': 'NZ',
    'Sudáfrica': 'ZA',
    'Otro': 'XX'
}

# =================== ERROR MESSAGES ===================

ERROR_MESSAGES = {
    'validation': {
        'required_field': 'El campo {field} es obligatorio',
        'invalid_email': 'El formato del email no es válido',
        'invalid_phone': 'Teléfono: Formato de teléfono inválido. Use el formato: +código país número',
        'file_too_large': 'El archivo {field} es demasiado grande. Máximo: {max_size}MB',
        'file_invalid_type': 'Tipo de archivo no permitido para {field}. Permitidos: {allowed}',
        'duplicate_email': 'Ya existe una aplicación con este email'
    },
    'database': {
        'connection_error': 'Error de conexión a la base de datos',
        'operation_failed': 'Error en la operación de base de datos'
    },
    'upload': {
        'cloudinary_error': 'Error al subir el archivo',
        'file_processing_error': 'Error al procesar el archivo'
    },
    'email': {
        'send_failed': 'Error al enviar el email de confirmación',
        'config_error': 'Configuración de email incorrecta'
    },
    'auth': {
        'invalid_credentials': 'Credenciales inválidas',
        'access_denied': 'Acceso denegado'
    }
}

# =================== SUCCESS MESSAGES ===================

SUCCESS_MESSAGES = {
    'application': {
        'submitted': 'Aplicación enviada exitosamente',
        'deleted': 'Aplicación eliminada exitosamente'
    },
    'email': {
        'sent': 'Email de confirmación enviado',
        'confirmed': 'Email confirmado exitosamente'
    },
    'admin': {
        'login_success': 'Login exitoso',
        'operation_success': 'Operación completada exitosamente'
    }
}
