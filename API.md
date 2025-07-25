# 🔌 WorkWave Coast - Documentación del API

## Base URL
- **Desarrollo Local**: `http://localhost:5000`
- **Producción**: Configurar según tu servidor

## Endpoints

### 1. Información del API
```
GET /
```

**Respuesta:**
```json
{
    "status": "ok",
    "message": "WorkWave Coast API funcionando",
    "endpoints": {
        "/submit": "POST - Enviar postulación",
        "/download": "GET - Descargar Excel",
        "/stats": "GET - Estadísticas"
    }
}
```

### 2. Enviar Postulación
```
POST /submit
Content-Type: multipart/form-data
```

**Parámetros:**
- `nombre` (string, requerido): Nombre del postulante
- `apellido` (string, requerido): Apellido del postulante
- `nacionalidad` (string, requerido): Nacionalidad
- `puesto` (string, requerido): Puesto al que aplica
- `cv` (file, requerido): Archivo PDF del curriculum
- `documentos` (files[], opcional): Documentos adicionales

**Respuesta exitosa:**
```json
{
    "success": true,
    "message": "Postulación recibida exitosamente",
    "timestamp": "2025-07-25T10:30:00.000000"
}
```

**Respuesta de error:**
```json
{
    "success": false,
    "message": "Descripción del error"
}
```

### 3. Descargar Excel
```
GET /download
```

**Respuesta:** Descarga del archivo Excel con todas las postulaciones.

### 4. Estadísticas
```
GET /stats
```

**Respuesta:**
```json
{
    "total_postulaciones": 15,
    "archivo_csv_existe": true,
    "archivo_excel_existe": true,
    "carpeta_uploads_existe": true
}
```

## Códigos de Estado HTTP

- `200` - Operación exitosa
- `400` - Error en los datos enviados
- `404` - Recurso no encontrado
- `500` - Error interno del servidor

## Validaciones

### Archivos CV
- **Formato**: Solo PDF
- **Tamaño máximo**: 5MB
- **Requerido**: Sí

### Documentos Adicionales
- **Formatos**: PDF, JPG, JPEG, PNG, DOC, DOCX
- **Tamaño máximo**: 5MB por archivo
- **Requerido**: No

### Campos de Texto
- **Nombre**: Texto, requerido
- **Apellido**: Texto, requerido
- **Nacionalidad**: Texto/Select, requerido
- **Puesto**: Texto/Select, requerido

## Ejemplo de Uso con JavaScript

```javascript
const formData = new FormData();
formData.append('nombre', 'Juan');
formData.append('apellido', 'Pérez');
formData.append('nacionalidad', 'España');
formData.append('puesto', 'Camarero/a');
formData.append('cv', cvFile); // File object

fetch('http://localhost:5000/submit', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Postulación enviada exitosamente');
    } else {
        console.error('Error:', data.message);
    }
});
```

## Ejemplo de Uso con cURL

```bash
curl -X POST http://localhost:5000/submit \
  -F "nombre=Juan" \
  -F "apellido=Pérez" \
  -F "nacionalidad=España" \
  -F "puesto=Camarero/a" \
  -F "cv=@/path/to/cv.pdf"
```
