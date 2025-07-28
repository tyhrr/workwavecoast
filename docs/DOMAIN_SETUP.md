# 🌐 Configuración de Dominio Personalizado - WorkWave Coast

## Pasos para Configurar tu Dominio `workwavecoast.online`

### 📋 **Archivos Creados/Modificados:**
- ✅ `index.html` - Tu archivo original copiado desde `frontend/` con rutas ajustadas
- ✅ `CNAME` - Archivo con tu dominio personalizado  
- ✅ `.github/workflows/deploy.yml` - Deployment automático
- ✅ `frontend/script.js` - Actualizado para tu dominio
- ✅ `backend/app.py` - CORS configurado para tu dominio

### 🚀 **Paso 1: Subir Cambios a GitHub**

```bash
git add .
git commit -m "Configure custom domain and GitHub Pages deployment"
git push origin main
```

### ⚙️ **Paso 2: Configurar GitHub Pages**

1. Ve a tu repositorio en GitHub: `https://github.com/tuusuario/workwavecoast`
2. Ve a **Settings** > **Pages**
3. En **Source**, selecciona **GitHub Actions**
4. En **Custom domain**, ingresa: `workwavecoast.online`
5. Marca **Enforce HTTPS**

### 🌐 **Paso 3: Configurar DNS en tu Proveedor de Dominio**

En tu panel de control del dominio (donde compraste `workwavecoast.online`):

#### **Registros DNS a Configurar:**

```dns
Type: CNAME
Name: www
Value: tuusuario.github.io

Type: A
Name: @
Value: 185.199.108.153

Type: A  
Name: @
Value: 185.199.109.153

Type: A
Name: @
Value: 185.199.110.153

Type: A
Name: @
Value: 185.199.111.153
```

**IMPORTANTE**: Reemplaza `tuusuario` por tu nombre de usuario de GitHub.

### 🔧 **Paso 4: Configurar Backend en Render/Railway**

Para que tu API funcione, necesitas desplegar el backend:

#### **Opción A: Render (Recomendado)**
1. Ve a [render.com](https://render.com)
2. Conecta tu repositorio GitHub
3. Crea un **Web Service**
4. Configuración:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python app.py`
   - **Environment**: Python 3

#### **Variables de Entorno en Render:**
```env
MONGODB_URI=tu_mongodb_uri_de_atlas
CLOUDINARY_CLOUD_NAME=tu_cloudinary_name
CLOUDINARY_API_KEY=tu_cloudinary_key
CLOUDINARY_API_SECRET=tu_cloudinary_secret
PORT=10000
```

### 📱 **Paso 5: Actualizar CORS en el Backend**

Actualiza tu `app.py` para permitir tu dominio:

```python
from flask_cors import CORS

# Configurar CORS para tu dominio
CORS(app, origins=[
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://localhost:3000",
    "http://127.0.0.1:5500"
])
```

### 🎯 **Estructura Final:**

```
workwavecoast/
├── index.html              # ✅ Página principal
├── CNAME                   # ✅ Dominio personalizado
├── frontend/
│   ├── index.html         # Original
│   ├── script.js          # ✅ Actualizado
│   ├── styles.css
│   └── img/
├── backend/
│   ├── app.py             # ✅ API Flask
│   ├── requirements.txt
│   └── .env              # Configurar en Render
├── .github/workflows/
│   └── deploy.yml         # ✅ Deployment automático
└── docs/
```

### 🔄 **Flujo de Trabajo:**

1. **Frontend**: GitHub Pages → `workwavecoast.online`
2. **Backend**: Render → `workwavecoast-backend.onrender.com`
3. **Database**: MongoDB Atlas
4. **Files**: Cloudinary

### ⏱️ **Tiempos de Propagación:**

- **GitHub Pages**: 5-10 minutos
- **DNS**: 24-48 horas (puede ser menos)
- **SSL Certificate**: Automático con GitHub Pages

### 🧪 **Testing:**

Una vez configurado, podrás acceder a:
- `https://workwavecoast.online` → Tu sitio web
- `https://workwavecoast.online/frontend/` → Frontend original
- Tu API estará en Render

### 🚨 **Troubleshooting:**

#### Si tu dominio no funciona:
1. Verifica que el archivo `CNAME` tenga solo: `workwavecoast.online`
2. Revisa que los DNS records estén correctos
3. Espera 24-48 horas para propagación DNS
4. Verifica en GitHub Pages settings que el dominio esté configurado

#### Si el formulario no funciona:
1. Verifica que el backend esté desplegado en Render
2. Revisa la consola del navegador para errores CORS
3. Confirma que MongoDB Atlas permita conexiones desde Render

### 🎉 **¡Listo!**

Una vez completados estos pasos, tu sitio estará disponible en:
**https://workwavecoast.online** 🚀

---

**Nota**: Este setup es completamente gratuito usando GitHub Pages + Render free tier + MongoDB Atlas free tier.
