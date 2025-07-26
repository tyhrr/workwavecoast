# 🚀 Guía de Despliegue WorkWave Coast

## 📋 Prerrequisitos

Antes de desplegar, necesitas crear cuentas en:
- [MongoDB Atlas](https://www.mongodb.com/atlas) (Free Tier)
- [Cloudinary](https://cloudinary.com/) (Free Tier)
- [Render](https://render.com/) (Free Tier)

## 🔧 Configuración paso a paso

### 1. MongoDB Atlas

1. **Crear cuenta y cluster**:
   - Ve a [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Crea una cuenta gratuita
   - Crea un nuevo cluster (selecciona FREE tier)
   - Anota el nombre del cluster

2. **Configurar acceso**:
   - Ve a "Database Access" y crea un usuario
   - Ve a "Network Access" y agrega `0.0.0.0/0` (permitir desde cualquier IP)
   - En "Clusters", haz clic en "Connect" > "Connect your application"
   - Copia la URI de conexión (será algo como: `mongodb+srv://usuario:password@cluster.mongodb.net/`)

3. **Crear base de datos**:
   - Nombre de BD: `job_applications`
   - Colección: `candidates` (se crea automáticamente)

### 2. Cloudinary

1. **Crear cuenta**:
   - Ve a [Cloudinary](https://cloudinary.com/)
   - Crea una cuenta gratuita
   - Ve al Dashboard

2. **Obtener credenciales**:
   - Anota el `Cloud Name`
   - Anota el `API Key`
   - Anota el `API Secret`

### 3. Render (Backend)

1. **Preparar repositorio**:
   - Asegúrate de que todos los archivos estén en GitHub
   - La carpeta `backend/` debe contener `app.py` y `requirements.txt`

2. **Crear Web Service**:
   - Ve a [Render](https://render.com/)
   - Crea una cuenta y conecta con GitHub
   - Clic en "New Web Service"
   - Selecciona tu repositorio `workwavecoast`
   - Configuración:
     - **Name**: `workwavecoast-backend`
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Configurar variables de entorno**:
   En la sección "Environment Variables":
   ```
   MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/job_applications?retryWrites=true&w=majority
   CLOUDINARY_CLOUD_NAME=tu_cloud_name
   CLOUDINARY_API_KEY=tu_api_key
   CLOUDINARY_API_SECRET=tu_api_secret
   ```

4. **Desplegar**:
   - Haz clic en "Create Web Service"
   - Render automáticamente desplegará tu backend
   - Anota la URL que te proporciona (ej: `https://workwavecoast-backend.onrender.com`)

### 4. GitHub Pages (Frontend)

1. **Actualizar configuración**:
   - En `frontend/script.js`, actualiza `API_BASE_URL` con tu URL de Render
   
2. **Activar GitHub Pages**:
   - Ve a tu repositorio en GitHub
   - Settings > Pages
   - Source: "Deploy from a branch"
   - Branch: `main`
   - Folder: `/ (root)` o `/frontend` si reorganizas
   - Save

3. **Verificar**:
   - Tu frontend estará en: `https://tuusuario.github.io/workwavecoast`
   - O en tu dominio personalizado si configuraste CNAME

## 🔍 Verificación

### Verificar Backend
1. Ve a tu URL de Render: `https://tu-app.onrender.com`
2. Deberías ver: `{"status": "ok", "message": "WorkWave Coast API funcionando"...}`
3. Prueba health check: `https://tu-app.onrender.com/health`

### Verificar Frontend
1. Ve a tu GitHub Pages URL
2. Completa el formulario de prueba
3. Verifica que no hay errores en la consola del navegador

### Verificar Base de Datos
1. En MongoDB Atlas, ve a "Collections"
2. Después de enviar una aplicación, deberías ver datos en `job_applications.candidates`

## 🐛 Solución de Problemas

### Error de CORS
- Verifica que la URL de GitHub Pages esté en la lista de `origins` en `app.py`
- Formato: `["https://tuusuario.github.io", ...]`

### Error de MongoDB
- Verifica que la variable `MONGODB_URI` esté correcta en Render
- Asegúrate de que la IP `0.0.0.0/0` esté en la whitelist de MongoDB

### Error de Cloudinary
- Verifica las variables `CLOUDINARY_*` en Render
- Prueba las credenciales desde el dashboard de Cloudinary

### Backend no responde
- Ve a los logs en Render Dashboard
- Verifica que `gunicorn` esté instalado en `requirements.txt`

## 📊 URLs Finales

Una vez completado:
- **Frontend**: `https://tuusuario.github.io/workwavecoast`
- **Backend**: `https://tu-app.onrender.com`
- **API Docs**: `https://tu-app.onrender.com/`
- **Stats**: `https://tu-app.onrender.com/api/stats`
- **Export**: `https://tu-app.onrender.com/api/export`

## 🔄 Actualizaciones

Para actualizar:
1. Haz push a GitHub
2. Render se redespliega automáticamente
3. GitHub Pages se actualiza automáticamente
