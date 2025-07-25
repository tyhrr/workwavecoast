#!/usr/bin/env python3
"""
WorkWave Coast - Backend Server
Servidor Flask para recibir postulaciones de trabajo en la costa croata
"""

import os
import csv
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
from pathlib import Path

# Configuración de la aplicación
app = Flask(__name__)
CORS(app)  # Permitir CORS para desarrollo local

# Configuración de archivos
UPLOAD_FOLDER = 'uploads'
CSV_FILE = 'data.csv'
EXCEL_FILE = 'export.xlsx'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear directorios necesarios
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_csv():
    """Inicializar archivo CSV con headers si no existe"""
    if not os.path.exists(CSV_FILE):
        headers = [
            'timestamp',
            'nombre',
            'apellido', 
            'nacionalidad',
            'puesto',
            'cv_filename',
            'documentos_adicionales',
            'ip_address'
        ]
        
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
        
        print(f"✅ Archivo CSV inicializado: {CSV_FILE}")

def save_to_csv(data):
    """Guardar datos en archivo CSV"""
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                data['timestamp'],
                data['nombre'],
                data['apellido'],
                data['nacionalidad'],
                data['puesto'],
                data['cv_filename'],
                ';'.join(data['documentos_adicionales']) if data['documentos_adicionales'] else '',
                data['ip_address']
            ])
        return True
    except Exception as e:
        print(f"❌ Error guardando en CSV: {e}")
        return False

def generate_excel():
    """Generar archivo Excel desde CSV"""
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE, encoding='utf-8')
            
            # Formatear columnas
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%d/%m/%Y %H:%M:%S')
            
            # Guardar como Excel
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Postulaciones', index=False)
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Postulaciones']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"✅ Archivo Excel generado: {EXCEL_FILE}")
            return True
        else:
            print("❌ No existe archivo CSV para generar Excel")
            return False
            
    except Exception as e:
        print(f"❌ Error generando Excel: {e}")
        return False

@app.route('/')
def index():
    """Página principal con información del API"""
    return jsonify({
        'status': 'ok',
        'message': 'WorkWave Coast API funcionando',
        'endpoints': {
            '/submit': 'POST - Enviar postulación',
            '/download': 'GET - Descargar Excel',
            '/stats': 'GET - Estadísticas'
        }
    })

@app.route('/submit', methods=['POST'])
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
        
        # Guardar CV
        cv_filename = f"{timestamp_str}_{secure_filename(cv_file.filename)}"
        cv_path = os.path.join(app.config['UPLOAD_FOLDER'], cv_filename)
        cv_file.save(cv_path)

        # Procesar documentos adicionales (opcionales)
        documentos_adicionales = []
        if 'documentos' in request.files:
            documentos_files = request.files.getlist('documentos')
            
            for doc_file in documentos_files:
                if doc_file.filename and allowed_file(doc_file.filename):
                    doc_filename = f"{timestamp_str}_{secure_filename(doc_file.filename)}"
                    doc_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_filename)
                    doc_file.save(doc_path)
                    documentos_adicionales.append(doc_filename)

        # Preparar datos para guardar
        data = {
            'timestamp': timestamp.isoformat(),
            'nombre': request.form['nombre'].strip(),
            'apellido': request.form['apellido'].strip(),
            'nacionalidad': request.form['nacionalidad'].strip(),
            'puesto': request.form['puesto'].strip(),
            'cv_filename': cv_filename,
            'documentos_adicionales': documentos_adicionales,
            'ip_address': request.remote_addr
        }

        # Guardar en CSV
        if save_to_csv(data):
            # Generar Excel actualizado
            generate_excel()
            
            print(f"✅ Nueva postulación recibida: {data['nombre']} {data['apellido']}")
            
            return jsonify({
                'success': True,
                'message': 'Postulación recibida exitosamente',
                'timestamp': timestamp.isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error guardando datos'
            }), 500

    except Exception as e:
        print(f"❌ Error procesando postulación: {e}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500

@app.route('/download')
def download_excel():
    """Descargar archivo Excel con todas las postulaciones"""
    try:
        if not os.path.exists(EXCEL_FILE):
            generate_excel()
        
        if os.path.exists(EXCEL_FILE):
            return send_file(
                EXCEL_FILE,
                as_attachment=True,
                download_name=f'postulaciones_workwave_coast_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'success': False,
                'message': 'No hay datos para descargar'
            }), 404
            
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        return jsonify({
            'success': False,
            'message': 'Error generando archivo de descarga'
        }), 500

@app.route('/stats')
def get_stats():
    """Obtener estadísticas básicas"""
    try:
        stats = {
            'total_postulaciones': 0,
            'archivo_csv_existe': os.path.exists(CSV_FILE),
            'archivo_excel_existe': os.path.exists(EXCEL_FILE),
            'carpeta_uploads_existe': os.path.exists(UPLOAD_FOLDER)
        }
        
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                stats['total_postulaciones'] = sum(1 for row in reader) - 1  # -1 para header
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo estadísticas'
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando WorkWave Coast Server...")
    print("📋 Configuración:")
    print(f"   - Puerto: 5000")
    print(f"   - Carpeta uploads: {UPLOAD_FOLDER}")
    print(f"   - Archivo CSV: {CSV_FILE}")
    print(f"   - Archivo Excel: {EXCEL_FILE}")
    print(f"   - Tamaño máximo archivo: {MAX_FILE_SIZE / 1024 / 1024}MB")
    
    # Inicializar CSV
    initialize_csv()
    
    print("\n🌐 Servidor disponible en:")
    print("   - http://localhost:5000")
    print("   - http://127.0.0.1:5000")
    print("\n📊 Endpoints disponibles:")
    print("   - GET  /        - Info del API")
    print("   - POST /submit  - Enviar postulación")
    print("   - GET  /download - Descargar Excel")
    print("   - GET  /stats   - Estadísticas")
    print("\n⚡ Para detener el servidor presiona Ctrl+C")
    print("-" * 50)
    
    # Ejecutar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)
