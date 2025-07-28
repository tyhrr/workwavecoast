# WorkWave Coast - Setup Guide

## Configuración Completa del Proyecto

### 1. Configuración del Backend

El backend ya está configurado con:
- ✅ Entorno virtual de Python creado
- ✅ Dependencias instaladas (Flask, MongoDB, Cloudinary, etc.)
- ✅ Archivo `app.py` creado con la API completa
- ✅ Estructura de archivos lista

### 2. Variables de Entorno

**IMPORTANTE**: Debes crear el archivo `.env` en la carpeta `backend/`:

1. Copia el archivo `backend/env.example` a `backend/.env`
2. Configura las siguientes variables:

```env
# MongoDB Atlas (OBLIGATORIO)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=YourApp

# Cloudinary (OPCIONAL - para subida de archivos)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Puerto del servidor
PORT=5000
```

### 3. Configuración de MongoDB Atlas

1. Ve a https://www.mongodb.com/cloud/atlas
2. Crea una cuenta gratuita
3. Crea un nuevo cluster (Free Tier)
4. Crea una base de datos llamada `workwave`
5. Crea una colección llamada `candidates`
6. Obtén tu URI de conexión y agrégala al archivo `.env`

### 4. Ejecutar la Aplicación

#### Opción 1: Usando el script de Windows
```batch
start_backend.bat
```

#### Opción 2: Manualmente
```powershell
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Ir a la carpeta backend
cd backend

# Ejecutar la aplicación
python app.py
```

#### Opción 3: Usando VS Code Tasks
- Presiona `Ctrl+Shift+P`
- Busca "Tasks: Run Task"
- Selecciona "Start Backend Server"

### 5. Frontend

El frontend está listo para usar:
- Abre `frontend/index.html` en tu navegador
- O usa la extensión Live Server de VS Code para desarrollo

### 6. URLs de la API

Una vez que el backend esté ejecutándose:

- **Backend**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health
- **Submit Application**: POST http://localhost:5000/api/submit
- **Get Applications**: GET http://localhost:5000/api/applications

### 7. Estructura de Archivos Final

```
workwave coast/
├── backend/
│   ├── app.py              # ✅ API Flask principal
│   ├── requirements.txt    # ✅ Dependencias Python
│   ├── .env               # ⚠️ Debes crear este archivo
│   ├── env.example        # ✅ Plantilla de variables
│   └── .gitignore         # ✅ Configurado
├── frontend/
│   ├── index.html         # ✅ Interfaz principal
│   ├── script.js          # ✅ Lógica del frontend
│   ├── styles.css         # ✅ Estilos
│   └── img/               # ✅ Imágenes
├── docs/                  # ✅ Documentación
├── .venv/                 # ✅ Entorno virtual
└── start_backend.bat      # ✅ Script de inicio
```

### 8. Próximos Pasos

1. **Crear archivo `.env`** con las credenciales de MongoDB
2. **Configurar MongoDB Atlas** siguiendo la guía en `docs/`
3. **Ejecutar el backend** usando cualquiera de las opciones
4. **Probar la aplicación** abriendo el frontend

### 9. Desarrollo

Para desarrollo activo, puedes usar:
- **Backend**: El servidor se reiniciará automáticamente al hacer cambios
- **Frontend**: Usa Live Server para ver cambios en tiempo real

¡El proyecto está completamente configurado y listo para usar! 🚀
