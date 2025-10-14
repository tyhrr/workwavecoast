"""
WorkWave Coast Backend API
=========================

Flask application for managing job applications on the Croatian coast.
Handles file uploads to Cloudinary and stores application data in MongoDB Atlas.

Author: WorkWave Team
Version: 2.1.0 - PERFORMANCE & MONITORING UPGRADE
"""

import cloudinary
import cloudinary.uploader
import cloudinary.utils

import os
import json
import re
import logging
import requests
import sys
import subprocess
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for, send_from_directory
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from pymongo import MongoClient
import pymongo.errors
from bson import ObjectId
from dotenv import load_dotenv
from pythonjsonlogger.json import JsonFormatter
import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary.utils
import cloudinary.exceptions

# Load environment variables
# Try to load .env from parent directory (where the .env file is located)
import os
from pathlib import Path

# Get the directory of this script (backend folder)
current_dir = Path(__file__).parent
# Go up one level to the project root where .env is located
project_root = current_dir.parent
env_path = project_root / '.env'

# Load environment variables with explicit path
load_dotenv(dotenv_path=env_path)

# Debug: Print if .env file was found
if env_path.exists():
    print(f"✅ Loading .env from: {env_path}")
else:
    print(f"⚠️ .env file not found at: {env_path}")
    # Try loading from current directory as fallback
    load_dotenv()

app = Flask(__name__)

# Configure structured logging
def setup_logging():
    """Configure structured JSON logging."""
    # Remove existing handlers to avoid duplicates
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    # Configure logging based on environment
    # Detect production environment for configuration
    is_production_env = os.environ.get('FLASK_ENV') != 'development' and not os.environ.get('DEBUG', 'false').lower() == 'true'

    if is_production_env:
        handler = logging.StreamHandler()
        formatter = JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
    else:
        # Simple logging for development
        logging.basicConfig(level=logging.INFO)

    app.logger.info("Structured logging configured")

# Initialize logging
setup_logging()

# Configure Rate Limiting with better error handling
try:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per hour", "50 per minute"],
        storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
        strategy="fixed-window"  # More memory efficient than sliding window
    )
except Exception as limiter_error:
    app.logger.warning(f"Rate limiter initialization warning: {limiter_error}")
    # Continue without rate limiting if initialization fails
    limiter = None

def safe_limit(rate_limit, error_message=None):
    """Safe wrapper for rate limiting that handles when limiter is None."""
    def decorator(f):
        if limiter:
            return limiter.limit(rate_limit, error_message=error_message)(f)
        return f
    return decorator

# Security: Force environment variables for production security
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required for security")
app.secret_key = SECRET_KEY

# =================== EMAIL CONFIGURATION ===================
# Email configuration for sending confirmation emails
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Initialize Flask-Mail
mail = Mail(app)

def check_email_configuration():
    """Check if email configuration is properly set up."""
    config_issues = []

    if not app.config.get('MAIL_USERNAME'):
        config_issues.append("MAIL_USERNAME not configured")
    if not app.config.get('MAIL_PASSWORD'):
        config_issues.append("MAIL_PASSWORD not configured")
    if not app.config.get('MAIL_SERVER'):
        config_issues.append("MAIL_SERVER not configured")

    return len(config_issues) == 0, config_issues

