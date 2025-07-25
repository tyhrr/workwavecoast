# 🏖️ WorkWave Coast

**Sistema web para recopilar postulaciones de trabajo en la costa croata**

Una solución completa y simple para gestionar aplicaciones laborales en el sector hotelero y gastronómico de Croacia.

## 🌟 Características

- ✅ **Frontend responsivo** - HTML, CSS y JavaScript vanilla (sin frameworks)
- ✅ **Backend ligero** - Python Flask con funcionalidades completas
- ✅ **Gestión de archivos** - Subida segura de CVs y documentos
- ✅ **Exportación de datos** - CSV y Excel descargables
- ✅ **GitHub Pages ready** - Frontend deployable estáticamente
- ✅ **Fácil configuración** - Un solo comando para ejecutar

## 📁 Estructura del Proyecto

```
WorkWave Coast/
├── index.html              # Página principal del formulario
├── style.css               # Estilos CSS (responsive, sin dependencias)
├── script.js               # JavaScript para el frontend
├── server.py               # Servidor backend en Python Flask
├── requirements.txt        # Dependencias de Python
├── uploads/                # Carpeta para archivos subidos
├── data.csv                # Base de datos CSV (se crea automáticamente)
├── export.xlsx             # Archivo Excel exportable (se genera automáticamente)
└── README.md               # Este archivo
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- Git (para clonar el repositorio)

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/workwave-coast.git
cd workwave-coast
```

### 2. Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servidor
```bash
python server.py
```

El servidor estará disponible en: **http://localhost:5000**

## 🌐 Uso del Sistema

### Para usuarios (postulantes)
1. Abre la página web en tu navegador
2. Completa el formulario con tus datos:
   - Nombre y apellido
   - Nacionalidad
   - Puesto al que aplicas
   - Sube tu CV (solo PDF)
   - Documentos adicionales (opcional)
3. Envía tu postulación
4. Recibirás confirmación de envío exitoso

### Para administradores
1. **Ver estadísticas**: `GET http://localhost:5000/stats`
2. **Descargar Excel**: `GET http://localhost:5000/download`
3. **Acceder a datos CSV**: Archivo `data.csv` en la raíz del proyecto
4. **Archivos subidos**: Carpeta `uploads/`

## 🔧 Endpoints del API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información del API |
| POST | `/submit` | Enviar nueva postulación |
| GET | `/download` | Descargar archivo Excel |
| GET | `/stats` | Estadísticas del sistema |

## 📊 Gestión de Datos

### Archivo CSV (`data.csv`)
Contiene todas las postulaciones con los siguientes campos:
- `timestamp` - Fecha y hora de envío
- `nombre` - Nombre del postulante
- `apellido` - Apellido del postulante
- `nacionalidad` - Nacionalidad
- `puesto` - Puesto al que aplica
- `cv_filename` - Nombre del archivo CV
- `documentos_adicionales` - Lista de documentos extras
- `ip_address` - Dirección IP del envío

### Archivo Excel (`export.xlsx`)
- Se genera automáticamente desde el CSV
- Formato optimizado para visualización
- Descargable desde `/download`
- Se actualiza con cada nueva postulación

### Archivos subidos (`uploads/`)
- Todos los CVs y documentos se guardan aquí
- Nombres únicos con timestamp para evitar conflictos
- Validación de tipos de archivo
- Límite de tamaño: 5MB por archivo

## 🌍 Despliegue

### Frontend en GitHub Pages
1. Sube todo el proyecto a un repositorio de GitHub
2. Ve a Settings > Pages
3. Selecciona la rama main como fuente
4. Tu formulario estará disponible en: `https://tu-usuario.github.io/workwave-coast`

**Nota**: El frontend funcionará independientemente, pero para enviar datos necesitarás el backend ejecutándose.

### Backend en servidor
Para producción, puedes usar servicios como:
- Heroku
- DigitalOcean
- AWS EC2
- Google Cloud Platform

Simplemente instala las dependencias y ejecuta `python server.py`.

## ⚙️ Configuración Avanzada

### Variables de configuración en `server.py`:
```python
UPLOAD_FOLDER = 'uploads'           # Carpeta de archivos
CSV_FILE = 'data.csv'              # Archivo de datos
EXCEL_FILE = 'export.xlsx'         # Archivo Excel
MAX_FILE_SIZE = 5 * 1024 * 1024    # Tamaño máximo (5MB)
```

### Personalizar campos del formulario:
- Edita las opciones en `index.html`
- Actualiza la validación en `script.js`
- Modifica los headers CSV en `server.py`

## 🔒 Seguridad

- ✅ Validación de tipos de archivo
- ✅ Sanitización de nombres de archivo
- ✅ Límites de tamaño de archivo
- ✅ Validación de campos requeridos
- ✅ Protección CORS configurada

## 🐛 Solución de Problemas

### Error: "No se puede conectar al servidor"
- Verifica que el servidor esté ejecutándose: `python server.py`
- Confirma que esté en el puerto 5000: `http://localhost:5000`

### Error: "Archivo demasiado grande"
- Verifica que el CV sea menor a 5MB
- Comprime el PDF si es necesario

### Error: "Tipo de archivo no permitido"
- CV: Solo archivos PDF
- Documentos adicionales: PDF, JPG, PNG, DOC, DOCX

### El Excel no se genera
- Verifica que pandas y openpyxl estén instalados
- Comprueba permisos de escritura en la carpeta

## 📝 Desarrollo

### Agregar nuevos campos
1. Añade el campo HTML en `index.html`
2. Actualiza la validación en `script.js`
3. Modifica el backend en `server.py`
4. Actualiza los headers CSV

### Personalizar estilos
- Edita `style.css`
- Variables CSS en `:root` para fácil personalización
- Diseño responsive incluido

## 📞 Soporte

Para problemas o mejoras:
1. Abre un issue en GitHub
2. Incluye detalles del error
3. Proporciona pasos para reproducir

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

## 🙏 Contribuciones

¡Las contribuciones son bienvenidas!
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push y abre un Pull Request

---

**Desarrollado con ❤️ para facilitar oportunidades laborales en Croacia**
