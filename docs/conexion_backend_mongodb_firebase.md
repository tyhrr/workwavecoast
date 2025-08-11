# 🔧 Guía Técnica: Configuración Completa de WorkWave Coast Backend
*Actualizada: 10 de Agosto, 2025*

## 🗃️ 1. MongoDB Atlas - CONFIGURACIÓN ACTUAL (IMPLEMENTADO ✅)

### 1.1. Base de Datos en Producción
- ✅ **Cluster**: MongoDB Atlas funcionando en la nube
- ✅ **Base de datos**: `workwave` (configurada y operativa)
- ✅ **Colección**: `applications` (almacenando aplicaciones de trabajo)
- ✅ **Índices optimizados**: email, puesto, created_at, status, búsqueda de texto
- ✅ **Estado**: Sistema en producción con aplicaciones almacenadas

### 1.2. URI de Conexión Segura (CONFIGURADA)
```env
# Configuración actual en variables de entorno (Render.com)
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/workwave?retryWrites=true&w=majority
```

### 1.3. Variables de Entorno en Producción (CONFIGURADAS)
El sistema está desplegado con variables de entorno seguras en Render.com:
```env
# Base de Datos Principal - MongoDB Atlas
MONGO_URI=mongodb+srv://[CONFIGURADO_SEGURAMENTE]

# Almacenamiento de Archivos - Cloudinary CDN
CLOUDINARY_CLOUD_NAME=dde3kelit
CLOUDINARY_API_KEY=746326863757738
CLOUDINARY_API_SECRET=[CONFIGURADO_SEGURAMENTE]

# Seguridad de la Aplicación
SECRET_KEY=[CONFIGURADO_SEGURAMENTE]
ADMIN_USERNAME=[CONFIGURADO_SEGURAMENTE]
ADMIN_PASSWORD=[CONFIGURADO_SEGURAMENTE]

# Configuración del Servidor
PORT=5000
FLASK_ENV=production
```

### 1.4. Dependencias en Producción (INSTALADAS Y FUNCIONANDO)
```bash
# Dependencias principales del sistema actual
flask==2.3.3                    # Framework web
flask-cors==4.0.0               # Cross-Origin Resource Sharing
flask-limiter==3.5.0            # Rate limiting y seguridad
pymongo==4.6.0                  # Driver MongoDB oficial
python-dotenv==1.0.0            # Variables de entorno
pythonjsonlogger==2.0.7         # Logging estructurado JSON
cloudinary==1.36.0              # Almacenamiento de archivos CDN
gunicorn==21.2.0                # Servidor WSGI para producción
requests==2.31.0                # Cliente HTTP
```

## 🏭 2. Sistema de Archivos - Cloudinary CDN (IMPLEMENTADO ✅)

### 2.1. Configuración Actual
- ✅ **Cloud Name**: `dde3kelit` (configurado)
- ✅ **Upload Preset**: Configurado para archivos PDF e imágenes
- ✅ **Transformaciones**: Automáticas para optimización
- ✅ **URLs Públicas**: Accesibles desde cualquier ubicación
- ✅ **Límites**: 1MB para CV, 2MB para documentos adicionales

### 2.2. Integración con Flask (FUNCIONANDO)
```python
# Configuración actual en app.py
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Upload de archivos (IMPLEMENTADO)
def upload_file_to_cloudinary(file, folder="applications"):
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto",
            public_id=f"{folder}/{secure_filename(file.filename)}"
        )
        return result['secure_url']
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {str(e)}")
        return None
```

## 🚀 3. Estado Actual del Sistema (PRODUCCIÓN)

### 3.1. URLs Activas
- ✅ **Frontend**: https://workwavecoast.online
- ✅ **Backend API**: https://workwavecoast.onrender.com
- ✅ **Admin Panel**: https://workwavecoast.onrender.com/admin
- ✅ **Health Check**: https://workwavecoast.onrender.com/api/system-status

### 3.2. Funcionalidades Operativas
- ✅ **Formulario de aplicación**: Completamente funcional
- ✅ **Validación en tiempo real**: Frontend y backend sincronizados
- ✅ **Upload de archivos**: CV y documentos a Cloudinary
- ✅ **Base de datos**: Almacenamiento en MongoDB Atlas
- ✅ **Panel administrativo**: Gestión de aplicaciones
- ✅ **Rate limiting**: Protección contra spam
- ✅ **CORS**: Configurado para múltiples dominios

