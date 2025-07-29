"""
WorkWave Coast Backend API
=========================

Flask application for managing job applications on the Croatian coast.
Handles file uploads to Cloudinary and stores application data in MongoDB Atlas.

Author: WorkWave Team
Version: 2.0.0 - FULL SYSTEM RESTART
"""

import os
import json
from datetime import datetime

from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
from functools import wraps
import hashlib

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'workwave-admin-secret-2025')

# Admin credentials (you should set these as environment variables)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'workwave2025')

# Configure CORS for your custom domain
CORS(app, origins=[
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://workwavecoast.online",
    "http://www.workwavecoast.online",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5000"
], supports_credentials=True)

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['workwave']  # Database name
candidates = db['candidates']  # Collection name

# Cloudinary configuration (if needed)
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def login_required(f):
    """Decorator to require admin login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# HTML Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WorkWave Coast - Admin Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               height: 100vh; display: flex; justify-content: center; align-items: center; margin: 0; }
        .login-container { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                          max-width: 400px; width: 100%; }
        .logo { text-align: center; margin-bottom: 2rem; color: #333; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
        input { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; }
        .btn { background: #667eea; color: white; padding: 0.75rem 1.5rem; border: none; 
               border-radius: 5px; cursor: pointer; width: 100%; font-size: 1rem; }
        .btn:hover { background: #5a67d8; }
        .error { color: red; margin-top: 1rem; text-align: center; }
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
            <button type="submit" class="btn">Iniciar Sesión</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WorkWave Coast - Panel de Administración</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
        .header { background: #667eea; color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
        .container { padding: 2rem; max-width: 1200px; margin: 0 auto; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
        .applications { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .application { border-bottom: 1px solid #eee; padding: 1.5rem; }
        .application:last-child { border-bottom: none; }
        .app-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .app-name { font-size: 1.2rem; font-weight: bold; color: #333; }
        .app-date { color: #666; font-size: 0.9rem; }
        .app-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
        .detail { padding: 0.5rem; background: #f8f9fa; border-radius: 4px; }
        .detail strong { color: #333; }
        .files { margin-top: 1rem; }
        .file-link { display: inline-block; background: #28a745; color: white; padding: 0.5rem 1rem; 
                    border-radius: 4px; text-decoration: none; margin-right: 0.5rem; margin-bottom: 0.5rem; }
        .file-link:hover { background: #218838; }
        .logout { background: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; }
        .logout:hover { background: #c82333; }
        .status { padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; }
        .status.pending { background: #fff3cd; color: #856404; }
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
                <p style="font-size: 2rem; margin: 0; color: #667eea;">{{ applications|length }}</p>
            </div>
            <div class="stat-card">
                <h3>📅 Hoy</h3>
                <p style="font-size: 2rem; margin: 0; color: #28a745;">
                {% set today_count = applications|selectattr('created_at', 'match', '2025-07-29.*')|list|length %}
                {{ today_count }}
                </p>
            </div>
            <div class="stat-card">
                <h3>⏳ Pendientes</h3>
                <p style="font-size: 2rem; margin: 0; color: #ffc107;">
                {% set pending_count = applications|selectattr('status', 'equalto', 'pending')|list|length %}
                {{ pending_count }}
                </p>
            </div>
        </div>

        <div class="applications">
            {% for app in applications %}
            <div class="application">
                <div class="app-header">
                    <div class="app-name">{{ app.nombre }} {{ app.apellido }}</div>
                    <div class="app-date">{{ app.created_at[:19]|replace('T', ' ') }}</div>
                </div>
                
                <div class="app-details">
                    <div class="detail"><strong>Email:</strong> {{ app.email }}</div>
                    <div class="detail"><strong>Teléfono:</strong> {{ app.telefono }}</div>
                    <div class="detail"><strong>Nacionalidad:</strong> {{ app.nacionalidad }}</div>
                    <div class="detail"><strong>Puesto:</strong> {{ app.puesto }}</div>
                    <div class="detail"><strong>Español:</strong> {{ app.espanol_nivel }}</div>
                    <div class="detail"><strong>Inglés:</strong> {{ app.ingles_nivel }}</div>
                    {% if app.otro_idioma %}
                    <div class="detail"><strong>{{ app.otro_idioma }}:</strong> {{ app.otro_idioma_nivel }}</div>
                    {% endif %}
                    <div class="detail">
                        <strong>Estado:</strong> 
                        <span class="status {{ app.status }}">{{ app.status.title() }}</span>
                    </div>
                </div>
                
                {% if app.files_parsed %}
                <div class="files">
                    <strong>📎 Archivos:</strong><br>
                    {% for file_type, file_info in app.files_parsed.items() %}
                        {% if file_info.url %}
                            <a href="{{ file_info.url }}" target="_blank" class="file-link">
                                📄 {{ file_type.title() }} ({{ (file_info.bytes / 1024)|round(1) }}KB)
                            </a>
                        {% endif %}
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint that returns basic API information.

    Returns:
        dict: JSON response with API status and message
    """
    return jsonify({"message": "WorkWave Coast Backend API", "status": "running"})

