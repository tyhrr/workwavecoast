#!/usr/bin/env python3
"""
WorkWave Coast - Backend Server
Servidor Flask para recibir postulaciones de trabajo en la costa croata
Versión actualizada con MongoDB Atlas y Cloudinary
"""

import os
import csv
import io
from datetime import datetime
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pymongo
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)
CORS(app, origins=["https://tyhrr.github.io", "https://workwavecoast.free.nf", "http://localhost:3000"])

# Configuración de archivos
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Configuración de MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is required")

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Crear directorios necesarios
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Conexión a MongoDB
client = MongoClient(MONGODB_URI)
db = client['job_applications']
candidates_collection = db['candidates']

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_cloudinary(file_path, resource_type="auto"):
    """Subir archivo a Cloudinary y retornar URL"""
    try:
        result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            folder="workwavecoast"
        )
        return result.get('secure_url')
    except Exception as e:
        print(f"❌ Error subiendo a Cloudinary: {e}")
        return None

@app.route('/')
def index():
    """Página principal con información del API"""
    return jsonify({
        'status': 'ok',
        'message': 'WorkWave Coast API funcionando',
        'version': '2.0 - MongoDB + Cloudinary',
        'endpoints': {
            '/api/submit': 'POST - Enviar postulación',
            '/api/export': 'GET - Exportar a CSV',
            '/api/stats': 'GET - Estadísticas'
        }
    })