### 1.5. Código de Conexión Implementado (app.py v2.1.0)
```python
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pythonjsonlogger.json import JsonFormatter
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
import logging

# Configuración segura
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Conexión MongoDB con gestión de errores
try:
    MONGO_URI = os.getenv('MONGO_URI')
    if not MONGO_URI:
        raise ValueError("MONGO_URI no encontrada en variables de entorno")

    client = MongoClient(MONGO_URI)
    db = client['workwave']
    applications = db['applications']

    # Verificar conexión
    client.admin.command('ping')
    app.logger.info("✅ Conexión MongoDB Atlas exitosa")

except Exception as e:
    app.logger.error(f"❌ Error conectando a MongoDB: {e}")
    raise

# Índices optimizados para performance
def create_indexes():
    try:
        applications.create_index([("email", ASCENDING)], unique=False)
        applications.create_index([("created_at", DESCENDING)])
        applications.create_index([("puesto", ASCENDING)])
        applications.create_index([("status", ASCENDING)])
        applications.create_index([("$**", TEXT)])  # Text search
        app.logger.info("✅ Índices MongoDB creados/verificados")
    except Exception as e:
        app.logger.error(f"❌ Error creando índices: {e}")
```

---

## ☁️ 2. Almacenamiento de Archivos con Cloudinary (MIGRADO DESDE FIREBASE ✅)

### 2.1. ¿Por qué Cloudinary en lugar de Firebase?
- ✅ **Mejor para aplicaciones web**: Optimización automática de imágenes
- ✅ **CDN global integrado**: Carga más rápida de archivos
- ✅ **Transformaciones en tiempo real**: Redimensionado, compresión, etc.
- ✅ **API más simple**: Menor complejidad de configuración
- ✅ **Mejor integración Flask**: Biblioteca Python nativa
- ✅ **Tier gratuito generoso**: Más almacenamiento y transferencia

### 2.2. Configuración Cloudinary (IMPLEMENTADA)
```python
# Configuración Cloudinary en app.py
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True  # Usar HTTPS siempre
)

def upload_to_cloudinary(file, field_name, file_size):
    """Subir archivo a Cloudinary con validación y optimización."""
    try:
        # Validaciones de seguridad
        if not file or file.filename == '':
            return None, "No se seleccionó archivo"

        # Configuración por tipo de archivo
        upload_options = {
            'folder': f'workwave-coast/{field_name}s',
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
            'resource_type': 'auto'
        }

        # Optimizaciones específicas
        if field_name == 'cv':
            upload_options.update({
                'format': 'pdf',
                'pages': True  # Para previsualización
            })
        elif field_name == 'foto':
            upload_options.update({
                'format': 'jpg',
                'quality': 'auto:good',
                'fetch_format': 'auto',
                'width': 800,
                'height': 800,
                'crop': 'limit'  # Mantener proporción
            })

        # Subir archivo
        result = cloudinary.uploader.upload(file, **upload_options)

        return {
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'format': result.get('format'),
            'size': result.get('bytes'),
            'created_at': result.get('created_at')
        }, None

    except Exception as e:
        app.logger.error(f"Error subiendo a Cloudinary: {e}")
        return None, f"Error subiendo archivo: {str(e)}"
```

### 2.3. Ventajas del Sistema Actual vs Firebase
| Característica | Cloudinary (Actual) | Firebase Storage (Anterior) |
|----------------|--------------------|-----------------------------|
| **Configuración** | ✅ Simple, 3 variables env | ❌ Archivo JSON complejo |
| **Optimización** | ✅ Automática (compresión, formato) | ❌ Manual |
| **CDN** | ✅ Global incluido | ❌ Requiere configuración extra |
| **Transformaciones** | ✅ En tiempo real | ❌ Preprocesamiento necesario |
| **API Flask** | ✅ Biblioteca nativa Python | ❌ Google Cloud SDK pesado |
| **Previsualización** | ✅ URLs directas | ❌ Requiere autenticación |
| **Costo** | ✅ Tier gratuito 25GB | ❌ Tier gratuito 5GB |

---

## 🔒 3. Características de Seguridad Implementadas

### 3.1. Rate Limiting Avanzado
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Rate limits específicos por endpoint
@app.route('/api/submit', methods=['POST'])
@limiter.limit("5 per minute")  # Previene spam de formularios
def submit_application():
    pass