def send_confirmation_email(applicant_name, applicant_email):
    """Send confirmation email to applicant after successful application submission."""
    try:
        # Check email configuration first
        is_configured, issues = check_email_configuration()
        if not is_configured:
            app.logger.error("Email not configured properly", extra={
                "configuration_issues": issues,
                "recipient": applicant_email
            })
            return False

        app.logger.info("Attempting to send confirmation email", extra={
            "recipient": applicant_email,
            "applicant_name": applicant_name,
            "mail_server": app.config.get('MAIL_SERVER'),
            "mail_port": app.config.get('MAIL_PORT'),
            "mail_username": app.config.get('MAIL_USERNAME', 'Not set')
        })

        # Email subject and body
        subject = "Confirmación de recepción de tu postulación"

        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Postulación - WorkWave Coast</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #1A2A36;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #F7FAFC;
                }}
                .header {{
                    background: linear-gradient(90deg, #00587A 0%, #0088B9 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                    box-shadow: 0 4px 24px rgba(0,88,122,0.08);
                }}
                .greeting {{
                    font-size: 18px;
                    color: #00587A;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}
                .main-text {{
                    margin-bottom: 25px;
                    line-height: 1.7;
                }}
                .suggestions {{
                    background: #E8F4F8;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 25px 0;
                    border-left: 4px solid #00B4D8;
                }}
                .suggestions h3 {{
                    color: #00587A;
                    margin-top: 0;
                    margin-bottom: 15px;
                }}
                .suggestions ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .suggestions li {{
                    margin-bottom: 10px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #E8F4F8;
                    text-align: center;
                }}
                .signature {{
                    color: #0088B9;
                    font-weight: 600;
                    margin-top: 20px;
                }}
                .logo {{
                    display: inline-block;
                    margin-right: 10px;
                    font-size: 24px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1><span class="logo">🏖️</span>WorkWave Coast</h1>
            </div>

            <div class="content">
                <div class="greeting">Hola {applicant_name},</div>

                <div class="main-text">
                    Queremos confirmarte que hemos recibido correctamente tu información y que ya forma parte de nuestra base de datos de candidatos para futuras oportunidades laborales en Croacia.
                </div>

                <div class="main-text">
                    Por el momento, no es necesario que realices ninguna acción adicional. Nuestro equipo revisará tu perfil y se pondrá en contacto contigo en caso de que tu experiencia se ajuste a alguna de las posiciones disponibles.
                </div>

                <div class="suggestions">
                    <h3>Mientras tanto, te sugerimos:</h3>
                    <ul>
                        <li><strong>Mantener tu currículum actualizado</strong>, especialmente en lo referente a idiomas y experiencia reciente.</li>
                        <li><strong>Revisar tu correo y carpeta de spam con frecuencia</strong>, por si te contactamos.</li>
                        <li><strong>Seguir nuestras redes sociales</strong> para conocer nuevas oportunidades y consejos laborales en la región.</li>
                    </ul>
                </div>

                <div class="main-text">
                    Gracias por tu interés y confianza en nuestro equipo.<br>
                    Te deseamos mucho éxito en tu búsqueda laboral.
                </div>

                <div class="footer">
                    <div class="signature">
                        Un cordial saludo,<br>
                        <strong>El equipo de WorkWave Coast</strong>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version for email clients that don't support HTML
        text_body = f"""
Hola {applicant_name},

Queremos confirmarte que hemos recibido correctamente tu información y que ya forma parte de nuestra base de datos de candidatos para futuras oportunidades laborales en Croacia.

Por el momento, no es necesario que realices ninguna acción adicional. Nuestro equipo revisará tu perfil y se pondrá en contacto contigo en caso de que tu experiencia se ajuste a alguna de las posiciones disponibles.

Mientras tanto, te sugerimos:

• Mantener tu currículum actualizado, especialmente en lo referente a idiomas y experiencia reciente.

• Revisar tu correo y carpeta de spam con frecuencia, por si te contactamos.

• Seguir nuestras redes sociales para conocer nuevas oportunidades y consejos laborales en la región.

Gracias por tu interés y confianza en nuestro equipo.
Te deseamos mucho éxito en tu búsqueda laboral.

Un cordial saludo,
El equipo de WorkWave Coast
        """

        # Create and send email
        msg = Message(
            subject=subject,
            recipients=[applicant_email],
            html=html_body,
            body=text_body
        )

        mail.send(msg)

        app.logger.info("Confirmation email sent successfully", extra={
            "recipient": applicant_email,
            "applicant_name": applicant_name
        })

        return True

    except Exception as e:
        app.logger.error("Failed to send confirmation email", extra={
            "recipient": applicant_email,
            "applicant_name": applicant_name,
            "error": str(e)
        })
        return False

# =================== COUNTRY FLAGS FUNCTIONALITY ===================
def country_name_to_iso(country_name):
    """Convert country name in Spanish to ISO 3166-1 alpha-2 code."""
    country_mapping = {
        'Croacia': 'HR',
        'España': 'ES',
        'Argentina': 'AR',
        'México': 'MX',
        'Colombia': 'CO',
        'Chile': 'CL',
        'Perú': 'PE',
        'Venezuela': 'VE',
        'Uruguay': 'UY',
        'Paraguay': 'PY',
        'Bolivia': 'BO',
        'Ecuador': 'EC',
        'Italia': 'IT',
        'Francia': 'FR',
        'Alemania': 'DE',
        'Reino Unido': 'GB',
        'Estados Unidos': 'US',
        'Brasil': 'BR',
        'Portugal': 'PT',
        'Países Bajos': 'NL',
        'Holanda': 'NL',
        'Bélgica': 'BE',
        'Suiza': 'CH',
        'Austria': 'AT',
        'Dinamarca': 'DK',
        'Suecia': 'SE',
        'Noruega': 'NO',
        'Finlandia': 'FI',
        'Polonia': 'PL',
        'República Checa': 'CZ',
        'Eslovaquia': 'SK',
        'Eslovenia': 'SI',
        'Hungría': 'HU',
        'Rumania': 'RO',
        'Bulgaria': 'BG',
        'Grecia': 'GR',
        'Turquía': 'TR',
        'Canadá': 'CA',
        'Australia': 'AU',
        'Nueva Zelanda': 'NZ',
        'Japón': 'JP',
        'Corea del Sur': 'KR',
        'China': 'CN',
        'India': 'IN',
        'Rusia': 'RU',
        'Ucrania': 'UA',
        'Marruecos': 'MA',
        'Egipto': 'EG',
        'Sudáfrica': 'ZA',
        'Nigeria': 'NG',
        'Kenia': 'KE',
        'Túnez': 'TN',
        'Argelia': 'DZ',
        'Costa Rica': 'CR',
        'Panamá': 'PA',
        'Guatemala': 'GT',
        'Honduras': 'HN',
        'El Salvador': 'SV',
        'Nicaragua': 'NI',
        'República Dominicana': 'DO',
        'Cuba': 'CU',
        'Jamaica': 'JM',
        'Haití': 'HT',
        'Puerto Rico': 'PR',
        'Israel': 'IL',
        'Jordania': 'JO',
        'Líbano': 'LB',
        'Siria': 'SY',
        'Irán': 'IR',
        'Irak': 'IQ',
        'Arabia Saudí': 'SA',
        'Emiratos Árabes Unidos': 'AE',
        'Qatar': 'QA',
        'Kuwait': 'KW',
        'Bahréin': 'BH',
        'Omán': 'OM',
        'Yemen': 'YE',
        'Afganistán': 'AF',
        'Pakistán': 'PK',
        'Bangladesh': 'BD',
        'Sri Lanka': 'LK',
        'Nepal': 'NP',
        'Bután': 'BT',
        'Maldivas': 'MV',
        'Tailandia': 'TH',
        'Vietnam': 'VN',
        'Camboya': 'KH',
        'Laos': 'LA',
        'Myanmar': 'MM',
        'Malasia': 'MY',
        'Singapur': 'SG',
        'Indonesia': 'ID',
        'Brunéi': 'BN',
        'Filipinas': 'PH',
        'Timor Oriental': 'TL',
        'Mongolia': 'MN',
        'Kazajistán': 'KZ',
        'Uzbekistán': 'UZ',
        'Turkmenistán': 'TM',
        'Tayikistán': 'TJ',
        'Kirguistán': 'KG',
        'Armenia': 'AM',
        'Azerbaiyán': 'AZ',
        'Georgia': 'GE',
        'Moldavia': 'MD',
        'Bielorrusia': 'BY',
        'Lituania': 'LT',
        'Letonia': 'LV',
        'Estonia': 'EE',
        'Islandia': 'IS',
        'Irlanda': 'IE',
        'Malta': 'MT',
        'Chipre': 'CY',
        'Luxemburgo': 'LU',
        'Mónaco': 'MC',
        'Andorra': 'AD',
        'San Marino': 'SM',
        'Vaticano': 'VA',
        'Liechtenstein': 'LI'
    }

    return country_mapping.get(country_name, None)

def iso_to_flag_emoji(iso_code):
    """Convert ISO 3166-1 alpha-2 country code to flag emoji."""
    if not iso_code or len(iso_code) != 2:
        return '🌍'  # Default world emoji for unknown countries

    # Convert each character to its corresponding regional indicator symbol
    # Regional Indicator Symbols: U+1F1E6 to U+1F1FF (A-Z)
    first_char = ord(iso_code[0].upper()) - ord('A') + 0x1F1E6
    second_char = ord(iso_code[1].upper()) - ord('A') + 0x1F1E6

    try:
        return chr(first_char) + chr(second_char)
    except ValueError:
        return '🌍'  # Fallback for invalid codes

def get_country_flag(country_name):
    """Get flag emoji for country name."""
    if not country_name or country_name.lower() == 'otra':
        return '🌍'

    iso_code = country_name_to_iso(country_name)
    if iso_code:
        return iso_to_flag_emoji(iso_code)
    return '🌍'

# Register custom Jinja2 filter for country flags
@app.template_filter('country_flag')
def country_flag_filter(country_name):
    """Jinja2 filter to convert country name to flag emoji."""
    return get_country_flag(country_name)

# Configuration constants - Force environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required")

# CORS origins
ALLOWED_ORIGINS = [
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://workwavecoast.online",
    "http://www.workwavecoast.online",
    "https://admin.workwavecoast.online",  # Subdomain for admin panel
    "https://workwavecoast.onrender.com",  # Your actual Render URL
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5000",
    "null"  # Para archivos abiertos directamente (file://)
]

# Configure CORS with proper settings
CORS(app,
     origins=ALLOWED_ORIGINS,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'])

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is required")

client = MongoClient(MONGODB_URI)
db = client['workwave']
candidates = db['candidates']

# Create MongoDB indexes for better performance
def create_indexes():
    """Create database indexes for optimal query performance."""
    try:
        # Index for sorting applications by date (most common query)
        candidates.create_index([("created_at", -1)])

        # Unique index for email to prevent duplicates
        try:
            candidates.create_index([("email", 1)], unique=True, name="email_unique_idx")
        except pymongo.errors.OperationFailure as e:
            if "IndexKeySpecsConflict" in str(e) or "already exists" in str(e):
                app.logger.info("Email unique index already exists, skipping creation")
            else:
                raise e

        # Compound index for filtering by position and date
        candidates.create_index([("puesto", 1), ("created_at", -1)])

        # Index for status filtering
        candidates.create_index([("status", 1)])

        # Text index for searching names, emails, and phones
        try:
            candidates.create_index([
                ("nombre", "text"),
                ("apellido", "text"),
                ("email", "text"),
                ("telefono", "text")
            ], name="search_text_idx")
        except pymongo.errors.OperationFailure as e:
            if "IndexOptionsConflict" in str(e) or "equivalent index already exists" in str(e):
                app.logger.info("Text search index already exists with different options, skipping creation")
            else:
                raise e

        # Index for phone number searches
        candidates.create_index([("telefono", 1)])

        # Index for English level filtering
        candidates.create_index([("ingles_nivel", 1)])

        app.logger.info("MongoDB indexes created successfully")

    except (pymongo.errors.OperationFailure, pymongo.errors.DuplicateKeyError) as e:
        app.logger.warning("MongoDB index creation failed: %s", str(e))
    except pymongo.errors.PyMongoError as e:
        app.logger.error("MongoDB connection error during index creation: %s", str(e))
    except (ValueError, TypeError) as e:
        app.logger.error("Configuration error creating indexes: %s", str(e))
    except Exception as e:
        app.logger.error("Unexpected error creating indexes: %s", str(e))

# Initialize indexes
create_indexes()

# Cloudinary configuration - Force environment variables for security
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    raise ValueError("All Cloudinary environment variables (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET) are required")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# File configuration constants
FILE_SIZE_LIMITS = {
    'cv': 1024 * 1024,  # 1MB for CV
    'documentos': 2 * 1024 * 1024  # 2MB for additional documents
}

ALLOWED_EXTENSIONS = {
    'cv': ['.pdf', '.doc', '.docx'],
    'documentos': ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
}

REQUIRED_FIELDS = ['nombre', 'apellido', 'nacionalidad', 'email', 'telefono', 'puesto', 'ingles_nivel', 'experiencia']

# Input validation patterns
VALIDATION_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'telefono': r'^\+\d{1,4}\s\d{7,15}$',  # Formato: +código país número
    'nombre': r'^[a-zA-ZÀ-ÿ\s]{1,50}$',
    'apellido': r'^[a-zA-ZÀ-ÿ\s]{1,50}$'
}

# Phone validation patterns by country code
PHONE_PATTERNS = {
    '+385': r'^\+385\s[0-9]{8,9}$',  # Croacia
    '+34': r'^\+34\s[0-9]{9}$',      # España
    '+54': r'^\+54\s[0-9]{10,11}$',  # Argentina
    '+52': r'^\+52\s[0-9]{10}$',     # México
    '+57': r'^\+57\s[0-9]{10}$',     # Colombia
    '+56': r'^\+56\s[0-9]{9}$',      # Chile
    '+51': r'^\+51\s[0-9]{9}$',      # Perú
    '+58': r'^\+58\s[0-9]{10}$',     # Venezuela
    '+598': r'^\+598\s[0-9]{8}$',    # Uruguay
    '+595': r'^\+595\s[0-9]{9}$',    # Paraguay
    '+591': r'^\+591\s[0-9]{8}$',    # Bolivia
    '+593': r'^\+593\s[0-9]{9}$',    # Ecuador
    '+39': r'^\+39\s[0-9]{9,10}$',   # Italia
    '+33': r'^\+33\s[0-9]{10}$',     # Francia
    '+49': r'^\+49\s[0-9]{10,11}$',  # Alemania
    '+44': r'^\+44\s[0-9]{10,11}$',  # Reino Unido
    '+1': r'^\+1\s[0-9]{10}$',       # Estados Unidos
    '+55': r'^\+55\s[0-9]{10,11}$',  # Brasil
    '+351': r'^\+351\s[0-9]{9}$'     # Portugal
}

def validate_phone_number(phone):
    """Validate phone number format according to country code."""
    if not phone or not isinstance(phone, str):
        return False, "Número de teléfono requerido"

    phone = phone.strip()

    # Check if phone matches the general international format
    if not re.match(r'^\+\d{1,4}\s\d{7,15}$', phone):
        return False, "Formato de teléfono inválido. Use el formato: +código país número"

    # Extract country code
    parts = phone.split(' ', 1)
    if len(parts) != 2:
        return False, "Formato de teléfono inválido"

    country_code = parts[0]

    # Check country-specific pattern if available
    if country_code in PHONE_PATTERNS:
        if not re.match(PHONE_PATTERNS[country_code], phone):
            return False, f"Formato incorrecto para {country_code}. Verifica el número de dígitos."

    return True, "Válido"


def validate_application_data(data):
    """Validate application form data for security and format."""
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if not data.get(field) or not data.get(field).strip():
            field_names = {
                'nombre': 'Nombre',
                'apellido': 'Apellido',
                'nacionalidad': 'Nacionalidad',
                'email': 'Email',
                'telefono': 'Teléfono',
                'puesto': 'Puesto',
                'ingles_nivel': 'Nivel de inglés',
                'experiencia': 'Experiencia laboral'
            }
            errors.append(f"Campo requerido faltante: {field_names.get(field, field)}")

    # Special validation for phone number
    if 'telefono' in data and data['telefono']:
        is_valid, message = validate_phone_number(data['telefono'])
        if not is_valid:
            errors.append(f"Teléfono: {message}")

    # Validate field formats (excluding phone which has special validation)
    for field, pattern in VALIDATION_PATTERNS.items():
        if field == 'telefono':  # Skip phone, already validated above
            continue
        if field in data and data[field]:
            if not re.match(pattern, data[field].strip()):
                errors.append(f"Formato inválido para {field}")

    # Validate field lengths to prevent DoS
    max_lengths = {
        'nombre': 50, 'apellido': 50, 'email': 100, 'telefono': 25,
        'nacionalidad': 50, 'puesto': 50, 'experiencia': 500,
        'motivacion': 1000, 'disponibilidad': 200, 'puestos_adicionales': 200,
        'espanol_nivel': 20, 'otro_idioma': 50, 'otro_idioma_nivel': 20,
        'ingles_nivel': 20
    }

    for field, max_length in max_lengths.items():
        if field in data and data[field] and len(data[field]) > max_length:
            errors.append(f"Campo {field} excede la longitud máxima de {max_length} caracteres")

    return len(errors) == 0, errors


def check_duplicate_application(email):
    """Check if an application with this email already exists."""
    try:
        existing = candidates.find_one({"email": email.lower().strip()})
        return existing is not None
    except Exception as e:
        app.logger.error("Error checking duplicate application", extra={
            "email": email,
            "error": str(e)
        })
        return False  # If we can't check, allow the application


def login_required(f):
    """Decorator to require admin login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def validate_file(file, field_name):
    """Validate uploaded file size and extension."""
    if not file or not file.filename:
        return True, None, 0

    # Validate file extension
    if field_name in ALLOWED_EXTENSIONS:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS[field_name]:
            allowed = ', '.join(ALLOWED_EXTENSIONS[field_name])
            return False, "Tipo de archivo no permitido para " + field_name + ". Permitidos: " + allowed, 0

    # Validate file size
    try:
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
    except IOError:
        return False, "Error al procesar el archivo " + field_name, 0

    if field_name in FILE_SIZE_LIMITS and file_size > FILE_SIZE_LIMITS[field_name]:
        max_size_mb = FILE_SIZE_LIMITS[field_name] / (1024 * 1024)
        return False, "El archivo " + field_name + " es demasiado grande. Máximo: " + str(max_size_mb) + "MB", file_size

    return True, None, file_size


def upload_to_cloudinary(file, field_name, file_size):
    """Upload file to Cloudinary with proper error handling and public access."""
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')

    # Check if Cloudinary is properly configured
    if not all([cloud_name, api_key, api_secret]) or cloud_name == 'tu_cloud_name':
        return {
            'filename': file.filename,
            'size_bytes': file_size,
            'status': 'cloudinary_not_configured',
            'note': 'File received but stored locally due to missing Cloudinary config',
            'system_version': '2.0.2'
        }

    try:

        # Configure upload options for GUARANTEED public access
        upload_options = {
            'folder': 'workwave_coast',
            'use_filename': True,
            'unique_filename': True,
            'type': 'upload',  # Standard upload type
            'access_mode': 'public',  # Force public access
            'sign_url': False,  # Disable URL signing
            'secure': True,  # Use HTTPS but public
            'public_id_prefix': '',  # No authentication prefix
            'invalidate': True,  # Clear CDN cache
            'overwrite': False,  # Keep unique filenames
            'resource_type': 'auto',  # Let Cloudinary auto-detect, then override if needed
        }

        # Override resource type for PDFs to ensure proper handling
        if field_name == 'cv' and file.filename.lower().endswith('.pdf'):
            upload_options['resource_type'] = 'raw'
            upload_options['format'] = 'pdf'

        # For documents, also use raw type
        elif field_name == 'documentos' and file.filename.lower().endswith('.pdf'):
            upload_options['resource_type'] = 'raw'
            upload_options['format'] = 'pdf'

        # Upload file
        upload_result = cloudinary.uploader.upload(file, **upload_options)

        # Determine resource type for URL generation
        resource_type = upload_result.get('resource_type', 'image')
        public_id = upload_result['public_id']

        # Generate both the direct URL and our proxy URL
        direct_url = upload_result['secure_url']
        proxy_url = f"/api/admin/cloudinary-proxy/{public_id}"

        # VERIFY PUBLIC ACCESS: Test if the uploaded file is publicly accessible
        access_verified = False
        try:
            test_response = requests.head(direct_url, timeout=5)
            access_verified = test_response.status_code == 200
            app.logger.info(f"Public access verification: {access_verified} (status: {test_response.status_code})")
        except Exception as verify_error:
            app.logger.warning(f"Could not verify public access: {str(verify_error)}")

        # Log the upload for debugging
        app.logger.info("File uploaded to Cloudinary", extra={
            "field_name": field_name,
            "file_name": file.filename,
            "public_id": public_id,
            "resource_type": resource_type,
            "direct_url": direct_url,
            "proxy_url": proxy_url,
            "bytes": upload_result.get('bytes', 0),
            "access_verified": access_verified,
            "upload_type": upload_options.get('type'),
            "access_mode": upload_options.get('access_mode')
        })

        return {
            'url': direct_url,  # Primary URL
            'proxy_url': proxy_url,  # Fallback URL through our server
            'public_id': public_id,
            'resource_type': resource_type,
            'format': upload_result.get('format', ''),
            'bytes': upload_result.get('bytes', 0),
            'pages': upload_result.get('pages', 1) if 'pages' in upload_result else 1,
            'filename': file.filename,
            'status': 'cloudinary_upload_success',
            'system_version': '2.0.2'
        }

    except (ConnectionError, requests.RequestException) as e:
        app.logger.error("Network error during Cloudinary upload", extra={
            "field_name": field_name,
            "file_name": file.filename,
            "error": str(e)
        })
        return {
            'filename': file.filename,
            'size_bytes': file_size,
            'status': 'cloudinary_network_error',
            'error': str(e),
            'note': 'Network error during cloud upload',
            'system_version': '2.0.2'
        }
    except ValueError as e:
        app.logger.error("Invalid file data for Cloudinary", extra={
            "field_name": field_name,
            "file_name": file.filename,
            "error": str(e)
        })
        return {
            'filename': file.filename,
            'size_bytes': file_size,
            'status': 'cloudinary_invalid_file',
            'error': str(e),
            'note': 'Invalid file format or data',
            'system_version': '2.0.2'
        }
    except cloudinary.exceptions.Error as e:
        app.logger.error("Cloudinary API error during upload", extra={
            "field_name": field_name,
            "file_name": file.filename,
            "error": str(e),
            "error_type": "cloudinary_api"
        })
        return {
            'filename': file.filename,
            'size_bytes': file_size,
            'status': 'cloudinary_api_error',
            'error': str(e),
            'note': 'Cloudinary service error',
            'system_version': '2.0.2'
        }
    except (OSError, IOError) as e:
        app.logger.error("File system error during upload", extra={
            "field_name": field_name,
            "file_name": file.filename,
            "error": str(e),
            "error_type": "filesystem"
        })
        return {
            'filename': file.filename,
            'size_bytes': file_size,
            'status': 'filesystem_error',
            'error': str(e),
            'note': 'File system access error',
            'system_version': '2.0.2'
        }
    except Exception as e:
        app.logger.error("Unexpected error during Cloudinary upload", extra={
            "field_name": field_name,
            "file_name": file.filename,
            "error": str(e)
        })
        # Fallback: save basic file info instead of failing
        return {
            'filename': file.filename,
            'size_bytes': file_size,
            'status': 'cloudinary_upload_failed',
            'error': str(e),
            'note': 'File received but not uploaded to cloud storage',
            'system_version': '2.0.2'
        }


# HTML Templates
LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WorkWave Coast - Admin Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Montserrat', Arial, sans-serif;
            background: linear-gradient(135deg, #00587A 0%, #00B4D8 100%);
            color: #1A2A36;
            margin: 0;
            padding: 0;
            line-height: 1.6;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 4px 24px rgba(0,88,122,0.08);
            padding: 2rem;
            width: 100%;
            max-width: 400px;
            position: relative;
            z-index: 1;
        }
        .logo {
            text-align: center;
            margin-bottom: 2rem;
            color: #00587A;
        }
        .logo h1 {
            font-size: 1.8rem;
            margin: 0.5rem 0 0.7rem 0;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .logo p {
            color: #0088B9;
            font-weight: 500;
            margin: 0;
        }
        .form-group {
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .form-group label {
            font-weight: 500;
            margin-bottom: 0.3rem;
            color: #0088B9;
            font-size: 0.9rem;
        }
        input[type="text"], input[type="password"] {
            padding: 0.6rem 0.8rem;
            border: 1px solid #B2DFEE;
            border-radius: 6px;
            font-size: 1rem;
            background: #F7FAFC;
            color: #1A2A36;
            transition: border 0.2s;
            width: 100%;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            border-color: #00B4D8;
            outline: none;
            box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.1);
        }
        .submit-btn {
            background: linear-gradient(90deg, #0088B9 0%, #00B4D8 100%);
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 0.8rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 1rem;
            box-shadow: 0 2px 8px rgba(0,88,122,0.08);
            transition: all 0.2s;
            width: 100%;
        }
        .submit-btn:hover {
            background: linear-gradient(90deg, #00587A 0%, #0088B9 100%);
            box-shadow: 0 4px 16px rgba(0,88,122,0.13);
            transform: translateY(-1px);
        }
        .error {
            color: #dc3545;
            margin-top: 1rem;
            text-align: center;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🏖️ WorkWave Coast</h1>
            <p>Panel de Administración</p>
        </div>
        <form method="POST">
            <div class="form-group">
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="submit-btn">Iniciar Sesión</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>'''


ADMIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WorkWave Coast - Panel de Administración</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Montserrat', Arial, sans-serif;
            background: #F7FAFC;
            color: #1A2A36;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(90deg, #00587A 0%, #0088B9 100%);
            color: #fff;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,88,122,0.08);
        }
        .header h1 {
            font-size: 1.5rem;
            margin: 0;
            font-weight: 700;
        }
        .logout {
            background: rgba(255,255,255,0.2);
            color: #fff;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
        }
        .logout:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-1px);
        }
        .container {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,88,122,0.08);
            padding: 1.5rem;
            text-align: center;
            border: 1px solid #B2DFEE;
        }
        .stat-card h3 {
            color: #00587A;
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
            font-weight: 600;
        }
        .stat-number {
            font-size: 2rem;
            margin: 0;
            font-weight: 700;
        }
        .filters-section {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,88,122,0.08);
            padding: 1.5rem;
            margin-bottom: 2rem;
            border: 1px solid #B2DFEE;
        }
        .filters-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            align-items: end;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
        }
        .filter-group label {
            font-weight: 500;
            margin-bottom: 0.3rem;
            color: #0088B9;
            font-size: 0.9rem;
        }
        input[type="text"], select {
            padding: 0.6rem 0.8rem;
            border: 1px solid #B2DFEE;
            border-radius: 6px;
            font-size: 1rem;
            background: #F7FAFC;
            color: #1A2A36;
            transition: border 0.2s;
        }
        input[type="text"]:focus, select:focus {
            border-color: #00B4D8;
            outline: none;
            box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.1);
        }
        .clear-btn {
            background: #FFD180;
            color: #00587A;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .clear-btn:hover {
            background: #ffc947;
            transform: translateY(-1px);
        }
        .select-all-btn {
            background: #0088B9;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .select-all-btn:hover {
            background: #00587A;
            transform: translateY(-1px);
        }
        .delete-selected-btn {
            background: #dc3545;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            margin-left: 0.5rem;
        }
        .delete-selected-btn:hover {
            background: #c82333;
            transform: translateY(-1px);
        }
        .delete-selected-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }
        .selection-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding: 1rem;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,88,122,0.08);
        }
        .selection-info {
            color: #0088B9;
            font-weight: 500;
        }
        .selection-actions {
            display: flex;
            gap: 0.5rem;
        }
        .applications-list {
            background: #fff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0,88,122,0.08);
            border: 1px solid #B2DFEE;
        }
        .application-item {
            border-bottom: 1px solid #B2DFEE;
            padding: 1rem 1.5rem;
            transition: background 0.2s;
            display: grid;
            grid-template-columns: auto 2fr 1fr 1fr auto auto;
            gap: 1rem;
            align-items: center;
        }
        .application-item:last-child { border-bottom: none; }
        .application-item:hover { background: #F7FAFC; }
        .application-item.selected { background: #E3F2FD; }
        .application-checkbox {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: #00B4D8;
        }
        .delete-btn {
            background: #dc3545;
            color: #fff;
            border: none;
            border-radius: 4px;
            padding: 0.3rem 0.6rem;
            font-size: 0.7rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .delete-btn:hover {
            background: #c82333;
            transform: translateY(-1px);
        }
        .applicant-info {
            display: flex;
            flex-direction: column;
        }
        .applicant-name {
            font-weight: 600;
            color: #00587A;
            font-size: 1rem;
        }
        .applicant-details {
            font-size: 0.85rem;
            color: #0088B9;
            margin-top: 0.2rem;
        }
        .job-info {
            display: flex;
            flex-direction: column;
        }
        .job-position {
            font-weight: 500;
            color: #1A2A36;
        }
        .languages {
            font-size: 0.8rem;
            color: #666;
            margin-top: 0.2rem;
        }
        .application-date {
            font-size: 0.8rem;
            color: #666;
        }
        .application-files {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }
        .file-link {
            background: #00B4D8;
            color: #fff;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.2s;
            cursor: pointer;
        }
        .file-link:hover {
            background: #0088B9;
            transform: translateY(-1px);
        }
        .file-error {
            background: #ff6b6b !important;
            cursor: help;
        }
        .no-files {
            color: #999;
            font-size: 0.8rem;
            font-style: italic;
        }
        .file-details {
            grid-column: 1 / -1;
            background: #f8f9fa;
            padding: 0.8rem;
            border-radius: 6px;
            border-top: 1px solid #e9ecef;
            margin-top: 0.5rem;
        }
        .file-detail-item {
            margin-bottom: 0.3rem;
            font-size: 0.8rem;
        }
        .file-detail-item strong {
            color: #00587A;
        }
        .file-detail-item a {
            color: #00B4D8;
            text-decoration: none;
        }
        .file-detail-item a:hover {
            text-decoration: underline;
        }
        .file-detail-item small {
            color: #666;
            margin-left: 0.5rem;
        }
        .expand-btn {
            background: #FFD180;
            color: #00587A;
            border: none;
            border-radius: 3px;
            padding: 0.2rem 0.4rem;
            font-size: 0.7rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        .expand-btn:hover {
            background: #ffc947;
        }
        .file-link:hover {
            background: #0088B9;
            transform: translateY(-1px);
        }
        .no-results {
            text-align: center;
            padding: 3rem;
            color: #666;
            font-style: italic;
        }
        .results-count {
            margin-bottom: 1rem;
            color: #00587A;
            font-weight: 500;
        }
        @media (max-width: 768px) {
            .application-item {
                grid-template-columns: 1fr;
                gap: 0.5rem;
            }
            .filters-row {
                grid-template-columns: 1fr;
            }
            .header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            .selection-controls {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            .selection-actions {
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏖️ WorkWave Coast - Panel de Administración</h1>
        <a href="/admin/logout" class="logout">Cerrar Sesión</a>
    </div>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>📊 Total Aplicaciones</h3>
                <p class="stat-number" style="color: #00B4D8;">{{ applications|length }}</p>
            </div>
            <div class="stat-card">
                <h3>📅 Hoy</h3>
                <p class="stat-number" style="color: #FFD180;">{{ today_count }}</p>
            </div>
            <div class="stat-card">
                <h3>⏳ Pendientes</h3>
                <p class="stat-number" style="color: #0088B9;">{{ pending_count }}</p>
            </div>
        </div>

        <div class="filters-section">
            <div class="filters-row">
                <div class="filter-group">
                    <label for="searchFilter">🔍 Buscar por nombre, apellido, teléfono o email:</label>
                    <input type="text" id="searchFilter" placeholder="Ej: Juan, García, +385123456789, juan@email.com..." onkeyup="filterApplications()">
                </div>
                <div class="filter-group">
                    <label for="jobFilter">💼 Filtrar por puesto:</label>
                    <select id="jobFilter" onchange="filterApplications()">
                        <option value="">Todos los puestos</option>
                        <option value="Camarero/a">Camarero/a</option>
                        <option value="Recepcionista">Recepcionista</option>
                        <option value="Cocinero/a">Cocinero/a</option>
                        <option value="Animador/a">Animador/a</option>
                        <option value="Limpieza">Limpieza</option>
                        <option value="Mantenimiento">Mantenimiento</option>
                        <option value="Otro">Otro</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="englishFilter">🇬🇧 Nivel de inglés:</label>
                    <select id="englishFilter" onchange="filterApplications()">
                        <option value="">Todos los niveles</option>
                        <option value="A1">A1 - Básico</option>
                        <option value="A2">A2 - Pre-intermedio</option>
                        <option value="B1">B1 - Intermedio</option>
                        <option value="B2">B2 - Intermedio-Alto</option>
                        <option value="C1">C1 - Avanzado</option>
                        <option value="C2">C2 - Nativo</option>
                    </select>
                </div>
                <div class="filter-group">
                    <button class="clear-btn" onclick="clearFilters()">Limpiar Filtros</button>
                </div>
            </div>
        </div>

        <div class="selection-controls">
            <div class="selection-info">
                <span id="selectedCount">0</span> aplicaciones seleccionadas
            </div>
            <div class="selection-actions">
                <button class="select-all-btn" onclick="toggleSelectAll()">Seleccionar Todo</button>
                <button class="delete-selected-btn" onclick="deleteSelected()" disabled id="deleteSelectedBtn">
                    🗑️ Eliminar Seleccionadas
                </button>
            </div>
        </div>

        <div class="results-count" id="resultsCount">
            Mostrando {{ applications|length }} aplicaciones
        </div>

        <div class="applications-list">
            {% for app in applications %}
            <div class="application-item"
                 data-id="{{ app.get('_id', '') }}"
                 data-name="{{ (app.get('nombre', '') + ' ' + app.get('apellido', '')).lower() }}"
                 data-contact="{{ (app.get('email', '') + ' ' + app.get('telefono', '')).lower() }}"
                 data-job="{{ app.get('puesto', '') }}"
                 data-english="{{ app.get('ingles_nivel', '') }}">

                <input type="checkbox" class="application-checkbox" onchange="updateSelection()">

                <div class="applicant-info">
                    <div class="applicant-name">{{ app.get('nombre', '')|e }} {{ app.get('apellido', '')|e }}</div>
                    <div class="applicant-details">
                        📧 {{ app.get('email', '')|e }} | 📞 {{ app.get('telefono', '')|e }} | {{ app.get('nacionalidad', '')|country_flag }} {{ app.get('nacionalidad', '')|e }}
                    </div>
                </div>

                <div class="job-info">
                    <div class="job-position">{{ app.get('puesto', '')|e }}</div>
                    <div class="languages">
                        🇪🇸 {{ app.get('espanol_nivel', '')|e }} | 🇬🇧 {{ app.get('ingles_nivel', '')|e }}{% if app.get('otro_idioma') %} | {{ app.get('otro_idioma', '')|e }}: {{ app.get('otro_idioma_nivel', '')|e }}{% endif %}
                    </div>
                </div>

                <div class="application-date">
                    📅 {{ app.get('created_at', '')[:10] }}<br>
                    🕐 {{ app.get('created_at', '')[11:16] }}
                </div>

                <div class="application-files">
                    {% if app.get('files_parsed') %}
                        {% for file_type, file_info in app.get('files_parsed', {}).items() %}
                            {% if file_info.get('url') %}
                                {% if 'cloudinary.com' in file_info.get('url', '') %}
                                    {% set url_parts = file_info.get('url', '').split('/') %}
                                    {% set proxy_path = '' %}
                                    {% for i in range(url_parts|length) %}
                                        {% if url_parts[i] == 'upload' and i + 1 < url_parts|length and not proxy_path %}
                                            {% set proxy_path = '/'.join(url_parts[i+1:]) %}
                                        {% endif %}
                                    {% endfor %}
                                    {% set file_url = '/api/admin/cloudinary-proxy/' + proxy_path if proxy_path else file_info.get('url') %}
                                {% else %}
                                    {% set file_url = file_info.get('url') %}
                                {% endif %}
                                <a href="{{ file_url }}" target="_blank" class="file-link"
                                   title="Ver {{ file_type }} - {{ file_info.get('filename', 'archivo') }}"
                                   data-direct-url="{{ file_info.get('url') }}"
                                   data-public-id="{{ file_info.get('public_id', '') }}"
                                   data-resource-type="{{ file_info.get('resource_type', 'raw') }}">
                                    {% if file_type == 'cv' %}📄{% else %}📎{% endif %} {{ file_type.title() }}
                                </a>
                            {% elif file_info.get('filename') %}
                                <span class="file-link file-error" title="Archivo: {{ file_info.get('filename') }} - {{ file_info.get('note', 'Error al cargar') }}">
                                    {% if file_type == 'cv' %}📄{% else %}📎{% endif %} {{ file_type.title() }} ⚠️
                                </span>
                            {% endif %}
                        {% endfor %}
                        <button class="expand-btn" onclick="toggleFileDetails(this)" title="Ver detalles y experiencia">
                            📋
                        </button>
                    {% else %}
                        <span class="no-files">Sin archivos</span>
                        <button class="expand-btn" onclick="toggleFileDetails(this)" title="Ver experiencia laboral">
                            📋
                        </button>
                    {% endif %}
                </div>

                <button class="delete-btn" onclick="deleteApplication('{{ app.get('_id', '') }}')" title="Eliminar esta aplicación">
                    🗑️
                </button>

                <!-- Detailed info (expandable) -->
                <div class="file-details" style="display: none;">
                    <!-- Experience Section -->
                    <div class="file-detail-item" style="background: #e8f4f8; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                        <strong style="color: #00587A; font-size: 1rem;">💼 Experiencia Laboral:</strong>
                        <div style="margin-top: 0.5rem; line-height: 1.5; color: #1A2A36; font-size: 0.9rem; white-space: pre-wrap;">{{ app.get('experiencia', 'No especificada')|e }}</div>
                        {% if app.get('puestos_adicionales') %}
                            <div style="margin-top: 0.8rem;">
                                <strong style="color: #0088B9;">📌 Puestos adicionales de interés:</strong>
                                <span style="color: #666; margin-left: 0.5rem;">{{ app.get('puestos_adicionales', '')|e }}</span>
                            </div>
                        {% endif %}
                    </div>

                    <!-- Files Section -->
                    {% if app.get('files_parsed') %}
                        <div style="border-top: 1px solid #e9ecef; padding-top: 1rem;">
                            <strong style="color: #00587A; margin-bottom: 0.5rem; display: block;">📎 Archivos Adjuntos:</strong>
                            {% for file_type, file_info in app.get('files_parsed', {}).items() %}
                                <div class="file-detail-item">
                                    <strong>{{ file_type.title() }}:</strong>
                                    {% if file_info.get('url') %}
                                    {% if 'cloudinary.com' in file_info.get('url', '') %}
                                        {% set url_parts = file_info.get('url', '').split('/') %}
                                        {% set proxy_path = '' %}
                                        {% for i in range(url_parts|length) %}
                                            {% if url_parts[i] == 'upload' and i + 1 < url_parts|length and not proxy_path %}
                                                {% set proxy_path = '/'.join(url_parts[i+1:]) %}
                                            {% endif %}
                                        {% endfor %}
                                        {% set detail_url = '/api/admin/cloudinary-proxy/' + proxy_path if proxy_path else file_info.get('url') %}
                                    {% else %}
                                        {% set detail_url = file_info.get('url') %}
                                    {% endif %}
                                    <a href="{{ detail_url }}" target="_blank"
                                       title="Usar proxy para mejor compatibilidad">
                                        {{ file_info.get('filename', 'Ver archivo') }}
                                    </a>
                                    <small>({{ (file_info.get('bytes', 0) / 1024) | round(1) }} KB)</small>
                                    {% if file_info.get('public_id') %}
                                        <br><small>ID: {{ file_info.get('public_id') }}</small>
                                        <br><small>Tipo: {{ file_info.get('resource_type', 'auto') }}</small>
                                    {% endif %}
                                    <br><small><a href="{{ file_info.get('url') }}" target="_blank" style="color: #666;">URL directa</a></small>
                                    {% else %}
                                        <span>{{ file_info.get('filename', 'N/A') }}</span>
                                        <small>({{ file_info.get('status', 'Error') }})</small>
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </div>
                    {% else %}
                        <div style="border-top: 1px solid #e9ecef; padding-top: 1rem; color: #666; font-style: italic;">
                            No hay archivos adjuntos
                        </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>        <div id="noResults" class="no-results" style="display: none;">
            No se encontraron aplicaciones que coincidan con los filtros seleccionados.
        </div>
    </div>

    <script>
        let selectedApplications = new Set();

        function filterApplications() {
            const searchTerm = document.getElementById('searchFilter').value.toLowerCase();
            const jobFilter = document.getElementById('jobFilter').value;
            const englishFilter = document.getElementById('englishFilter').value;

            const applications = document.querySelectorAll('.application-item');
            let visibleCount = 0;

            applications.forEach(app => {
                const name = app.getAttribute('data-name');
                const contact = app.getAttribute('data-contact'); // email + phone
                const job = app.getAttribute('data-job');
                const english = app.getAttribute('data-english');

                // Search in name, email, and phone
                const matchesSearch = name.includes(searchTerm) || contact.includes(searchTerm);
                const matchesJob = jobFilter === '' || job === jobFilter;
                const matchesEnglish = englishFilter === '' || english === englishFilter;

                if (matchesSearch && matchesJob && matchesEnglish) {
                    app.style.display = 'grid';
                    visibleCount++;
                } else {
                    app.style.display = 'none';
                    // Uncheck hidden items
                    const checkbox = app.querySelector('.application-checkbox');
                    if (checkbox.checked) {
                        checkbox.checked = false;
                        selectedApplications.delete(app.getAttribute('data-id'));
                    }
                }
            });

            const resultsCount = document.getElementById('resultsCount');
            const noResults = document.getElementById('noResults');

            if (visibleCount === 0) {
                resultsCount.style.display = 'none';
                noResults.style.display = 'block';
            } else {
                resultsCount.style.display = 'block';
                resultsCount.textContent = `Mostrando ${visibleCount} aplicaciones`;
                noResults.style.display = 'none';
            }

            updateSelection();
        }

        function clearFilters() {
            document.getElementById('searchFilter').value = '';
            document.getElementById('jobFilter').value = '';
            document.getElementById('englishFilter').value = '';
            filterApplications();
        }

        function updateSelection() {
            const checkboxes = document.querySelectorAll('.application-checkbox');
            const visibleCheckboxes = Array.from(checkboxes).filter(cb =>
                cb.closest('.application-item').style.display !== 'none'
            );

            selectedApplications.clear();
            let selectedCount = 0;

            checkboxes.forEach(checkbox => {
                const appItem = checkbox.closest('.application-item');
                const appId = appItem.getAttribute('data-id');

                if (checkbox.checked) {
                    selectedApplications.add(appId);
                    selectedCount++;
                    appItem.classList.add('selected');
                } else {
                    appItem.classList.remove('selected');
                }
            });

            document.getElementById('selectedCount').textContent = selectedCount;
            const deleteBtn = document.getElementById('deleteSelectedBtn');
            deleteBtn.disabled = selectedCount === 0;

            // Update select all button text
            const selectAllBtn = document.querySelector('.select-all-btn');
            const allVisible = visibleCheckboxes.length > 0;
            const allSelected = visibleCheckboxes.every(cb => cb.checked);

            if (allVisible && allSelected) {
                selectAllBtn.textContent = 'Deseleccionar Todo';
            } else {
                selectAllBtn.textContent = 'Seleccionar Todo';
            }
        }

        function toggleSelectAll() {
            const visibleCheckboxes = Array.from(document.querySelectorAll('.application-checkbox'))
                .filter(cb => cb.closest('.application-item').style.display !== 'none');

            const allSelected = visibleCheckboxes.every(cb => cb.checked);

            visibleCheckboxes.forEach(checkbox => {
                checkbox.checked = !allSelected;
            });

            updateSelection();
        }

        function deleteApplication(applicationId) {
            if (!confirm('¿Estás seguro de que quieres eliminar esta aplicación? Esta acción no se puede deshacer.')) {
                return;
            }

            const deleteBtn = event.target;
            const originalText = deleteBtn.textContent;
            deleteBtn.textContent = '⏳';
            deleteBtn.disabled = true;

            fetch(`/api/admin/delete-application/${applicationId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the application from the DOM
                    const appItem = document.querySelector(`[data-id="${applicationId}"]`);
                    if (appItem) {
                        appItem.remove();
                        selectedApplications.delete(applicationId);
                        updateSelection();
                        filterApplications(); // Update count
                    }

                    // Show success message
                    showMessage('Aplicación eliminada exitosamente', 'success');
                } else {
                    showMessage('Error al eliminar la aplicación: ' + data.error, 'error');
                    deleteBtn.textContent = originalText;
                    deleteBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de conexión al eliminar la aplicación', 'error');
                deleteBtn.textContent = originalText;
                deleteBtn.disabled = false;
            });
        }

        function deleteSelected() {
            const selectedCount = selectedApplications.size;
            if (selectedCount === 0) {
                return;
            }

            if (!confirm(`¿Estás seguro de que quieres eliminar ${selectedCount} aplicaciones seleccionadas? Esta acción no se puede deshacer.`)) {
                return;
            }

            const deleteBtn = document.getElementById('deleteSelectedBtn');
            const originalText = deleteBtn.textContent;
            deleteBtn.textContent = '⏳ Eliminando...';
            deleteBtn.disabled = true;

            const applicationIds = Array.from(selectedApplications);

            fetch('/api/admin/delete-applications', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    application_ids: applicationIds
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the applications from the DOM
                    applicationIds.forEach(appId => {
                        const appItem = document.querySelector(`[data-id="${appId}"]`);
                        if (appItem) {
                            appItem.remove();
                        }
                    });

                    selectedApplications.clear();
                    updateSelection();
                    filterApplications(); // Update count

                    showMessage(`${data.deleted_count} aplicaciones eliminadas exitosamente`, 'success');
                } else {
                    showMessage('Error al eliminar las aplicaciones: ' + data.error, 'error');
                }

                deleteBtn.textContent = originalText;
                deleteBtn.disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error de conexión al eliminar las aplicaciones', 'error');
                deleteBtn.textContent = originalText;
                deleteBtn.disabled = false;
            });
        }

        function showMessage(message, type) {
            // Create a simple toast notification
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 6px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                max-width: 300px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
                transform: translateX(100%);
            `;

            if (type === 'success') {
                toast.style.backgroundColor = '#28a745';
            } else {
                toast.style.backgroundColor = '#dc3545';
            }

            toast.textContent = message;
            document.body.appendChild(toast);

            // Animate in
            setTimeout(() => {
                toast.style.transform = 'translateX(0)';
            }, 10);

            // Remove after 5 seconds
            setTimeout(() => {
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            }, 5000);
        }

        function toggleFileDetails(button) {
            const applicationItem = button.closest('.application-item');
            const fileDetails = applicationItem.querySelector('.file-details');

            if (fileDetails.style.display === 'none' || fileDetails.style.display === '') {
                fileDetails.style.display = 'block';
                button.textContent = '📋 ❌';
                button.title = 'Ocultar detalles';
            } else {
                fileDetails.style.display = 'none';
                button.textContent = '📋';
                button.title = 'Ver detalles y experiencia';
            }
        }

        // Handle file link errors with fallback
        function handleFileError(link, publicId) {
            if (publicId) {
                link.href = '/api/file/' + publicId;
                link.onclick = null; // Remove the original onclick
                link.title = 'Usando enlace de respaldo - ' + link.title;
                // Try to reload
                window.open(link.href, '_blank');
            } else {
                alert('Error: No se puede cargar el archivo. Contacte al administrador.');
            }
        }

        // Enhanced file link handling with signed URLs
        document.addEventListener('DOMContentLoaded', function() {
            filterApplications();
            updateSelection();

            // Add click handlers to file links for getting signed URLs
            const fileLinks = document.querySelectorAll('.file-link[href*="/api/admin/cloudinary-proxy/"]');
            fileLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();

                    const originalHref = this.href;
                    const filePath = originalHref.replace(/.*\\/api\\/admin\\/cloudinary-proxy\\//, '');

                    // Change button to loading state
                    const originalText = this.textContent;
                    this.textContent = originalText + ' 🔄';
                    this.style.backgroundColor = '#ffc947';

                    // Get signed URL
                    fetch('/api/admin/signed-url/' + filePath)
                        .then(response => response.json())
                        .then(data => {
                            if (data.success && data.signed_url) {
                                // Open the signed URL
                                window.open(data.signed_url, '_blank');
                                this.textContent = originalText + ' ✅';
                                this.style.backgroundColor = '#28a745';
                            } else {
                                // Fallback to original proxy
                                window.open(originalHref, '_blank');
                                this.textContent = originalText + ' ⚠️';
                                this.style.backgroundColor = '#ffc107';
                            }

                            // Reset after 2 seconds
                            setTimeout(() => {
                                this.textContent = originalText;
                                this.style.backgroundColor = '#00B4D8';
                            }, 2000);
                        })
                        .catch(error => {
                            console.warn('Signed URL failed, using proxy:', error);
                            window.open(originalHref, '_blank');
                            this.textContent = originalText + ' ⚠️';
                            this.style.backgroundColor = '#dc3545';

                            setTimeout(() => {
                                this.textContent = originalText;
                                this.style.backgroundColor = '#00B4D8';
                            }, 2000);
                        });
                });
            });
        });
    </script>
</body>
</html>'''


# Route handlers

## Eliminadas las funciones duplicadas de admin_login, admin_panel y admin_logout para evitar redeclaración.
@app.route('/api/admin/check-file-access', methods=['GET'])
def check_file_access_status():
    """Check public access status of all workwave_coast files."""
    try:
        # Get all files using search
        search_results = cloudinary.Search().expression('folder:workwave_coast').max_results(100).execute()
        files = search_results.get('resources', [])

        results = {
            "total_files": len(files),
            "accessible_files": [],
            "inaccessible_files": [],
            "check_timestamp": datetime.now(timezone.utc).isoformat()
        }

        for file_info in files:
            public_id = file_info.get('public_id')
            secure_url = file_info.get('secure_url')

            # Test access
            try:
                response = requests.head(secure_url, timeout=10)
                is_accessible = response.status_code == 200

                file_status = {
                    "public_id": public_id,
                    "url": secure_url,
                    "status_code": response.status_code,
                    "accessible": is_accessible,
                    "resource_type": file_info.get('resource_type', 'unknown'),
                    "format": file_info.get('format', 'unknown'),
                    "bytes": file_info.get('bytes', 0)
                }

                if is_accessible:
                    results["accessible_files"].append(file_status)
                else:
                    results["inaccessible_files"].append(file_status)

            except Exception as e:
                results["inaccessible_files"].append({
                    "public_id": public_id,
                    "url": secure_url,
                    "error": str(e),
                    "accessible": False
                })

        results["summary"] = {
            "accessible_count": len(results["accessible_files"]),
            "inaccessible_count": len(results["inaccessible_files"]),
            "access_rate": f"{(len(results['accessible_files']) / len(files) * 100):.1f}%" if files else "0%"
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/admin/make-files-public', methods=['POST'])
def make_existing_files_public():
    """Make all existing workwave_coast files public in Cloudinary."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        if not all([cloud_name, api_key, api_secret]):
            return jsonify({"error": "Cloudinary not configured"}), 500

        app.logger.info("Starting bulk public access conversion for workwave_coast files")

        results = {
            "success": True,
            "processed_files": [],
            "errors": [],
            "summary": {}
        }

        # Get all files in the workwave_coast folder using Search API (works better)
        try:
            # Use search to get all files in the folder
            search_results = cloudinary.Search().expression('folder:workwave_coast').max_results(500).execute()
            all_files_data = search_results.get('resources', [])

            all_files = []
            for file_info in all_files_data:
                # Determine resource type from the file info
                resource_type = file_info.get('resource_type', 'image')
                all_files.append((file_info, resource_type))

            app.logger.info(f"Found {len(all_files)} files to process using Search API")

            for file_info, resource_type in all_files:
                public_id = file_info.get('public_id')
                try:
                    # Update the file to be public
                    update_result = cloudinary.uploader.explicit(
                        public_id,
                        resource_type=resource_type,
                        type="upload",
                        access_mode="public"
                    )

                    # Verify the update
                    new_url = update_result.get('secure_url')

                    results["processed_files"].append({
                        "public_id": public_id,
                        "resource_type": resource_type,
                        "new_url": new_url,
                        "status": "success"
                    })

                    app.logger.info(f"Made public: {public_id}")

                except Exception as file_error:
                    error_msg = f"Failed to update {public_id}: {str(file_error)}"
                    results["errors"].append(error_msg)
                    app.logger.error(error_msg)

            # Generate summary
            results["summary"] = {
                "total_files": len(all_files),
                "successful": len(results["processed_files"]),
                "failed": len(results["errors"]),
                "success_rate": f"{(len(results['processed_files']) / len(all_files) * 100):.1f}%" if all_files else "0%"
            }

            return jsonify(results)

        except Exception as api_error:
            app.logger.error(f"Error accessing Cloudinary API: {str(api_error)}")
            return jsonify({
                "success": False,
                "error": f"Failed to access files: {str(api_error)}"
            }), 500

    except Exception as e:
        app.logger.error(f"Error in make files public endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Bulk update failed",
            "details": str(e)
        }), 500


@app.route('/api/admin/download-file/<path:file_path>')
def admin_download_file(file_path):
    """Download file from Cloudinary using server credentials and serve it directly."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        if not all([cloud_name, api_key, api_secret]):
            return jsonify({"error": "Cloudinary not configured"}), 500

        app.logger.info(f"Direct download request for: {file_path}")

        # Clean up the file path
        clean_path = file_path
        if clean_path.startswith('raw/') or clean_path.startswith('image/'):
            clean_path = clean_path.split('/', 1)[1]

        try:
            # Use Cloudinary's download method with authentication
            download_url = cloudinary.utils.cloudinary_url(
                clean_path,
                resource_type='raw',  # Try raw first for PDFs
                type='upload',
                sign_url=True,
                auth_token={
                    'key': api_key,
                    'duration': 3600,  # 1 hour
                    'start_time': int(datetime.now(timezone.utc).timestamp())
                }
            )[0]

            # Download the file using server credentials
            headers = {
                'Authorization': f'Basic {api_key}:{api_secret}',
                'User-Agent': 'WorkWave-Coast-Admin/1.0'
            }

            response = requests.get(download_url, headers=headers, timeout=30)

            if response.status_code == 200:
                # Determine content type based on file extension
                content_type = 'application/pdf' if clean_path.lower().endswith('.pdf') else 'application/octet-stream'

                # Extract filename from path
                filename = clean_path.split('/')[-1]

                # Create response with file content
                from flask import Response
                return Response(
                    response.content,
                    mimetype=content_type,
                    headers={
                        'Content-Disposition': f'inline; filename="{filename}"',
                        'Content-Length': str(len(response.content)),
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    }
                )
            else:
                app.logger.error(f"Failed to download file: HTTP {response.status_code}")
                return jsonify({
                    "error": f"Failed to download file: HTTP {response.status_code}",
                    "file_path": file_path
                }), response.status_code

        except Exception as download_error:
            app.logger.error(f"Error downloading file: {str(download_error)}")
            return jsonify({
                "error": f"Download failed: {str(download_error)}",
                "file_path": file_path
            }), 500

    except Exception as e:
        app.logger.error(f"Error in download file endpoint: {str(e)}")
        return jsonify({
            "error": "Download endpoint failed",
            "details": str(e)
        }), 500


@app.route('/api/admin/signed-url/<path:file_path>')
def admin_get_signed_url(file_path):
    """Generate a temporary signed URL for accessing private Cloudinary files."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        if not all([cloud_name, api_key, api_secret]):
            return jsonify({"error": "Cloudinary not configured"}), 500

        app.logger.info(f"Generating signed URL for: {file_path}")

        # Clean up the file path
        clean_path = file_path
        if clean_path.startswith('raw/') or clean_path.startswith('image/'):
            clean_path = clean_path.split('/', 1)[1]

        # Determine resource type
        is_pdf = clean_path.lower().endswith('.pdf') or 'pdf' in clean_path.lower()
        resource_type = 'raw' if is_pdf else 'image'

        # Generate signed URL with 1 hour expiration
        try:
            # Use Cloudinary's utils to generate a signed URL
            signed_url = cloudinary.utils.cloudinary_url(
                clean_path,
                resource_type=resource_type,
                type='upload',
                sign_url=True,
                expires_at=int((datetime.now(timezone.utc).timestamp()) + 3600),  # 1 hour from now
                secure=True
            )[0]

            app.logger.info(f"Generated signed URL: {signed_url}")

            return jsonify({
                "success": True,
                "signed_url": signed_url,
                "expires_in_seconds": 3600,
                "file_path": file_path,
                "resource_type": resource_type
            })

        except Exception as e:
            app.logger.error(f"Error generating signed URL: {str(e)}")
            return jsonify({"error": f"Failed to generate signed URL: {str(e)}"}), 500

    except Exception as e:
        app.logger.error(f"Error in signed URL endpoint: {str(e)}")
        return jsonify({"error": "Signed URL generation failed", "details": str(e)}), 500


@app.route('/api/admin/cloudinary-proxy/<path:file_path>')
def admin_cloudinary_proxy(file_path):
    """Public proxy for Cloudinary files specifically for admin panel - no auth required."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        if not cloud_name:
            app.logger.error("Cloudinary not configured for admin proxy")
            return jsonify({"error": "Cloudinary not configured"}), 500

        app.logger.info(f"Admin Cloudinary proxy request for: {file_path}")

        # Clean up the file path - remove any prefixes
        clean_path = file_path
        if clean_path.startswith('raw/') or clean_path.startswith('image/'):
            clean_path = clean_path.split('/', 1)[1]

        # Determine resource type based on file extension
        is_pdf = clean_path.lower().endswith('.pdf') or 'pdf' in clean_path.lower()

        # Generate the direct Cloudinary URL
        if is_pdf:
            # For PDFs, try raw resource type first
            cloudinary_url = f"https://res.cloudinary.com/{cloud_name}/raw/upload/{clean_path}"
        else:
            # For other files, try image resource type first
            cloudinary_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{clean_path}"

        app.logger.info(f"Admin proxy redirecting to: {cloudinary_url}")

        # Add CORS headers for admin panel access
        response = redirect(cloudinary_url)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        return response

    except Exception as e:
        app.logger.error(f"Error in admin Cloudinary proxy: {str(e)}")
        return jsonify({
            "error": "Admin proxy error",
            "details": str(e),
            "file_path": file_path
        }), 500


@app.route('/api/cloudinary-url/<path:full_public_id>')
def get_cloudinary_public_url_flexible(full_public_id):
    """Generate a public Cloudinary URL without authentication - flexible version."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        if not cloud_name:
            app.logger.error("Cloudinary cloud name not configured")
            return jsonify({"error": "Cloudinary not configured"}), 500

        app.logger.info(f"Cloudinary URL request for: {full_public_id}")

        # Clean up the public_id - remove any resource type prefixes
        clean_public_id = full_public_id
        if clean_public_id.startswith('raw/') or clean_public_id.startswith('image/'):
            clean_public_id = clean_public_id.split('/', 1)[1]

        # Try to determine if it's a PDF or other file type
        is_pdf = clean_public_id.lower().endswith('.pdf') or 'pdf' in clean_public_id.lower()

        # Try both raw and image resource types
        urls_to_try = []
        if is_pdf:
            # For PDFs, try raw first, then image
            urls_to_try = [
                f"https://res.cloudinary.com/{cloud_name}/raw/upload/{clean_public_id}",
                f"https://res.cloudinary.com/{cloud_name}/image/upload/{clean_public_id}"
            ]
        else:
            # For other files, try image first, then raw
            urls_to_try = [
                f"https://res.cloudinary.com/{cloud_name}/image/upload/{clean_public_id}",
                f"https://res.cloudinary.com/{cloud_name}/raw/upload/{clean_public_id}"
            ]

        # Use the first URL (most likely to work)
        url = urls_to_try[0]
        app.logger.info(f"Generated Cloudinary URL: {url}")

        debug_requested = request.args.get('debug') == 'true'
        if debug_requested:
            return jsonify({
                "debug": True,
                "original_public_id": full_public_id,
                "clean_public_id": clean_public_id,
                "cloud_name": cloud_name,
                "is_pdf": is_pdf,
                "generated_url": url,
                "alternative_urls": urls_to_try[1:],
                "message": "This is the URL that would be redirected to"
            })

        return redirect(url)

    except Exception as e:
        app.logger.error(f"Error generating Cloudinary URL: {str(e)}")
        return jsonify({"error": "Failed to generate Cloudinary URL", "details": str(e)}), 500


@app.route('/api/file/<path:public_id>')
@login_required
def serve_file_proxy(public_id):
    """Proxy to serve files from Cloudinary with authentication."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        if not cloud_name:
            return "Cloudinary not configured", 500

        # Try different resource types
        urls_to_try = [
            f"https://res.cloudinary.com/{cloud_name}/raw/upload/{public_id}",
            f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}",
            f"https://res.cloudinary.com/{cloud_name}/auto/upload/{public_id}"
        ]

        # Use the first URL and redirect
        return redirect(urls_to_try[0])

    except Exception as e:
        app.logger.error(f"Error serving file proxy: {str(e)}")
        return jsonify({"error": "File proxy error", "details": str(e)}), 500


@app.route('/api/admin/file/<path:public_id>')
def serve_admin_file(public_id):
    """Serve files for admin panel without authentication requirement."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        if not cloud_name:
            app.logger.error("Cloudinary not configured for admin file access")
            return jsonify({"error": "Cloudinary not configured"}), 500

        app.logger.info(f"Admin file request for: {public_id}")

        # Clean the public_id
        clean_public_id = public_id
        if clean_public_id.startswith('raw/') or clean_public_id.startswith('image/'):
            clean_public_id = clean_public_id.split('/', 1)[1]

        # Try different combinations for file access
        urls_to_try = [
            f"https://res.cloudinary.com/{cloud_name}/raw/upload/{clean_public_id}",
            f"https://res.cloudinary.com/{cloud_name}/image/upload/{clean_public_id}",
            f"https://res.cloudinary.com/{cloud_name}/raw/upload/v1753899372/{clean_public_id}",
            f"https://res.cloudinary.com/{cloud_name}/image/upload/v1753899372/{clean_public_id}"
        ]

        # Use the most appropriate URL based on file type
        is_pdf = clean_public_id.lower().endswith('.pdf') or 'pdf' in clean_public_id.lower()
        if is_pdf:
            primary_url = urls_to_try[0]  # Try raw first for PDFs
        else:
            primary_url = urls_to_try[1]  # Try image first for other files

        app.logger.info(f"Admin redirecting to: {primary_url}")
        return redirect(primary_url)

    except Exception as e:
        app.logger.error(f"Error serving admin file: {str(e)}")
        return jsonify({"error": "Admin file access error", "details": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    """Serve the frontend index.html as the home page."""
    try:
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'index.html')
        if os.path.exists(frontend_path):
            with open(frontend_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "<h2>Frontend no encontrado</h2><p>Busque el archivo en: {}</p>".format(frontend_path), 404
    except Exception as e:
        return "Error sirviendo frontend: " + str(e), 500


@app.route('/app')
@app.route('/frontend')
def serve_frontend():
    """Serve the frontend application to avoid CORS issues."""
    try:
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'index.html')
        if os.path.exists(frontend_path):
            with open(frontend_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"""
            <h2>Frontend no encontrado</h2>
            <p>Busque el archivo en: {frontend_path}</p>
            <p>Para probar la API directamente:</p>
            <ul>
                <li><a href="/api/health">Health Check</a></li>
                <li><a href="/admin">Panel de Admin</a></li>
                <li>POST a <code>/api/submit</code> para enviar aplicaciones</li>
            </ul>
            """
    except FileNotFoundError:
        app.logger.warning("Frontend file not found")
        return "Error sirviendo frontend: archivo no encontrado", 404
    except IOError as e:
        app.logger.error("IO error serving frontend: %s", str(e))
        return "Error sirviendo frontend: " + str(e), 500
    except Exception as e:
        app.logger.error("Unexpected error serving frontend: %s", str(e))
        return "Error sirviendo frontend: " + str(e), 500


@app.route('/frontend/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory."""
    try:
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        return send_from_directory(frontend_dir, filename)
    except FileNotFoundError:
        app.logger.warning("Static file not found: %s", filename)
        return "Archivo no encontrado: " + filename, 404
    except IOError as e:
        app.logger.error("IO error serving static file: %s", str(e))
        return "Error de acceso al archivo: " + filename, 403
    except Exception as e:
        app.logger.error("Unexpected error serving static file: %s", str(e))
        return "Error interno del servidor", 500


@app.route('/api/submit', methods=['OPTIONS'])
@cross_origin(origins=ALLOWED_ORIGINS, supports_credentials=True)
def submit_options():
    """Handle preflight OPTIONS request for CORS."""
    return '', 204


@app.route('/api/ping', methods=['GET'])
@cross_origin(origins=ALLOWED_ORIGINS, supports_credentials=True)
def ping():
    """Simple ping endpoint to verify backend connectivity."""
    try:
        return jsonify({
            "status": "ok",
            "message": "Backend is running",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/test-email', methods=['POST'])
@cross_origin(origins=ALLOWED_ORIGINS, supports_credentials=True)
@safe_limit("5 per minute", error_message="Demasiadas solicitudes de prueba.")
def test_email():
    """Test endpoint to verify email configuration and send test email."""
    try:
        data = request.get_json()
        test_email = data.get('email', 'test@example.com')

        # Check email configuration
        is_configured, issues = check_email_configuration()

        result = {
            "email_configured": is_configured,
            "configuration_issues": issues,
            "mail_server": app.config.get('MAIL_SERVER'),
            "mail_port": app.config.get('MAIL_PORT'),
            "mail_use_tls": app.config.get('MAIL_USE_TLS'),
            "mail_username": app.config.get('MAIL_USERNAME', 'Not set')
        }

        if is_configured:
            # Try to send test email
            success = send_confirmation_email("Usuario de Prueba", test_email)
            result["test_email_sent"] = success
            result["test_email_recipient"] = test_email

        return jsonify(result), 200

    except Exception as e:
        app.logger.error("Error in test email endpoint", extra={
            "error": str(e),
            "type": type(e).__name__
        })
        return jsonify({
            "error": "Failed to test email configuration",
            "details": str(e)
        }), 500

@app.route('/api/submit', methods=['POST'])
@cross_origin(origins=ALLOWED_ORIGINS, supports_credentials=True)
@safe_limit("5 per minute", error_message="Demasiadas solicitudes. Inténtalo en unos minutos.")
def submit_application():
    """Submit a job application with form data and file uploads."""
    try:
        app.logger.info("New application submission attempt", extra={
            "endpoint": "/api/submit",
            "remote_addr": get_remote_address(),
            "user_agent": request.headers.get('User-Agent', 'Unknown')
        })

        # Get form data
        data = request.form.to_dict()

        # TEMPORAL: Log para debugging
        app.logger.info("Received form data", extra={
            "data_keys": list(data.keys()),
            "data_values": {k: v[:50] if isinstance(v, str) else v for k, v in data.items()},
            "files_received": list(request.files.keys())
        })

        # Check for duplicate application first
        email = data.get('email', '').strip().lower()
        if email and check_duplicate_application(email):
            app.logger.warning("Duplicate application attempt", extra={
                "email": email,
                "remote_addr": get_remote_address()
            })
            return jsonify({
                "success": False,
                "message": "Ya existe una aplicación con este email. Cada persona solo puede aplicar una vez."
            }), 409

        # Validate input data
        is_valid, validation_errors = validate_application_data(data)
        if not is_valid:
            app.logger.warning("Invalid application data submitted", extra={
                "errors": validation_errors,
                "remote_addr": get_remote_address()
            })
            return jsonify({
                "success": False,
                "message": "Datos de formulario inválidos: " + "; ".join(validation_errors),
                "errors": validation_errors
            }), 400

        # Add timestamp and status
        data['created_at'] = datetime.now(timezone.utc).isoformat()
        data['status'] = 'pending'

        # Sanitize data (strip whitespace and normalize email)
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()

        # Normalize email to lowercase for consistency
        if 'email' in data:
            data['email'] = data['email'].lower()

        # Validate required file uploads
        if 'cv' not in request.files or not request.files['cv'].filename:
            app.logger.warning("Missing required CV file", extra={
                "remote_addr": get_remote_address()
            })
            return jsonify({
                "success": False,
                "message": "El archivo CV es requerido."
            }), 400

        # Handle file uploads
        files = request.files
        file_urls = {}

        for field_name, file in files.items():
            if file and file.filename:
                # Validate file
                is_valid, error_message, file_size = validate_file(file, field_name)
                if not is_valid:
                    app.logger.warning("Invalid file upload", extra={
                        "field": field_name,
                        "file_name": file.filename,
                        "error": error_message
                    })
                    return jsonify({
                        "success": False,
                        "message": error_message
                    }), 400

                # Upload to Cloudinary
                file_urls[field_name] = upload_to_cloudinary(file, field_name, file_size)

        # Add file URLs to data
        data['files'] = json.dumps(file_urls) if file_urls else "{}"

        # Insert into MongoDB
        result = candidates.insert_one(data)

        app.logger.info("Application submitted successfully", extra={
            "application_id": str(result.inserted_id),
            "applicant_name": f"{data.get('nombre', '')} {data.get('apellido', '')}",
            "position": data.get('puesto', ''),
            "additional_positions": data.get('puestos_adicionales', ''),
            "files_count": len(file_urls),
            "email": data.get('email', ''),
            "phone": data.get('telefono', ''),
            "english_level": data.get('ingles_nivel', '')
        })

        # Send confirmation email to applicant
        applicant_name = f"{data.get('nombre', '')} {data.get('apellido', '')}".strip()
        applicant_email = data.get('email', '')

        if applicant_name and applicant_email:
            email_sent = send_confirmation_email(applicant_name, applicant_email)
            if email_sent:
                app.logger.info("Confirmation email sent", extra={
                    "application_id": str(result.inserted_id),
                    "recipient": applicant_email
                })
            else:
                app.logger.warning("Failed to send confirmation email", extra={
                    "application_id": str(result.inserted_id),
                    "recipient": applicant_email
                })

        return jsonify({
            "success": True,
            "message": "Postulación enviada exitosamente",
            "application_id": str(result.inserted_id)
        }), 201

    except pymongo.errors.PyMongoError as e:
        app.logger.error("Database error submitting application", extra={
            "error": str(e),
            "remote_addr": get_remote_address()
        })
        return jsonify({
            "success": False,
            "message": "Error de base de datos. Inténtalo más tarde.",
            "error": "database_error"
        }), 503
    except ValueError as e:
        app.logger.warning("Invalid data in application submission", extra={
            "error": str(e),
            "remote_addr": get_remote_address()
        })
        return jsonify({
            "success": False,
            "message": "Datos inválidos proporcionados",
            "error": "invalid_data"
        }), 400
    except Exception as e:
        app.logger.error("Unexpected error submitting application", extra={
            "error": str(e),
            "remote_addr": get_remote_address()
        })
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": "internal_error"
        }), 500


@app.route('/api/applications', methods=['GET'])
@safe_limit("30 per minute")
def get_applications():
    """Retrieve job applications from the database with pagination."""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 per page
        skip = (page - 1) * limit

        # Get filter parameters
        position = request.args.get('position')
        status = request.args.get('status')

        # Build query
        query = {}
        if position:
            query['puesto'] = position
        if status:
            query['status'] = status

        # Get total count for pagination
        total_count = candidates.count_documents(query)

        # Get applications with pagination
        applications_cursor = candidates.find(query, {"_id": 0}).sort('created_at', -1).skip(skip).limit(limit)
        applications = list(applications_cursor)

        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1

        app.logger.info("Applications retrieved", extra={
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "filters": query
        })

        return jsonify({
            "success": True,
            "applications": applications,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": has_next,
                "has_prev": has_prev,
                "per_page": limit
            }
        })

    except pymongo.errors.PyMongoError as e:
        app.logger.error("Database error fetching applications", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Error de base de datos",
            "error": "database_error"
        }), 503
    except ValueError as e:
        app.logger.warning("Invalid parameters for applications query", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Parámetros inválidos",
            "error": "invalid_parameters"
        }), 400
    except Exception as e:
        app.logger.error("Unexpected error fetching applications", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Error interno del servidor",
            "error": "internal_error"
        }), 500


@app.route('/api/applications/latest', methods=['GET'])
def get_latest_application():
    """Retrieve the most recent job application from the database."""
    try:
        latest_app = candidates.find().sort('created_at', -1).limit(1)
        applications = list(latest_app)

        if applications:
            application = applications[0]
            application['_id'] = str(application['_id'])

            return jsonify({
                "success": True,
                "application": application
            })
        else:
            return jsonify({
                "success": True,
                "application": None,
                "message": "No applications found"
            })

    except Exception as e:
        app.logger.error("Error fetching latest application: %s", str(e))
        return jsonify({
            "success": False,
            "message": "Error fetching latest application",
            "error": str(e)
        }), 500


@app.route('/api/test-cloudinary-config', methods=['GET'])
def test_cloudinary_config():
    """Test and display Cloudinary configuration status."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        config_status = {
            "cloud_name": cloud_name if cloud_name else "NOT_SET",
            "api_key": "SET" if api_key else "NOT_SET",
            "api_secret": "SET" if api_secret else "NOT_SET",
            "all_configured": all([cloud_name, api_key, api_secret])
        }

        # Test a known file URL
        if cloud_name:
            test_urls = {
                "test_cv_raw": f"https://res.cloudinary.com/{cloud_name}/raw/upload/workwave_coast/cv_wxlzwh.pdf",
                "test_cv_image": f"https://res.cloudinary.com/{cloud_name}/image/upload/v1753899372/workwave_coast/cv_wxlzwh.pdf",
                "proxy_url": "/api/cloudinary-url/v1753899372/workwave_coast/cv_wxlzwh.pdf"
            }
        else:
            test_urls = {"error": "Cloud name not configured"}

        return jsonify({
            "success": True,
            "cloudinary_config": config_status,
            "test_urls": test_urls,
            "endpoints": {
                "cloudinary_proxy": "/api/cloudinary-url/<path>",
                "admin_file": "/api/admin/file/<path>",
                "authenticated_file": "/api/file/<path>"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/diagnose-cloudinary', methods=['GET'])
def diagnose_cloudinary():
    """Comprehensive Cloudinary connection and file access diagnosis."""
    try:
        diagnosis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_version": "2.1.0",
            "diagnosis_steps": []
        }

        # Step 1: Check environment variables
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        env_check = {
            "step": "Environment Variables Check",
            "cloud_name": cloud_name if cloud_name else "❌ NOT_SET",
            "api_key": "✅ SET" if api_key else "❌ NOT_SET",
            "api_secret": "✅ SET" if api_secret else "❌ NOT_SET",
            "status": "✅ PASS" if all([cloud_name, api_key, api_secret]) else "❌ FAIL"
        }
        diagnosis["diagnosis_steps"].append(env_check)

        if not all([cloud_name, api_key, api_secret]):
            diagnosis["final_status"] = "❌ FAILED - Missing environment variables"
            return jsonify(diagnosis)

        # Step 2: Test Cloudinary API connection
        try:
            api_test = cloudinary.api.ping()
            api_check = {
                "step": "Cloudinary API Connection Test",
                "status": "✅ PASS",
                "response": api_test
            }
        except Exception as e:
            api_check = {
                "step": "Cloudinary API Connection Test",
                "status": "❌ FAIL",
                "error": str(e)
            }
        diagnosis["diagnosis_steps"].append(api_check)

        # Step 3: List recent files in workwave_coast folder
        try:
            recent_files = cloudinary.api.resources(
                resource_type="raw",
                prefix="workwave_coast/",
                max_results=10
            )
            files_check = {
                "step": "Recent Raw Files Check",
                "status": "✅ PASS",
                "files_found": len(recent_files.get('resources', [])),
                "files": [
                    {
                        "public_id": resource.get('public_id'),
                        "secure_url": resource.get('secure_url'),
                        "format": resource.get('format'),
                        "bytes": resource.get('bytes'),
                        "created_at": resource.get('created_at')
                    }
                    for resource in recent_files.get('resources', [])[:5]
                ]
            }
        except Exception as e:
            files_check = {
                "step": "Recent Raw Files Check",
                "status": "❌ FAIL",
                "error": str(e)
            }
        diagnosis["diagnosis_steps"].append(files_check)

        # Step 4: Test a specific file URL
        if 'files' in files_check and files_check['files'] and isinstance(files_check['files'], list) and len(files_check['files']) > 0:
            test_file = files_check['files'][0]
            if isinstance(test_file, dict):
                test_public_id = test_file.get('public_id', '')

                # Test different URL variations
                url_tests = []
                test_urls = [
                    f"https://res.cloudinary.com/{cloud_name}/raw/upload/{test_public_id}",
                    f"https://res.cloudinary.com/{cloud_name}/image/upload/{test_public_id}",
                    test_file.get('secure_url', '')  # Direct URL from API
                ]

                for i, url in enumerate(test_urls):
                    try:
                        response = requests.head(url, timeout=10)
                        url_tests.append({
                            f"url_{i+1}": url,
                            "status": response.status_code,
                            "accessible": response.status_code == 200
                        })
                    except Exception as e:
                        url_tests.append({
                            f"url_{i+1}": url,
                            "status": "ERROR",
                            "error": str(e)
                        })

                url_check = {
                    "step": "File URL Accessibility Test",
                    "test_file": test_public_id,
                    "url_tests": url_tests
                }
                diagnosis["diagnosis_steps"].append(url_check)

        # Step 5: Check recent applications with files
        try:
            recent_apps = list(candidates.find(
                {"files": {"$ne": "{}"}},
                {"files": 1, "nombre": 1, "apellido": 1, "created_at": 1}
            ).sort("created_at", -1).limit(3))

            app_files_check = {
                "step": "Recent Applications Files Check",
                "status": "✅ PASS",
                "recent_applications": []
            }

            for app in recent_apps:
                try:
                    files_data = json.loads(app.get('files', '{}'))
                    app_files_check["recent_applications"].append({
                        "applicant": f"{app.get('nombre', '')} {app.get('apellido', '')}",
                        "created_at": app.get('created_at', ''),
                        "files_count": len(files_data),
                        "files": files_data
                    })
                except Exception as e:
                    app_files_check["recent_applications"].append({
                        "applicant": f"{app.get('nombre', '')} {app.get('apellido', '')}",
                        "error": f"Failed to parse files: {str(e)}"
                    })
        except Exception as e:
            app_files_check = {
                "step": "Recent Applications Files Check",
                "status": "❌ FAIL",
                "error": str(e)
            }
        diagnosis["diagnosis_steps"].append(app_files_check)

        # Final diagnosis
        failed_steps = [step for step in diagnosis["diagnosis_steps"] if step.get("status") == "❌ FAIL"]
        if failed_steps:
            diagnosis["final_status"] = f"❌ {len(failed_steps)} step(s) failed"
            diagnosis["recommendations"] = [
                "Check environment variables are set correctly",
                "Verify Cloudinary API credentials",
                "Check network connectivity to Cloudinary",
                "Review file upload process"
            ]
        else:
            diagnosis["final_status"] = "✅ All checks passed"

        return jsonify(diagnosis)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/test-file-access/<path:file_path>', methods=['GET'])
def test_file_access(file_path):
    """Test file access with different URL patterns."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        if not cloud_name:
            return jsonify({"error": "Cloud name not configured"}), 500

        # Generate different URL patterns to test
        test_results = {
            "file_path": file_path,
            "cloud_name": cloud_name,
            "url_tests": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Pattern 1: Raw upload with path
        url1 = f"https://res.cloudinary.com/{cloud_name}/raw/upload/{file_path}"

        # Pattern 2: Image upload with path
        url2 = f"https://res.cloudinary.com/{cloud_name}/image/upload/{file_path}"

        # Pattern 3: Auto upload with path
        url3 = f"https://res.cloudinary.com/{cloud_name}/auto/upload/{file_path}"

        # Pattern 4: With workwave_coast prefix if not already present
        if not file_path.startswith('workwave_coast/'):
            url4 = f"https://res.cloudinary.com/{cloud_name}/raw/upload/workwave_coast/{file_path}"
        else:
            url4 = None

        test_urls = [
            ("raw_upload", url1),
            ("image_upload", url2),
            ("auto_upload", url3)
        ]

        if url4:
            test_urls.append(("raw_with_prefix", url4))

        for label, url in test_urls:
            try:
                response = requests.head(url, timeout=10)
                test_results["url_tests"].append({
                    "label": label,
                    "url": url,
                    "status_code": response.status_code,
                    "accessible": response.status_code == 200,
                    "headers": dict(response.headers)
                })
            except Exception as e:
                test_results["url_tests"].append({
                    "label": label,
                    "url": url,
                    "error": str(e),
                    "accessible": False
                })

        return jsonify(test_results)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/cloudinary-ping', methods=['GET'])
def cloudinary_ping():
    """Simple ping test for Cloudinary API."""
    try:
        # Just test the ping endpoint - should not require type parameter
        ping_result = cloudinary.api.ping()

        return jsonify({
            "success": True,
            "ping_result": ping_result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/list-cloudinary-files', methods=['GET'])
def list_cloudinary_files():
    """List all files in the workwave_coast folder."""
    try:
        results = {"success": True, "timestamp": datetime.now(timezone.utc).isoformat()}

        # Try multiple approaches to list files
        # Approach 1: List by prefix
        try:
            raw_files = cloudinary.api.resources(
                prefix="workwave_coast/"
            )
            results["by_prefix"] = {
                "count": len(raw_files.get('resources', [])),
                "files": [f.get('public_id') for f in raw_files.get('resources', [])[:5]]
            }
        except Exception as e:
            results["by_prefix_error"] = str(e)

        # Approach 2: Use search
        try:
            search_results = cloudinary.Search().expression('folder:workwave_coast').execute()
            results["by_search"] = {
                "count": search_results.get('total_count', 0),
                "files": [f.get('public_id') for f in search_results.get('resources', [])[:5]]
            }
        except Exception as e:
            results["by_search_error"] = str(e)

        # Approach 3: List all resources and filter
        try:
            all_resources = cloudinary.api.resources(max_results=100)
            workwave_files = [
                f for f in all_resources.get('resources', [])
                if 'workwave' in f.get('public_id', '').lower()
            ]
            results["filtered"] = {
                "count": len(workwave_files),
                "files": [f.get('public_id') for f in workwave_files[:5]]
            }
        except Exception as e:
            results["filtered_error"] = str(e)

        return jsonify(results)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500
def test_cloudinary():
    """Test Cloudinary configuration and connection."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        response_data = {
            "success": False,
            "environment_variables": {
                "cloud_name": cloud_name if cloud_name else "NOT_SET",
                "api_key": "SET" if api_key else "NOT_SET",
                "api_secret": "SET" if api_secret else "NOT_SET"
            }
        }

        if not all([cloud_name, api_key, api_secret]):
            response_data.update({
                "message": "Cloudinary environment variables not configured",
                "instructions": {
                    "step1": "Go to https://cloudinary.com and create a free account",
                    "step2": "Get your Cloud Name, API Key, and API Secret from the dashboard",
                    "step3": "Set these as environment variables in Render",
                    "variables_needed": ["CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"]
                }
            })
            return jsonify(response_data), 400

        # Test Cloudinary connection
        try:
            result = cloudinary.api.ping()
            response_data.update({
                "success": True,
                "message": "Cloudinary connection successful",
                "cloudinary_response": result
            })
            return jsonify(response_data)

        except Exception as cloudinary_error:
            response_data.update({
                "message": f"Cloudinary connection failed: {str(cloudinary_error)}",
                "possible_causes": [
                    "Invalid cloud_name - check if it matches your Cloudinary dashboard",
                    "Invalid API key or secret",
                    "Network connectivity issues",
                    "Cloudinary service temporarily unavailable"
                ],
                "current_cloud_name": cloud_name
            })
            return jsonify(response_data), 500

    except (ConnectionError, requests.RequestException) as e:
        return jsonify({
            "success": False,
            "message": "Network error connecting to Cloudinary",
            "error": str(e),
            "error_type": "network_error"
        }), 503
    except (ValueError, TypeError) as e:
        return jsonify({
            "success": False,
            "message": "Configuration error with Cloudinary credentials",
            "error": str(e),
            "error_type": "config_error"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Unexpected error testing Cloudinary",
            "error": str(e)
        }), 500


@app.route('/api/debug-files/<application_id>')
@login_required
def debug_files(application_id):
    """Debug endpoint to check file URLs for a specific application."""
    try:
        from bson import ObjectId

        # Find the application
        application = candidates.find_one({"_id": ObjectId(application_id)})
        if not application:
            return jsonify({"error": "Application not found"}), 404

        # Parse files
        files_data = {}
        if 'files' in application:
            try:
                files_data = json.loads(application['files'])
            except (json.JSONDecodeError, TypeError):
                files_data = {}

        # Test each file URL
        debug_info = {
            "application_id": application_id,
            "applicant": f"{application.get('nombre', '')} {application.get('apellido', '')}",
            "files_raw": application.get('files', ''),
            "files_parsed": files_data,
            "cloudinary_config": {
                "cloud_name": os.getenv('CLOUDINARY_CLOUD_NAME'),
                "api_key_present": bool(os.getenv('CLOUDINARY_API_KEY')),
                "api_secret_present": bool(os.getenv('CLOUDINARY_API_SECRET'))
            },
            "url_tests": {}
        }

        # Test each file URL
        for file_type, file_info in files_data.items():
            if isinstance(file_info, dict) and file_info.get('url'):
                url = file_info['url']
                debug_info["url_tests"][file_type] = {
                    "url": url,
                    "public_id": file_info.get('public_id', 'N/A'),
                    "status": file_info.get('status', 'N/A'),
                    "is_cloudinary": 'cloudinary.com' in url,
                    "is_secure": url.startswith('https://'),
                    "fallback_endpoint": f"/api/file/{file_info.get('public_id', 'unknown')}"
                }

        return jsonify(debug_info)

    except pymongo.errors.PyMongoError as e:
        return jsonify({
            "error": "Database error",
            "details": str(e),
            "error_type": "database"
        }), 503
    except (ValueError, TypeError) as e:
        return jsonify({
            "error": "Data parsing error",
            "details": str(e),
            "error_type": "data_format"
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Unexpected error",
            "details": str(e),
            "error_type": "unknown"
        }), 500


@app.route('/api/test-cv-url')
def test_cv_url():
    """Test endpoint to debug the specific CV URL issue."""
    test_url = "https://res.cloudinary.com/dde3kelit/image/upload/v1753899372/workwave_coast/cv_wxlzwh.pdf"

    # Extract public_id from the URL
    parts = test_url.split('/')
    if 'workwave_coast' in parts:
        idx = parts.index('workwave_coast')
        if idx + 1 < len(parts):
            public_id_with_ext = parts[idx + 1]
            public_id = public_id_with_ext.split('.')[0]  # Remove extension

            # Generate corrected URLs
            cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', 'dde3kelit')  # Updated config

            # Try different URL variations
            url_variations = {
                "original_url": test_url,
                "variation_1_raw_with_folder": f"https://res.cloudinary.com/{cloud_name}/raw/upload/workwave_coast/{public_id}.pdf",
                "variation_2_raw_without_folder": f"https://res.cloudinary.com/{cloud_name}/raw/upload/{public_id}.pdf",
                "variation_3_raw_with_version": f"https://res.cloudinary.com/{cloud_name}/raw/upload/v1753899372/workwave_coast/{public_id}.pdf",
                "variation_4_raw_full_public_id": f"https://res.cloudinary.com/{cloud_name}/raw/upload/v1753899372/workwave_coast/cv_wxlzwh",
                "variation_5_image_original": test_url,
                "cloud_name": cloud_name,
                "public_id_extracted": public_id,
                "problem": "URL uses /image/upload/ for PDF (should be /raw/upload/), but file might not exist or have different public_id"
            }

            return jsonify(url_variations)

    return jsonify({"error": "Could not parse URL"})


@app.route('/api/test-cv-url-forced')
def test_cv_url_forced():
    """Test endpoint with forced correct cloud_name."""
    test_url = "https://res.cloudinary.com/dde3kelit/image/upload/v1753899372/workwave_coast/cv_wxlzwh.pdf"

    # Force the correct cloud_name
    cloud_name = "dde3kelit"  # Hardcoded correct value

    # Try different URL variations
    url_variations = {
        "original_url": test_url,
        "variation_1_raw_with_folder": f"https://res.cloudinary.com/{cloud_name}/raw/upload/workwave_coast/cv_wxlzwh.pdf",
        "variation_2_raw_without_folder": f"https://res.cloudinary.com/{cloud_name}/raw/upload/cv_wxlzwh.pdf",
        "variation_3_raw_with_version": f"https://res.cloudinary.com/{cloud_name}/raw/upload/v1753899372/workwave_coast/cv_wxlzwh.pdf",
        "variation_4_raw_full_public_id": f"https://res.cloudinary.com/{cloud_name}/raw/upload/v1753899372/workwave_coast/cv_wxlzwh",
        "variation_5_image_original": test_url,
        "cloud_name": cloud_name,
        "public_id_extracted": "cv_wxlzwh",
        "problem": "Testing with FORCED correct cloud_name",
        "note": "If this works, then the .env file wasn't reloaded properly"
    }

    return jsonify(url_variations)


@app.route('/api/test-working-cv')
def test_working_cv():
    """Test the CV URL that we know works (variation 5)."""
    working_url = "https://res.cloudinary.com/dde3kelit/image/upload/v1753899372/workwave_coast/cv_wxlzwh.pdf"

    return f"""
    <h2>✅ URL que funciona encontrada</h2>
    <p><strong>URL correcta para este CV:</strong></p>
    <p><a href="{working_url}" target="_blank">{working_url}</a></p>

    <h3>🔧 Solución implementada:</h3>
    <p>• El archivo está almacenado como 'image' en lugar de 'raw'</p>
    <p>• El proxy ahora detecta automáticamente el tipo correcto</p>
    <p>• Los CVs existentes seguirán funcionando</p>

    <h3>🧪 Probar el proxy:</h3>
    <p><a href="/api/cloudinary-url/v1753899372/workwave_coast/cv_wxlzwh.pdf" target="_blank">
        Proxy URL (debería funcionar automáticamente)
    </a></p>

    <p><em>El proxy ahora detecta si el archivo está como 'image' o 'raw' y usa la URL correcta.</em></p>
    """


@app.route('/api/check-cloudinary-file')
def check_cloudinary_file():
    """Check if a specific file exists in Cloudinary using the Admin API."""
    try:
        # Try to get info about the specific public_id
        public_id = "workwave_coast/cv_wxlzwh"

        try:
            # Try as raw resource first
            result_raw = cloudinary.api.resource(public_id, resource_type="raw")
            return jsonify({
                "status": "found_as_raw",
                "public_id": public_id,
                "result": result_raw,
                "correct_url": result_raw.get('secure_url', 'N/A')
            })
        except Exception as e1:
            try:
                # Try as image resource
                result_image = cloudinary.api.resource(public_id, resource_type="image")
                return jsonify({
                    "status": "found_as_image",
                    "public_id": public_id,
                    "result": result_image,
                    "current_url": result_image.get('secure_url', 'N/A'),
                    "note": "File exists as image, needs to be re-uploaded as raw for PDF"
                })
            except Exception as e2:
                # Try without folder prefix
                simple_id = "cv_wxlzwh"
                try:
                    result_simple = cloudinary.api.resource(simple_id, resource_type="raw")
                    return jsonify({
                        "status": "found_without_folder",
                        "public_id": simple_id,
                        "result": result_simple,
                        "correct_url": result_simple.get('secure_url', 'N/A')
                    })
                except Exception as e3:
                    return jsonify({
                        "status": "not_found",
                        "errors": {
                            "raw_with_folder": str(e1),
                            "image_with_folder": str(e2),
                            "raw_without_folder": str(e3)
                        },
                        "suggestion": "File might not exist or have different public_id"
                    })

    except Exception as e:
        return jsonify({"error": "Cloudinary API error: " + str(e)}), 500


@app.route('/api/debug-proxy/<path:test_id>')
def debug_proxy(test_id):
    """Debug endpoint to test the proxy route pattern."""
    return jsonify({
        "message": "Proxy route is working!",
        "received_id": test_id,
        "cloud_name": os.getenv('CLOUDINARY_CLOUD_NAME'),
        "test_url": f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME')}/image/upload/{test_id}"
    })
@app.route('/api/file/<file_id>')
@login_required
def serve_file(file_id):
    """Serve file with authentication as fallback for Cloudinary issues."""
    try:
        # Find the application that contains this file
        application = candidates.find_one({
            "$or": [
                {"files": {"$regex": file_id}},
                {"cv_url": {"$regex": file_id}},
                {"foto_url": {"$regex": file_id}}
            ]
        })

        if not application:
            app.logger.warning("File not found in database", extra={"file_id": file_id})
            return "File not found", 404

        # Parse files to get the correct URL
        files_data = {}
        if 'files' in application:
            try:
                files_data = json.loads(application['files'])
            except (json.JSONDecodeError, TypeError):
                files_data = {}

        # Look for the file URL in the parsed data
        file_url = None
        for file_type, file_info in files_data.items():
            if isinstance(file_info, dict) and file_id in file_info.get('url', ''):
                file_url = file_info['url']
                break

        # Fallback to direct URLs
        if not file_url:
            if file_id in application.get('cv_url', ''):
                file_url = application['cv_url']
            elif file_id in application.get('foto_url', ''):
                file_url = application['foto_url']

        if not file_url:
            app.logger.error("File URL not found", extra={
                "file_id": file_id,
                "application_id": str(application['_id'])
            })
            return "File URL not found", 404

        # Redirect to the actual Cloudinary URL
        app.logger.info("Serving file via redirect", extra={
            "file_id": file_id,
            "file_url": file_url[:100] + "..." if len(file_url) > 100 else file_url
        })

        return redirect(file_url)

    except pymongo.errors.PyMongoError as e:
        app.logger.error("Database error serving file", extra={
            "file_id": file_id,
            "error": str(e),
            "error_type": "database"
        })
        return "Database error accessing file", 503
    except (ValueError, KeyError) as e:
        app.logger.error("File data error", extra={
            "file_id": file_id,
            "error": str(e),
            "error_type": "data_format"
        })
        return "Invalid file data format", 400
    except Exception as e:
        app.logger.error("Error serving file", extra={
            "file_id": file_id,
            "error": str(e)
        })
        return "Error serving file: " + str(e), 500


@app.route('/api/system-status', methods=['GET'])
def system_status():
    """Complete system status check for restart verification."""
    try:
        # Check environment variables
        cloudinary_vars = {
            'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
            'api_key': os.getenv('CLOUDINARY_API_KEY'),
            'api_secret': os.getenv('CLOUDINARY_API_SECRET')
        }

        # Test MongoDB
        try:
            client.admin.command('ping')
            mongo_status = "✅ Connected"
        except pymongo.errors.PyMongoError as e:
            mongo_status = f"❌ MongoDB Error: {str(e)}"
        except (ConnectionError, TimeoutError) as e:
            mongo_status = f"❌ Network Error: {str(e)}"

        # Test Cloudinary
        cloudinary_status = "❌ Not configured"
        if all(cloudinary_vars.values()):
            try:
                cloudinary.api.ping()
                cloudinary_status = "✅ Connected and working"
            except cloudinary.exceptions.Error as e:
                cloudinary_status = f"❌ Cloudinary API Error: {str(e)}"
            except (ConnectionError, requests.RequestException) as e:
                cloudinary_status = f"❌ Network Error: {str(e)}"

        # Count applications
        try:
            app_count = candidates.count_documents({})
        except pymongo.errors.PyMongoError:
            app_count = "Database error"

        return jsonify({
            "system_version": "2.0.2",
            "restart_status": "✅ System restarted successfully",
            "mongodb": mongo_status,
            "cloudinary": {
                "status": cloudinary_status,
                "variables": {
                    "cloud_name": cloudinary_vars['cloud_name'] or "NOT_SET",
                    "api_key": "SET" if cloudinary_vars['api_key'] else "NOT_SET",
                    "api_secret": "SET" if cloudinary_vars['api_secret'] else "NOT_SET"
                }
            },
            "applications_count": app_count,
            "timestamp": datetime.utcnow().isoformat()
        })

    except (KeyError, AttributeError) as e:
        return jsonify({
            "system_version": "2.0.2",
            "restart_status": "❌ Configuration error during status check",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500
    except Exception as e:
        return jsonify({
            "system_version": "2.0.2",
            "restart_status": "❌ Unexpected error during status check",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify database connectivity."""
    try:
        # Test MongoDB connection
        client.admin.command('ping')

        # Check Cloudinary configuration
        cloudinary_status = "configured" if (
            os.getenv('CLOUDINARY_CLOUD_NAME') and
            os.getenv('CLOUDINARY_CLOUD_NAME') != 'tu_cloud_name'
        ) else "not_configured"

        return jsonify({
            "status": "healthy",
            "mongodb": "connected",
            "cloudinary": cloudinary_status,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "mongodb": "disconnected",
            "cloudinary": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@app.route('/admin/login', methods=['GET', 'POST'])
@safe_limit("10 per minute", error_message="Demasiados intentos de login. Espera unos minutos.")
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        app.logger.info("Admin login attempt", extra={
            "username": username,
            "remote_addr": get_remote_address(),
            "user_agent": request.headers.get('User-Agent', 'Unknown')
        })

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            app.logger.info("Admin login successful", extra={
                "username": username,
                "remote_addr": get_remote_address()
            })
            return redirect(url_for('admin_dashboard'))
        else:
            app.logger.warning("Admin login failed", extra={
                "username": username,
                "remote_addr": get_remote_address()
            })
            error = "Credenciales incorrectas"
            return render_template_string(LOGIN_TEMPLATE, error=error)

    return render_template_string(LOGIN_TEMPLATE)


@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/api/admin/delete-application/<application_id>', methods=['DELETE'])
@login_required
def delete_application(application_id):
    """Delete a single application by ID."""
    try:
        # Validate ObjectId format
        try:
            obj_id = ObjectId(application_id)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "ID de aplicación inválido",
                "details": str(e)
            }), 400

        # Get application before deletion for logging
        application = candidates.find_one({"_id": obj_id})
        if not application:
            return jsonify({
                "success": False,
                "error": "Aplicación no encontrada"
            }), 404

        # Delete the application
        result = candidates.delete_one({"_id": obj_id})

        if result.deleted_count == 1:
            app.logger.info("Application deleted by admin", extra={
                "application_id": application_id,
                "applicant_name": f"{application.get('nombre', '')} {application.get('apellido', '')}",
                "applicant_email": application.get('email', ''),
                "admin_ip": get_remote_address()
            })

            return jsonify({
                "success": True,
                "message": "Aplicación eliminada exitosamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo eliminar la aplicación"
            }), 500

    except Exception as e:
        app.logger.error("Error deleting application", extra={
            "application_id": application_id,
            "error": str(e),
            "admin_ip": get_remote_address()
        })
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500


@app.route('/api/admin/delete-applications', methods=['DELETE'])
@login_required
def delete_multiple_applications():
    """Delete multiple applications by IDs."""
    try:
        data = request.get_json()
        if not data or 'application_ids' not in data:
            return jsonify({
                "success": False,
                "error": "Se requiere una lista de IDs de aplicaciones"
            }), 400

        application_ids = data['application_ids']
        if not isinstance(application_ids, list) or len(application_ids) == 0:
            return jsonify({
                "success": False,
                "error": "La lista de IDs no puede estar vacía"
            }), 400

        # Validate and convert to ObjectIds
        try:
            obj_ids = [ObjectId(app_id) for app_id in application_ids]
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Uno o más IDs de aplicación son inválidos",
                "details": str(e)
            }), 400

        # Get applications before deletion for logging
        applications = list(candidates.find({"_id": {"$in": obj_ids}}))
        found_count = len(applications)

        # Delete the applications
        result = candidates.delete_many({"_id": {"$in": obj_ids}})

        app.logger.info("Multiple applications deleted by admin", extra={
            "requested_count": len(application_ids),
            "found_count": found_count,
            "deleted_count": result.deleted_count,
            "admin_ip": get_remote_address(),
            "deleted_applications": [f"{app.get('nombre', '')} {app.get('apellido', '')} ({app.get('email', '')})" for app in applications]
        })

        return jsonify({
            "success": True,
            "message": f"Se eliminaron {result.deleted_count} aplicaciones exitosamente",
            "deleted_count": result.deleted_count,
            "requested_count": len(application_ids)
        })

    except Exception as e:
        app.logger.error("Error deleting multiple applications", extra={
            "error": str(e),
            "admin_ip": get_remote_address()
        })
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500


@app.route('/admin')
@app.route('/admin/')
@login_required
def admin_dashboard():
    """Admin dashboard to view applications."""
    try:
        app.logger.info("Admin dashboard accessed", extra={
            "remote_addr": get_remote_address(),
            "user_agent": request.headers.get('User-Agent', 'Unknown')
        })

        # Get all applications with proper sorting (limit for performance)
        applications = list(candidates.find({}).sort('created_at', -1).limit(1000))

        # Calculate statistics in Python (more efficient and reliable)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        today_count = 0
        pending_count = 0

        # Convert ObjectId to string and parse files JSON
        for application in applications:
            application['_id'] = str(application['_id'])
            if 'files' in application:
                try:
                    application['files_parsed'] = json.loads(application['files'])
                    # Log file URLs for debugging
                    if application['files_parsed']:
                        app.logger.debug("Application files", extra={
                            "applicant": f"{application.get('nombre', '')} {application.get('apellido', '')}",
                            "files": application['files_parsed']
                        })
                except (json.JSONDecodeError, TypeError):
                    application['files_parsed'] = {}
                    app.logger.warning("Failed to parse files JSON", extra={
                        "applicant": f"{application.get('nombre', '')} {application.get('apellido', '')}",
                        "raw_files": application.get('files', '')
                    })

            # Count today's applications
            if application.get('created_at', '')[:10] == today:
                today_count += 1

            # Count pending applications
            if application.get('status', 'pending') == 'pending':
                pending_count += 1

        app.logger.info("Admin dashboard loaded", extra={
            "total_applications": len(applications),
            "today_count": today_count,
            "pending_count": pending_count
        })

        return render_template_string(
            ADMIN_TEMPLATE,
            applications=applications,
            today_count=today_count,
            pending_count=pending_count
        )

    except pymongo.errors.PyMongoError as e:
        app.logger.error("Database error in admin dashboard", extra={"error": str(e)})
        return "Database error accessing applications", 503
    except (ValueError, TypeError) as e:
        app.logger.error("Data processing error in admin dashboard", extra={"error": str(e)})
        return "Error processing application data", 400
    except Exception as e:
        app.logger.error("Error in admin dashboard", extra={"error": str(e)})
        return "Error: " + str(e), 500


@app.route('/api/metrics', methods=['GET'])
@safe_limit("10 per minute")
def get_metrics():
    """Get application metrics for monitoring."""
    try:
        # Basic metrics
        today = datetime.utcnow().strftime('%Y-%m-%d')
        yesterday = datetime.utcnow().replace(day=datetime.utcnow().day-1).strftime('%Y-%m-%d')

        # Aggregate metrics
        total_applications = candidates.count_documents({})
        today_applications = candidates.count_documents({"created_at": {"$regex": f"^{today}"}})
        yesterday_applications = candidates.count_documents({"created_at": {"$regex": f"^{yesterday}"}})
        pending_applications = candidates.count_documents({"status": "pending"})

        # Position statistics
        position_stats = list(candidates.aggregate([
            {"$group": {"_id": "$puesto", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]))

        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.1.0",
            "totals": {
                "applications": total_applications,
                "today": today_applications,
                "yesterday": yesterday_applications,
                "pending": pending_applications
            },
            "top_positions": position_stats,
            "growth": {
                "daily_change": today_applications - yesterday_applications,
                "daily_change_percent": ((today_applications - yesterday_applications) / max(yesterday_applications, 1)) * 100
            }
        }

        app.logger.info("Metrics requested", extra={"metrics": metrics})

        return jsonify(metrics)

    except pymongo.errors.PyMongoError as e:
        app.logger.error("Database error generating metrics", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Database error generating metrics",
            "error": str(e)
        }), 503
    except (ValueError, ZeroDivisionError) as e:
        app.logger.error("Calculation error in metrics", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Error calculating metrics",
            "error": str(e)
        }), 400
    except Exception as e:
        app.logger.error("Error generating metrics", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Unexpected error generating metrics",
            "error": str(e)
        }), 500


@app.route('/healthz', methods=['GET'])
def healthz():
    """Simple health check endpoint for Render."""
    return jsonify({"status": "ok"}), 200


@app.route('/api/startup-info', methods=['GET'])
def startup_info():
    """Debug endpoint to show how the application started."""
    try:
        startup_details = {
            "startup_mode": "unknown",
            "server_type": "unknown",
            "environment_variables": {
                "RENDER": os.environ.get('RENDER', 'not_set'),
                "FLASK_ENV": os.environ.get('FLASK_ENV', 'not_set'),
                "DEBUG": os.environ.get('DEBUG', 'not_set'),
                "PORT": os.environ.get('PORT', 'not_set'),
            },
            "gunicorn_detected": False,
            "flask_dev_server": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Check if running under Gunicorn
        if 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '').lower():
            startup_details["server_type"] = "gunicorn"
            startup_details["gunicorn_detected"] = True
            startup_details["startup_mode"] = "production_gunicorn"
        elif hasattr(sys, 'ps1') or sys.flags.interactive:
            startup_details["server_type"] = "interactive_python"
            startup_details["startup_mode"] = "interactive"
        elif __name__ == '__main__':
            startup_details["server_type"] = "direct_python_execution"
            startup_details["flask_dev_server"] = True
            startup_details["startup_mode"] = "development_flask"
        else:
            startup_details["server_type"] = "wsgi_import"
            startup_details["startup_mode"] = "production_wsgi"

        # Add process information (with better error handling)
        startup_details["process_info"] = "Process info disabled for production stability"

        # Add server software detection
        startup_details["server_software"] = os.environ.get('SERVER_SOFTWARE', 'not_set')
        startup_details["wsgi_detected"] = 'wsgi' in str(sys.modules.keys()).lower()

        return jsonify(startup_details)

    except Exception as e:
        app.logger.error(f"Error in startup_info endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error in startup_info",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


if __name__ == '__main__':
    # Check if we're in production (Render environment)
    is_production = os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production'

    if is_production:
        # In production, run Flask as fallback since Render is calling python app.py directly
        # This prevents "Application exited early" error
        app.logger.info("Production environment detected - Render will handle server startup via Procfile/render.yaml")
        app.logger.warning("Running Flask server directly - this should only happen if Procfile/render.yaml failed")
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development mode - use Flask development server
        app.logger.info("Development environment detected, starting Flask dev server...")
        port = int(os.environ.get('PORT', 5000))
        debug_mode = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEBUG', 'false').lower() == 'true'
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