@app.route('/api/submit', methods=['OPTIONS'])
@cross_origin(origins=[
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://workwavecoast.online",
    "http://www.workwavecoast.online"
], supports_credentials=True)
def submit_options():
    """Handle preflight OPTIONS request for CORS."""
    return '', 204

@app.route('/api/submit', methods=['POST'])
@cross_origin(origins=[
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://workwavecoast.online",
    "http://www.workwavecoast.online"
], supports_credentials=True)
def submit_application():
    """
    Submit a job application with form data and file uploads.

    Accepts form data and files, uploads files to Cloudinary if configured,
    and stores the application data in MongoDB.

    Returns:
        dict: JSON response with success status and application ID
    """
    try:
        # Get form data
        data = request.form.to_dict()

        # Add timestamp
        data['created_at'] = datetime.utcnow().isoformat()
        data['status'] = 'pending'

        # Validate required fields
        required_fields = ['nombre', 'email', 'telefono']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"Campo requerido faltante: {field}"
                }), 400

        # File size limits (in bytes) and allowed extensions
        file_size_limits = {
            'cv': 1024 * 1024,  # 1MB for CV
            'documentos': 2 * 1024 * 1024  # 2MB for additional documents
        }

        allowed_extensions = {
            'cv': ['.pdf', '.doc', '.docx'],
            'documentos': ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        }

        # Handle file uploads
        files = request.files
        file_urls = {}

        for field_name, file in files.items():
            if file and file.filename:
                file_size = 0  # Initialize file_size

                # Validate file extension
                if field_name in allowed_extensions:
                    file_extension = os.path.splitext(file.filename)[1].lower()
                    if file_extension not in allowed_extensions[field_name]:
                        allowed = ', '.join(allowed_extensions[field_name])
                        return jsonify({
                            "success": False,
                            "message": f"Tipo de archivo no permitido para {field_name}. Permitidos: {allowed}"
                        }), 400

                # Validate file size
                if field_name in file_size_limits:
                    try:
                        file.seek(0, 2)  # Seek to end
                        file_size = file.tell()
                        file.seek(0)  # Reset to beginning
                    except IOError:
                        return jsonify({
                            "success": False,
                            "message": f"Error al procesar el archivo {field_name}"
                        }), 400

                    if file_size > file_size_limits[field_name]:
                        max_size_mb = file_size_limits[field_name] / (1024 * 1024)
                        return jsonify({
                            "success": False,
                            "message": (f"El archivo {field_name} es demasiado grande. "
                                       f"Máximo: {max_size_mb}MB")
                        }), 413

                # Upload to Cloudinary (if configured)
                cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
                api_key = os.getenv('CLOUDINARY_API_KEY')
                api_secret = os.getenv('CLOUDINARY_API_SECRET')

                if cloud_name and api_key and api_secret and cloud_name != 'tu_cloud_name':
                    try:
                        # Upload with specific options for different file types
                        upload_options = {
                            'folder': 'workwave_coast',
                            'resource_type': 'auto',
                            'use_filename': True,
                            'unique_filename': True
                        }

                        # Add PDF-specific options for CVs
                        if (field_name == 'cv' and
                            file.filename.lower().endswith('.pdf')):
                            upload_options['format'] = 'pdf'
                            upload_options['pages'] = True  # Enable page count

                        print(f"Upload options: {upload_options}")
                        upload_result = cloudinary.uploader.upload(
                            file, **upload_options)

                        file_urls[field_name] = {
                            'url': upload_result['secure_url'],
                            'public_id': upload_result['public_id'],
                            'format': upload_result.get('format', ''),
                            'bytes': upload_result.get('bytes', 0),
                            'pages': (upload_result.get('pages', 1)
                                     if 'pages' in upload_result else 1),
                            'status': 'cloudinary_upload_success',
                            'system_version': '2.0.0'
                        }

                    except (ValueError, ConnectionError, RuntimeError) as e:
                        # Fallback: save basic file info instead of failing
                        file_urls[field_name] = {
                            'filename': file.filename,
                            'size_bytes': file_size,
                            'status': 'cloudinary_upload_failed',
                            'error': str(e),
                            'note': 'File received but not uploaded to cloud storage',
                            'system_version': '2.0.0'
                        }
                        print(f"Saved file info as fallback: {file_urls[field_name]}")
                else:
                    # Fallback: save basic file info if Cloudinary not configured
                    file_urls[field_name] = {
                        'filename': file.filename,
                        'size_bytes': file_size,
                        'status': 'cloudinary_not_configured',
                        'note': 'File received but stored locally due to missing Cloudinary config',
                        'system_version': '2.0.0'
                    }

        # Add file URLs to data (convert to JSON string for MongoDB storage)
        data['files'] = json.dumps(file_urls) if file_urls else "{}"

        # Insert into MongoDB
        result = candidates.insert_one(data)

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "application_id": str(result.inserted_id)
        }), 201

    except (ValueError, KeyError, TypeError, ConnectionError, OSError,
            RuntimeError) as e:
        print(f"Error submitting application: {e}")
        return jsonify({
            "success": False,
            "message": "Error submitting application",
            "error": str(e)
        }), 500

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """
    Retrieve all job applications from the database.

    Returns:
        dict: JSON response with list of applications and count
    """
    try:
        # Get all applications
        applications = list(candidates.find({}, {"_id": 0}))

        return jsonify({
            "success": True,
            "applications": applications,
            "count": len(applications)
        })

    except (ConnectionError, TimeoutError) as e:
        print(f"Database connection error: {e}")
        return jsonify({
            "success": False,
            "message": "Database connection error",
            "error": str(e)
        }), 503
    except (ValueError, TypeError, OSError) as e:
        print(f"Unexpected error fetching applications: {e}")
        return jsonify({
            "success": False,
            "message": "Error fetching applications",
            "error": str(e)
        }), 500