@app.route('/api/submit', methods=['POST'])
def submit_application():
    """Recibir y procesar postulación"""
    try:
        # Verificar datos del formulario
        required_fields = ['nombre', 'apellido', 'nacionalidad', 'puesto']
        for field in required_fields:
            if field not in request.form or not request.form[field].strip():
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido faltante: {field}'
                }), 400

        # Verificar CV (requerido)
        if 'cv' not in request.files:
            return jsonify({
                'success': False,
                'message': 'CV es requerido'
            }), 400

        cv_file = request.files['cv']
        if cv_file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No se seleccionó archivo de CV'
            }), 400

        if not cv_file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'message': 'El CV debe ser un archivo PDF'
            }), 400

        # Procesar archivos
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
        
        # Guardar CV temporalmente y subirlo a Cloudinary
        cv_filename = f"{timestamp_str}_{secure_filename(cv_file.filename)}"
        cv_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], cv_filename)
        cv_file.save(cv_temp_path)
        
        # Subir CV a Cloudinary
        cv_url = upload_to_cloudinary(cv_temp_path, "raw")
        if not cv_url:
            return jsonify({
                'success': False,
                'message': 'Error subiendo CV al almacenamiento'
            }), 500
        
        # Eliminar archivo temporal
        os.remove(cv_temp_path)

        # Procesar documentos adicionales (opcionales)
        documentos_urls = []
        if 'documentos' in request.files:
            documentos_files = request.files.getlist('documentos')
            
            for doc_file in documentos_files:
                if doc_file.filename and allowed_file(doc_file.filename):
                    doc_filename = f"{timestamp_str}_{secure_filename(doc_file.filename)}"
                    doc_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_filename)
                    doc_file.save(doc_temp_path)
                    
                    # Subir a Cloudinary
                    doc_url = upload_to_cloudinary(doc_temp_path, "raw")
                    if doc_url:
                        documentos_urls.append({
                            'filename': doc_file.filename,
                            'url': doc_url
                        })
                    
                    # Eliminar archivo temporal
                    os.remove(doc_temp_path)

        # Preparar datos para MongoDB
        document = {
            'timestamp': timestamp,
            'nombre': request.form['nombre'].strip(),
            'apellido': request.form['apellido'].strip(),
            'nacionalidad': request.form['nacionalidad'].strip(),
            'puesto': request.form['puesto'].strip(),
            'cv_url': cv_url,
            'cv_filename': cv_file.filename,
            'documentos_adicionales': documentos_urls,
            'ip_address': request.remote_addr,
            'created_at': timestamp.isoformat()
        }

        # Guardar en MongoDB
        result = candidates_collection.insert_one(document)
        
        if result.inserted_id:
            print(f"✅ Nueva postulación guardada: {document['nombre']} {document['apellido']} (ID: {result.inserted_id})")
            
            return jsonify({
                'success': True,
                'message': 'Postulación recibida exitosamente',
                'id': str(result.inserted_id),
                'timestamp': timestamp.isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error guardando en base de datos'
            }), 500

    except Exception as e:
        print(f"❌ Error procesando postulación: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@app.route('/api/export')
def export_csv():
    """Exportar todas las postulaciones a CSV"""
    try:
        # Obtener todos los documentos de MongoDB
        candidates = list(candidates_collection.find().sort('timestamp', -1))
        
        if not candidates:
            return jsonify({
                'success': False,
                'message': 'No hay datos para exportar'
            }), 404
        
        # Crear CSV en memoria
        output = io.StringIO()
        fieldnames = [
            'timestamp',
            'nombre',
            'apellido',
            'nacionalidad',
            'puesto',
            'cv_url',
            'cv_filename',
            'documentos_adicionales',
            'ip_address'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for candidate in candidates:
            # Preparar fila para CSV
            row = {
                'timestamp': candidate.get('timestamp', '').strftime('%d/%m/%Y %H:%M:%S') if candidate.get('timestamp') else '',
                'nombre': candidate.get('nombre', ''),
                'apellido': candidate.get('apellido', ''),
                'nacionalidad': candidate.get('nacionalidad', ''),
                'puesto': candidate.get('puesto', ''),
                'cv_url': candidate.get('cv_url', ''),
                'cv_filename': candidate.get('cv_filename', ''),
                'documentos_adicionales': '; '.join([doc.get('filename', '') for doc in candidate.get('documentos_adicionales', [])]),
                'ip_address': candidate.get('ip_address', '')
            }
            writer.writerow(row)
        
        # Preparar respuesta
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=postulaciones_workwave_coast_{datetime.now().strftime("%Y%m%d")}.csv'
        
        print(f"✅ CSV exportado con {len(candidates)} registros")
        return response
        
    except Exception as e:
        print(f"❌ Error exportando CSV: {e}")
        return jsonify({
            'success': False,
            'message': 'Error generando exportación'
        }), 500

@app.route('/api/stats')
def get_stats():
    """Obtener estadísticas básicas"""
    try:
        total_applications = candidates_collection.count_documents({})
        
        # Estadísticas por nacionalidad
        nationality_stats = list(candidates_collection.aggregate([
            {"$group": {"_id": "$nacionalidad", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        
        # Estadísticas por puesto
        position_stats = list(candidates_collection.aggregate([
            {"$group": {"_id": "$puesto", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        
        # Aplicaciones recientes (últimos 7 días)
        week_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = week_ago.replace(day=week_ago.day - 7)
        recent_applications = candidates_collection.count_documents({
            "timestamp": {"$gte": week_ago}
        })
        
        stats = {
            'total_aplicaciones': total_applications,
            'aplicaciones_ultima_semana': recent_applications,
            'estadisticas_nacionalidad': nationality_stats[:10],  # Top 10
            'estadisticas_puesto': position_stats[:10],  # Top 10
            'conexion_bd': True,
            'cloudinary_configurado': bool(os.getenv('CLOUDINARY_CLOUD_NAME'))
        }
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo estadísticas',
            'conexion_bd': False
        }), 500

@app.route('/health')
def health_check():
    """Health check para Render"""
    try:
        # Verificar conexión a MongoDB
        client.admin.command('ping')
        return jsonify({
            'status': 'healthy',
            'mongodb': 'connected',
            'cloudinary': 'configured' if os.getenv('CLOUDINARY_CLOUD_NAME') else 'not configured'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando WorkWave Coast Server v2.0...")
    print("📋 Configuración:")
    print(f"   - MongoDB: {'✅ Configurado' if MONGODB_URI else '❌ No configurado'}")
    print(f"   - Cloudinary: {'✅ Configurado' if os.getenv('CLOUDINARY_CLOUD_NAME') else '❌ No configurado'}")
    print(f"   - Puerto: 5000")
    print(f"   - Carpeta uploads: {UPLOAD_FOLDER}")
    print(f"   - Tamaño máximo archivo: {MAX_FILE_SIZE / 1024 / 1024}MB")
    
    print("\n🌐 Servidor disponible en:")
    print("   - http://localhost:5000")
    print("   - http://127.0.0.1:5000")
    print("\n📊 Endpoints disponibles:")
    print("   - GET  /           - Info del API")
    print("   - POST /api/submit - Enviar postulación")
    print("   - GET  /api/export - Exportar CSV")
    print("   - GET  /api/stats  - Estadísticas")
    print("   - GET  /health     - Health check")
    print("\n⚡ Para detener el servidor presiona Ctrl+C")
    print("-" * 50)
    
    # Ejecutar servidor
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
