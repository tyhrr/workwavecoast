# 🔧 MEJORES PRÁCTICAS PARA WORKWAVE COAST

## 📊 MANEJO DE ERRORES ESPECÍFICOS

### ❌ INCORRECTO:
```python
try:
    result = some_operation()
except Exception as e:
    pass
```

### ✅ CORRECTO:
```python
try:
    result = some_operation()
except (ConnectionError, TimeoutError) as e:
    app.logger.error("Connection failed: %s", str(e))
    return {"error": "Service temporarily unavailable"}, 503
except ValueError as e:
    app.logger.warning("Invalid input: %s", str(e))
    return {"error": "Invalid data provided"}, 400
except Exception as e:
    app.logger.error("Unexpected error: %s", str(e))
    return {"error": "Internal server error"}, 500
```

## 🔒 SEGURIDAD DE ARCHIVOS

### Validación robusta de archivos:
```python
def validate_file_security(file):
    # Validar tipo MIME real (no solo extensión)
    import magic
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)

    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Tipo de archivo no permitido: {mime}")

    # Validar contenido del archivo
    if mime == 'application/pdf':
        # Verificar que es un PDF válido
        try:
            import PyPDF2
            PyPDF2.PdfReader(file)
            file.seek(0)
        except:
            raise ValueError("Archivo PDF corrupto")
```

## 📝 LOGGING ESTRUCTURADO

### ❌ INCORRECTO:
```python
app.logger.error(f"Error processing file {filename}: {error}")
```

### ✅ CORRECTO:
```python
app.logger.error(
    "Error processing file",
    extra={
        "filename": filename,
        "error": str(error),
        "user_id": user_id,
        "operation": "file_upload"
    }
)
```

## 🧪 TESTING RECOMENDADO

### Estructura de tests:
```
tests/
├── __init__.py
├── test_api.py
├── test_file_upload.py
├── test_validation.py
└── conftest.py
```

### Ejemplo de test básico:
```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_submit_application_success(client):
    data = {
        'nombre': 'Test',
        'email': 'test@example.com',
        'telefono': '+1234567890'
    }
    response = client.post('/api/submit', data=data)
    assert response.status_code == 201
```

## 🚀 OPTIMIZACIONES DE RENDIMIENTO

### 1. Cache de Cloudinary URLs:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cloudinary_url(public_id, resource_type):
    return f"https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{public_id}"
```

### 2. Paginación eficiente:
```python
def get_applications_paginated(page=1, limit=50):
    skip = (page - 1) * limit

    # Usar índices compuestos para mejor rendimiento
    pipeline = [
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {"$project": {"_id": 0, "files": 0}}  # Excluir campos pesados
    ]

    return list(candidates.aggregate(pipeline))
```

## 🔐 CONFIGURACIÓN SEGURA

### Variables de entorno requeridas:
```bash
# Producción
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db"
export CLOUDINARY_CLOUD_NAME="your_cloud_name"
export CLOUDINARY_API_KEY="your_api_key"
export CLOUDINARY_API_SECRET="your_api_secret"
export SECRET_KEY="$(openssl rand -hex 32)"
export ADMIN_USERNAME="admin_user"
export ADMIN_PASSWORD="$(openssl rand -base64 32)"
```

## 📊 MONITOREO Y MÉTRICAS

### Health check robusto:
```python
@app.route('/api/health')
def health_check():
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.1.0",
        "checks": {}
    }

    # Test MongoDB
    try:
        db.command('ping')
        health["checks"]["mongodb"] = "healthy"
    except Exception as e:
        health["checks"]["mongodb"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    # Test Cloudinary
    try:
        cloudinary.api.ping()
        health["checks"]["cloudinary"] = "healthy"
    except Exception as e:
        health["checks"]["cloudinary"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"

    status_code = 200 if health["status"] == "healthy" else 503
    return jsonify(health), status_code
```

## 🎯 VALIDACIÓN FRONTEND MEJORADA

### Validación en tiempo real:
```javascript
function validateFileType(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const arr = new Uint8Array(e.target.result).subarray(0, 4);
            let header = "";
            for (let i = 0; i < arr.length; i++) {
                header += arr[i].toString(16);
            }

            // PDF signature
            if (header === "25504446") {
                resolve(true);
            } else {
                reject(new Error("Archivo no es un PDF válido"));
            }
        };
        reader.readAsArrayBuffer(file);
    });
}
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] Instalar `python-magic` para validación MIME
- [ ] Configurar logging estructurado en producción
- [ ] Implementar rate limiting con Redis
- [ ] Agregar tests unitarios básicos
- [ ] Configurar monitoreo de errores (Sentry)
- [ ] Implementar backup automático de MongoDB
- [ ] Agregar compresión de respuestas HTTP
- [ ] Configurar SSL/TLS en producción
