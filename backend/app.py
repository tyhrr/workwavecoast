"""
WorkWave Coast Backend API
=========================

Flask application for managing job applications on the Croatian coast.
Handles file uploads to Cloudinary and stores application data in MongoDB Atlas.

Author: WorkWave Team
Version: 2.1.0 - PERFORMANCE & MONITORING UPGRADE
"""

import os
import json
import re
import logging
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient
from dotenv import load_dotenv
from pythonjsonlogger.json import JsonFormatter
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure structured logging
def setup_logging():
    """Configure structured JSON logging."""
    if not app.debug:  # Only in production
        handler = logging.StreamHandler()
        formatter = JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Structured logging configured")

# Initialize logging
setup_logging()

# Configure Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
)

# Security: Force environment variables for production security
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required for security")
app.secret_key = SECRET_KEY

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
    "http://localhost:5000"
]

# Configure CORS
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

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

        # Index for email uniqueness and quick lookups
        candidates.create_index([("email", 1)], unique=False)  # Allow duplicates for now

        # Compound index for filtering by position and date
        candidates.create_index([("puesto", 1), ("created_at", -1)])

        # Index for status filtering
        candidates.create_index([("status", 1)])

        # Text index for searching names
        candidates.create_index([
            ("nombre", "text"),
            ("apellido", "text"),
            ("email", "text")
        ])

        app.logger.info("MongoDB indexes created successfully")

    except Exception as e:
        app.logger.warning(f"Error creating indexes: {e}")

# Initialize indexes
create_indexes()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
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

REQUIRED_FIELDS = ['nombre', 'email', 'telefono']

# Input validation patterns
VALIDATION_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'telefono': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
    'nombre': r'^[a-zA-ZÀ-ÿ\s]{1,50}$',
    'apellido': r'^[a-zA-ZÀ-ÿ\s]{1,50}$'
}