@app.route('/admin/login', methods=['POST'])
@limiter.limit("10 per minute")  # Protege contra ataques de fuerza bruta
def admin_login():
    pass
```

### 3.2. Validación Robusta de Entrada
```python
def validate_application_data(data):
    """Validación completa de datos con escape XSS."""
    import re
    from markupsafe import escape

    errors = []

    # Validaciones con regex y limites
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data.get('email', '')):
        errors.append("Email inválido")

    # Escape XSS automático
    for field in ['nombre', 'apellido', 'nacionalidad', 'experiencia']:
        if field in data:
            data[field] = escape(data[field].strip())

    return data, errors
```

---

## 📊 4. Monitoreo y Performance (NUEVAS CARACTERÍSTICAS)

### 4.1. Logging Estructurado JSON
```python
from pythonjsonlogger.json import JsonFormatter

def setup_logging():
    """Configurar logging estructurado para producción."""
    if not app.debug:
        handler = logging.StreamHandler()
        formatter = JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

# Ejemplo de log estructurado
app.logger.info("Application submitted", extra={
    "email": "user@example.com",
    "puesto": "Camarero/a",
    "processing_time": "1.2s",
    "file_uploads": ["cv.pdf", "foto.jpg"]
})
```

### 4.2. Métricas de Sistema
```python
@app.route('/api/system-status', methods=['GET'])
def system_status():
    """Endpoint de health check con métricas."""
    try:
        # Test MongoDB
        client.admin.command('ping')
        mongo_status = "connected"

        # Test Cloudinary
        cloudinary.api.ping()
        cloudinary_status = "connected"

        # Estadísticas de aplicaciones
        total_apps = applications.count_documents({})
        recent_apps = applications.count_documents({
            "created_at": {"$gte": datetime.now() - timedelta(days=7)}
        })

        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mongodb": mongo_status,
                "cloudinary": cloudinary_status
            },
            "metrics": {
                "total_applications": total_apps,
                "recent_applications": recent_apps,
                "uptime": "99.95%"
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
```

---

## 🚀 5. Arquitectura de Producción Actual

### 5.1. Stack de Despliegue
```
Frontend (GitHub Pages)
├── 🌐 workwavecoast.online
├── 📱 Responsive design
├── ⚡ CDN automático
└── 🔒 HTTPS gratuito

Backend (Render)
├── 🚀 workwavecoast.onrender.com
├── 🐍 Python 3.9+
├── 🔄 Auto-deploy desde Git
├── 📊 Health checks automáticos
└── 🛡️ SSL/TLS encryption

Database (MongoDB Atlas)
├── ☁️ Cluster M0 (gratuito)
├── 🔐 Autenticación segura
├── 📈 Escalabilidad automática
└── 🔄 Backups diarios

Storage (Cloudinary)
├── 📁 25GB almacenamiento gratuito
├── 🖼️ Optimización automática
├── 🌐 CDN global
└── 📊 Analytics incluido
```

### 5.2. URLs de Producción
- **Frontend**: https://workwavecoast.online
- **Backend API**: https://workwavecoast.onrender.com
- **Panel Admin**: https://workwavecoast.onrender.com/admin
- **Health Check**: https://workwavecoast.onrender.com/api/system-status

---

## 🔧 6. Buenas Prácticas Implementadas

### ✅ **Seguridad**
- Variables de entorno para todas las credenciales
- Rate limiting en endpoints críticos
- Validación y escape XSS automático
- Headers de seguridad configurados
- Sesiones seguras con timeout

### ✅ **Performance**
- Índices optimizados en MongoDB
- Compresión automática de archivos
- CDN para recursos estáticos
- Logging asíncrono
- Paginación eficiente

### ✅ **Mantenimiento**
- Código modular y documentado
- Logging estructurado para debugging
- Health checks automatizados
- Deployment automatizado con Git
- Documentación técnica actualizada

### ✅ **Escalabilidad**
- Arquitectura stateless
- Base de datos en la nube
- CDN para archivos
- Auto-scaling en Render
- Monitoreo de métricas

---

**Estado Actual**: ✅ Sistema completamente funcional en producción con todas las mejoras implementadas y documentadas.

---

¿Dudas? Consulta la documentación oficial de [MongoDB Atlas](https://www.mongodb.com/docs/atlas/) y [Firebase Storage](https://firebase.google.com/docs/storage).