@app.route('/api/applications/latest', methods=['GET'])
def get_latest_application():
    """
    Retrieve the most recent job application from the database.

    Returns:
        dict: JSON response with the latest application details
    """
    try:
        # Get the most recent application
        latest_app = candidates.find().sort('created_at', -1).limit(1)
        applications = list(latest_app)

        if applications:
            application = applications[0]
            # Convert ObjectId to string for JSON serialization
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

    except (ConnectionError, TimeoutError, ValueError, TypeError, OSError,
            RuntimeError) as e:
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

        if not cloud_name or not api_key or not api_secret:
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
            "system_version": "2.0.0",
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
            "system_version": "2.0.0",
            "restart_status": "❌ Error during status check",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify database connectivity.

    Tests the MongoDB connection and returns the health status.

    Returns:
        dict: JSON response with health status and timestamp
    """
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

    except (ConnectionError, TimeoutError) as e:
        return jsonify({
            "status": "unhealthy",
            "mongodb": "disconnected",
            "cloudinary": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503
    except (ValueError, TypeError, OSError, RuntimeError) as e:
        return jsonify({
            "status": "unhealthy",
            "mongodb": "unknown_error",
            "cloudinary": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
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
        # Get all applications with proper sorting
        applications = list(candidates.find({}).sort('created_at', -1))
        
        # Convert ObjectId to string and parse files JSON
        for app in applications:
            app['_id'] = str(app['_id'])
            if 'files' in app:
                try:
                    app['files_parsed'] = json.loads(app['files'])
                except:
                    app['files_parsed'] = {}
        
        return render_template_string(ADMIN_TEMPLATE, applications=applications)
    
    except Exception as e:
        return f"Error loading applications: {str(e)}", 500

@app.route('/healthz', methods=['GET'])
def healthz():
    """
    Simple health check endpoint for Render.
    Returns a simple 200 OK response to indicate the service is running.
    """
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