def validate_application_data(data):
    """Validate application form data for security and format."""
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if not data.get(field) or not data.get(field).strip():
            errors.append(f"Campo requerido faltante o vacío: {field}")

    # Validate field formats
    for field, pattern in VALIDATION_PATTERNS.items():
        if field in data and data[field]:
            if not re.match(pattern, data[field].strip()):
                errors.append(f"Formato inválido para {field}")

    # Validate field lengths to prevent DoS
    max_lengths = {
        'nombre': 50, 'apellido': 50, 'email': 100, 'telefono': 20,
        'nacionalidad': 50, 'puesto': 50, 'experiencia': 500,
        'motivacion': 1000, 'disponibilidad': 200
    }

    for field, max_length in max_lengths.items():
        if field in data and data[field] and len(data[field]) > max_length:
            errors.append(f"Campo {field} excede la longitud máxima de {max_length} caracteres")

    return len(errors) == 0, errors


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
            return False, f"Tipo de archivo no permitido para {field_name}. Permitidos: {allowed}", 0

    # Validate file size
    try:
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
    except IOError:
        return False, f"Error al procesar el archivo {field_name}", 0

    if field_name in FILE_SIZE_LIMITS and file_size > FILE_SIZE_LIMITS[field_name]:
        max_size_mb = FILE_SIZE_LIMITS[field_name] / (1024 * 1024)
        return False, f"El archivo {field_name} es demasiado grande. Máximo: {max_size_mb}MB", file_size

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
        # Configure upload options with public access
        upload_options = {
            'folder': 'workwave_coast',
            'resource_type': 'auto',
            'use_filename': True,
            'unique_filename': True,
            'type': 'upload',  # Ensure it's uploaded as public
            'access_mode': 'public'  # Make sure it's publicly accessible
        }

        # Add PDF-specific options for CVs
        if field_name == 'cv' and file.filename.lower().endswith('.pdf'):
            upload_options['format'] = 'pdf'
            upload_options['pages'] = True

        upload_result = cloudinary.uploader.upload(file, **upload_options)

        # Generate a public URL that doesn't require authentication
        public_url = upload_result['secure_url']
        
        # Log the upload for debugging
        app.logger.info("File uploaded to Cloudinary", extra={
            "field_name": field_name,
            "filename": file.filename,
            "public_id": upload_result['public_id'],
            "url": public_url,
            "bytes": upload_result.get('bytes', 0)
        })

        return {
            'url': public_url,
            'public_id': upload_result['public_id'],
            'format': upload_result.get('format', ''),
            'bytes': upload_result.get('bytes', 0),
            'pages': upload_result.get('pages', 1) if 'pages' in upload_result else 1,
            'filename': file.filename,
            'status': 'cloudinary_upload_success',
            'system_version': '2.0.2'
        }

    except Exception as e:
        app.logger.error("Cloudinary upload failed", extra={
            "field_name": field_name,
            "filename": file.filename,
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
            grid-template-columns: 2fr 1fr 1fr auto;
            gap: 1rem;
            align-items: center;
        }
        .application-item:last-child { border-bottom: none; }
        .application-item:hover { background: #F7FAFC; }
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
                    <label for="searchFilter">🔍 Buscar por nombre o apellido:</label>
                    <input type="text" id="searchFilter" placeholder="Ej: Juan, María, García..." onkeyup="filterApplications()">
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

        <div class="results-count" id="resultsCount">
            Mostrando {{ applications|length }} aplicaciones
        </div>

        <div class="applications-list">
            {% for app in applications %}
            <div class="application-item"
                 data-name="{{ (app.get('nombre', '') + ' ' + app.get('apellido', '')).lower() }}"
                 data-job="{{ app.get('puesto', '') }}"
                 data-english="{{ app.get('ingles_nivel', '') }}">

                <div class="applicant-info">
                    <div class="applicant-name">{{ app.get('nombre', '')|e }} {{ app.get('apellido', '')|e }}</div>
                    <div class="applicant-details">
                        📧 {{ app.get('email', '')|e }} | 📞 {{ app.get('telefono', '')|e }} | 🌍 {{ app.get('nacionalidad', '')|e }}
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
                                <a href="{{ file_info.get('url') }}" target="_blank" class="file-link" 
                                   title="Ver {{ file_type }} - {{ file_info.get('filename', 'archivo') }}"
                                   onerror="this.href='/api/file/{{ file_info.get('public_id', file_info.get('url').split('/')[-1].split('.')[0] if file_info.get('url') else '') }}'">
                                    {% if file_type == 'cv' %}📄{% else %}📎{% endif %} {{ file_type.title() }}
                                </a>
                            {% elif file_info.get('filename') %}
                                <span class="file-link file-error" title="Archivo: {{ file_info.get('filename') }} - {{ file_info.get('note', 'Error al cargar') }}">
                                    {% if file_type == 'cv' %}📄{% else %}📎{% endif %} {{ file_type.title() }} ⚠️
                                </span>
                            {% endif %}
                        {% endfor %}
                        <button class="expand-btn" onclick="toggleFileDetails(this)" title="Ver detalles de archivos">
                            📋
                        </button>
                    {% else %}
                        <span class="no-files">Sin archivos</span>
                    {% endif %}
                </div>

                <!-- Detailed file info (expandable) -->
                <div class="file-details" style="display: none;">
                    {% if app.get('files_parsed') %}
                        {% for file_type, file_info in app.get('files_parsed', {}).items() %}
                            <div class="file-detail-item">
                                <strong>{{ file_type.title() }}:</strong>
                                {% if file_info.get('url') %}
                                    <a href="{{ file_info.get('url') }}" target="_blank" 
                                       onclick="if(event.ctrlKey || event.metaKey) return true; 
                                                var fallback='/api/file/{{ file_info.get('public_id', file_info.get('url').split('/')[-1].split('.')[0] if file_info.get('url') else '') }}';
                                                var link=this; 
                                                var img=new Image(); 
                                                img.onload=function(){window.open(link.href, '_blank');}; 
                                                img.onerror=function(){window.open(fallback, '_blank');}; 
                                                img.src=link.href; 
                                                return false;">
                                        {{ file_info.get('filename', 'Ver archivo') }}
                                    </a>
                                    <small>({{ (file_info.get('bytes', 0) / 1024) | round(1) }} KB)</small>
                                    {% if file_info.get('public_id') %}
                                        <br><small>ID: {{ file_info.get('public_id') }}</small>
                                    {% endif %}
                                {% else %}
                                    <span>{{ file_info.get('filename', 'N/A') }}</span>
                                    <small>({{ file_info.get('status', 'Error') }})</small>
                                {% endif %}
                            </div>
                        {% endfor %}
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>

        <div id="noResults" class="no-results" style="display: none;">
            No se encontraron aplicaciones que coincidan con los filtros seleccionados.
        </div>
    </div>

    <script>
        function filterApplications() {
            const searchTerm = document.getElementById('searchFilter').value.toLowerCase();
            const jobFilter = document.getElementById('jobFilter').value;
            const englishFilter = document.getElementById('englishFilter').value;

            const applications = document.querySelectorAll('.application-item');
            let visibleCount = 0;

            applications.forEach(app => {
                const name = app.getAttribute('data-name');
                const job = app.getAttribute('data-job');
                const english = app.getAttribute('data-english');

                const matchesSearch = name.includes(searchTerm);
                const matchesJob = jobFilter === '' || job === jobFilter;
                const matchesEnglish = englishFilter === '' || english === englishFilter;

                if (matchesSearch && matchesJob && matchesEnglish) {
                    app.style.display = 'grid';
                    visibleCount++;
                } else {
                    app.style.display = 'none';
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
        }

        function clearFilters() {
            document.getElementById('searchFilter').value = '';
            document.getElementById('jobFilter').value = '';
            document.getElementById('englishFilter').value = '';
            filterApplications();
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
                button.title = 'Ver detalles de archivos';
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

        // Add error handling to all file links
        document.addEventListener('DOMContentLoaded', function() {
            filterApplications();
            
            // Add error handling to file links
            const fileLinks = document.querySelectorAll('.file-link[href*="cloudinary.com"]');
            fileLinks.forEach(link => {
                link.addEventListener('error', function() {
                    console.warn('File link error, trying fallback:', this.href);
                    const publicId = this.getAttribute('data-public-id');
                    if (publicId) {
                        this.href = '/api/file/' + publicId;
                        this.style.backgroundColor = '#fff3cd';
                        this.title = 'Usando enlace de respaldo - ' + this.title;
                    }
                });
            });
        });
    </script>
</body>
</html>'''


# Route handlers
@app.route('/', methods=['GET'])
def home():
    """Home endpoint that returns basic API information."""
    return jsonify({
        "message": "WorkWave Coast Backend API",
        "status": "running",
        "version": "2.1.0"
    })


@app.route('/api/submit', methods=['OPTIONS'])
@cross_origin(origins=ALLOWED_ORIGINS, supports_credentials=True)
def submit_options():
    """Handle preflight OPTIONS request for CORS."""
    return '', 204


@app.route('/api/submit', methods=['POST'])
@cross_origin(origins=ALLOWED_ORIGINS, supports_credentials=True)
@limiter.limit("5 per minute", error_message="Demasiadas solicitudes. Inténtalo en unos minutos.")
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

        # Validate input data
        is_valid, validation_errors = validate_application_data(data)
        if not is_valid:
            app.logger.warning("Invalid application data submitted", extra={
                "errors": validation_errors,
                "remote_addr": get_remote_address()
            })
            return jsonify({
                "success": False,
                "message": "Datos de formulario inválidos",
                "errors": validation_errors
            }), 400

        # Add timestamp and status
        data['created_at'] = datetime.utcnow().isoformat()
        data['status'] = 'pending'

        # Sanitize data (strip whitespace)
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()

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
                        "filename": file.filename,
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
            "files_count": len(file_urls)
        })

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "application_id": str(result.inserted_id)
        }), 201

    except Exception as e:
        app.logger.error("Error submitting application", extra={
            "error": str(e),
            "remote_addr": get_remote_address()
        })
        return jsonify({
            "success": False,
            "message": "Error submitting application",
            "error": str(e)
        }), 500


@app.route('/api/applications', methods=['GET'])
@limiter.limit("30 per minute")
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

    except Exception as e:
        app.logger.error("Error fetching applications", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Error fetching applications",
            "error": str(e)
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
        print(f"Error fetching latest application: {e}")
        return jsonify({
            "success": False,
            "message": "Error fetching latest application",
            "error": str(e)
        }), 500


@app.route('/api/test-cloudinary', methods=['GET'])
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
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        
    except Exception as e:
        app.logger.error("Error serving file", extra={
            "file_id": file_id,
            "error": str(e)
        })
        return f"Error serving file: {str(e)}", 500


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
        except Exception as e:
            mongo_status = f"❌ Error: {str(e)}"

        # Test Cloudinary
        cloudinary_status = "❌ Not configured"
        if all(cloudinary_vars.values()):
            try:
                cloudinary.api.ping()
                cloudinary_status = "✅ Connected and working"
            except Exception as e:
                cloudinary_status = f"❌ Error: {str(e)}"

        # Count applications
        try:
            app_count = candidates.count_documents({})
        except Exception:
            app_count = "Error counting"

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

    except Exception as e:
        return jsonify({
            "system_version": "2.0.2",
            "restart_status": "❌ Error during status check",
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
@limiter.limit("10 per minute", error_message="Demasiados intentos de login. Espera unos minutos.")
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

    except Exception as e:
        app.logger.error("Error in admin dashboard", extra={"error": str(e)})
        return f"Error: {str(e)}", 500


@app.route('/api/metrics', methods=['GET'])
@limiter.limit("10 per minute")
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

    except Exception as e:
        app.logger.error("Error generating metrics", extra={"error": str(e)})
        return jsonify({
            "success": False,
            "message": "Error generating metrics",
            "error": str(e)
        }), 500


@app.route('/healthz', methods=['GET'])
def healthz():
    """Simple health check endpoint for Render."""
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
