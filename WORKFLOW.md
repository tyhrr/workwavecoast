# 🚀 Workflow de Desarrollo - WorkWave Coast

## 📋 **Guía Completa para Trabajar en el Proyecto**

### 🎯 **Resumen del Proyecto**
- **Frontend**: HTML/CSS/JS → GitHub Pages
- **Backend**: Flask/Python → Render
- **Database**: MongoDB Atlas
- **Storage**: Cloudinary
- **Domain**: workwavecoast.online

---

## 🔧 **1. CONFIGURACIÓN INICIAL (Solo una vez)**

### **1.1 Abrir VS Code y Terminal**
```powershell
# Navegar al proyecto
cd "C:\Users\alang\Desktop\Proyectos\workwave coast"

# Abrir VS Code
code .
```

### **1.2 Activar Entorno Virtual**
```powershell
# Activar el entorno virtual de Python
.venv\Scripts\Activate.ps1

# Verificar que esté activo (debería mostrar (.venv) en el prompt)
```

### **1.3 Verificar Estado del Proyecto**
```powershell
# Ver status de Git
git status

# Ver rama actual
git branch

# Actualizar desde GitHub
git pull origin main
```

---

## 💻 **2. WORKFLOW DE DESARROLLO DIARIO**

### **2.1 Iniciar Sesión de Trabajo**

#### **Abrir Archivos Principales en VS Code:**
- 📁 `frontend/index.html` - Interfaz principal
- 📁 `frontend/styles.css` - Estilos
- 📁 `frontend/script.js` - Lógica frontend
- 📁 `backend/app.py` - API Flask
- 📁 `backend/.env` - Variables de entorno (si existe)

#### **Iniciar Terminal y Activar Entorno:**
```powershell
# Terminal 1: Backend
cd "C:\Users\alang\Desktop\Proyectos\workwave coast"
.venv\Scripts\Activate.ps1
```

### **2.2 Desarrollo del Backend**

#### **Configurar Variables de Entorno (si no existe):**
```powershell
# Crear .env desde el ejemplo
cd backend
copy env.example .env

# Editar .env con tus credenciales
code .env
```

#### **Ejecutar Backend Localmente:**
```powershell
# Opción 1: Script automático
cd "C:\Users\alang\Desktop\Proyectos\workwave coast"
.\start_backend.bat

# Opción 2: Manual
cd backend
python app.py

# Opción 3: VS Code Task
# Ctrl+Shift+P → "Tasks: Run Task" → "Start Backend Server"
```

#### **Verificar Backend:**
```powershell
# En otro terminal o navegador
curl http://localhost:5000/api/health
# O abrir: http://localhost:5000/api/health
```

### **2.3 Desarrollo del Frontend**

#### **Abrir Frontend Localmente:**
```powershell
# Opción 1: Live Server (Recomendado)
# Instalar extensión "Live Server" en VS Code
# Click derecho en frontend/index.html → "Open with Live Server"

# Opción 2: Abrir directamente
# Doble click en frontend/index.html
```

#### **URLs de Desarrollo:**
- **Frontend**: `http://127.0.0.1:5500/frontend/` (Live Server)
- **Backend**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/api/health`

---

## 🔄 **3. CICLO DE DESARROLLO**

### **3.1 Hacer Cambios**

#### **Frontend (HTML/CSS/JS):**
1. Editar archivos en `frontend/`
2. Guardar cambios (Ctrl+S)
3. El navegador se actualiza automáticamente (Live Server)

#### **Backend (Python):**
1. Editar `backend/app.py`
2. Guardar cambios (Ctrl+S)
3. El servidor Flask se reinicia automáticamente (debug=True)

### **3.2 Probar Cambios**

#### **Probar Frontend:**
```powershell
# Verificar en navegador:
# - Estilos se cargan correctamente
# - Formulario funciona
# - JavaScript no tiene errores (F12 → Console)
```

#### **Probar Backend:**
```powershell
# Verificar endpoints
curl -X GET http://localhost:5000/
curl -X GET http://localhost:5000/api/health
curl -X GET http://localhost:5000/api/applications

# Probar envío de formulario desde frontend
```

#### **Probar Integración:**
1. Llenar formulario en frontend
2. Enviar datos
3. Verificar en MongoDB Atlas que llegaron los datos
4. Revisar logs en terminal del backend

---

## 📤 **4. GUARDAR Y SUBIR CAMBIOS**

### **4.1 Verificar Cambios**
```powershell
# Ver qué archivos cambiaron
git status

# Ver cambios específicos
git diff

# Ver cambios en archivo específico
git diff frontend/styles.css
```

### **4.2 Commit y Push**
```powershell
# Agregar cambios específicos
git add frontend/styles.css
git add backend/app.py

# O agregar todos los cambios
git add .

# Crear commit con mensaje descriptivo
git commit -m "Add new form validation and improve CSS styling"

# Subir a GitHub
git push origin main
```

### **4.3 Verificar Deployment**
```powershell
# GitHub Pages se actualiza automáticamente
# Verificar en ~5-10 minutos:
# https://tyhrr.github.io/workwavecoast

# Cuando tengas dominio configurado:
# https://workwavecoast.online
```

---

## 🌐 **5. DEPLOYMENT A PRODUCCIÓN**

### **5.1 Frontend (GitHub Pages)**
- ✅ **Automático**: Se despliega con cada `git push`
- 🔗 **URL**: `https://tyhrr.github.io/workwavecoast`
- ⏱️ **Tiempo**: 5-10 minutos

### **5.2 Backend (Render)**

#### **Primera vez:**
1. Ve a [render.com](https://render.com)
2. Conecta tu repo GitHub
3. Crea "Web Service"
4. Configuración:
   ```
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && python app.py
   Environment: Python 3
   ```

#### **Variables de Entorno en Render:**
```env
MONGODB_URI=mongodb+srv://...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
PORT=10000
```

#### **Actualizaciones:**
- ✅ **Automático**: Se redespliega con cada `git push`
- 🔗 **URL**: `https://tu-app.onrender.com`
- ⏱️ **Tiempo**: 2-5 minutos

---

## 🔍 **6. DEBUGGING Y TROUBLESHOOTING**

### **6.1 Problemas Comunes del Frontend**

#### **CSS no se carga:**
```powershell
# Verificar rutas en index.html
# Debe ser: href="frontend/styles.css"
# NO: href="../frontend/styles.css"

# Limpiar cache del navegador
# Ctrl+F5 o Ctrl+Shift+R
```

#### **JavaScript errores:**
```powershell
# Abrir DevTools (F12)
# Ver tab "Console" para errores
# Verificar que script.js se cargue correctamente
```

#### **Formulario no envía:**
```powershell
# Verificar que backend esté corriendo
curl http://localhost:5000/api/health

# Verificar CORS en app.py
# Revisar console del navegador para errores CORS
```

### **6.2 Problemas Comunes del Backend**

#### **Error de importación:**
```powershell
# Verificar entorno virtual activo
.venv\Scripts\Activate.ps1

# Reinstalar dependencias
pip install -r backend/requirements.txt
```

#### **Error de MongoDB:**
```powershell
# Verificar .env existe y tiene MONGODB_URI
cat backend/.env

# Probar conexión
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
print(client.admin.command('ping'))
"
```

#### **Error de Cloudinary:**
```powershell
# Verificar variables en .env
# CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

# Probar upload básico
```

---

## 📋 **7. CHECKLIST ANTES DE FINALIZAR SESIÓN**

### **🔄 ANTES DE CERRAR VS CODE - PASOS OBLIGATORIOS:**

#### **7.1 Guardar Todo el Trabajo**
```powershell
# 1. Guardar todos los archivos abiertos
# Ctrl+K, Ctrl+S (Guardar todos)
# O verificar que no haya puntos blancos en las pestañas (● = no guardado)
```

#### **7.2 Detener Servicios en Ejecución**
```powershell
# 1. Detener el servidor Flask
# En el terminal donde corre: Ctrl+C

# 2. Detener Live Server (si está activo)
# Click en "Port: 5500" en la barra inferior → Stop

# 3. Verificar que no haya procesos corriendo
# Ver que no haya terminales activos ejecutando comandos
```

#### **7.3 Verificar Estado del Código**
```powershell
# 1. Ver qué archivos han cambiado
git status

# 2. Ver las diferencias si hay cambios
git diff

# 3. Verificar que no haya errores de sintaxis
# Revisar que no haya líneas rojas en VS Code
```

#### **7.4 Confirmar y Subir Cambios**
```powershell
# Si hay cambios, guardarlos:

# 1. Agregar cambios
git add .

# 2. Hacer commit con mensaje descriptivo
git commit -m "Session work: describe what you changed"

# 3. Subir a GitHub
git push origin main

# 4. Verificar que se subió correctamente
git status
# Debería decir: "nothing to commit, working tree clean"
```

#### **7.5 Verificar Archivos Sensibles**
```powershell
# 1. Verificar que .env NO esté en Git
git ls-files | grep .env
# No debería mostrar nada

# 2. Verificar .gitignore incluye archivos sensibles
cat backend/.gitignore
# Debe incluir: .env, __pycache__/, *.pyc, .env.*
```

#### **7.6 Cerrar VS Code Correctamente**
```powershell
# 1. Cerrar terminales activos
# Click en el ícono de papelera en cada terminal

# 2. Cerrar pestañas de archivos
# Ctrl+W para cerrar pestaña actual
# Ctrl+K, Ctrl+W para cerrar todas

# 3. Guardar workspace (opcional)
# File → Save Workspace As... → Guardar como "WorkWave.code-workspace"

# 4. Cerrar VS Code
# Alt+F4 o File → Exit
```

---

### **✅ CHECKLIST COMPLETO ANTES DE CERRAR:**

#### **✅ Desarrollo Local:**
- [ ] Todos los archivos guardados (no hay puntos ● en pestañas)
- [ ] Frontend funciona correctamente (última prueba)
- [ ] Backend responde a endpoints (última verificación)
- [ ] Formulario envía datos correctamente
- [ ] No hay errores en console del navegador (F12)
- [ ] No hay errores en terminal del backend
- [ ] Servidor Flask detenido (Ctrl+C)
- [ ] Live Server detenido (si estaba activo)

#### **✅ Código:**
- [ ] Variables sensibles NO están en el código
- [ ] Comentarios agregados donde sea necesario
- [ ] Código limpio y organizado
- [ ] No hay líneas rojas de error en VS Code
- [ ] Archivo .env existe y tiene las variables necesarias
- [ ] .env NO está en Git (verificado)

#### **✅ Git:**
- [ ] `git status` ejecutado - cambios revisados
- [ ] `git add .` - Cambios agregados (si los hay)
- [ ] `git commit -m "mensaje descriptivo"` - Commit creado
- [ ] `git push origin main` - Cambios subidos
- [ ] `git status` final = "working tree clean"
- [ ] GitHub repository actualizado

#### **✅ Producción:**
- [ ] GitHub Actions workflow exitoso (si se subieron cambios)
- [ ] Frontend funciona en GitHub Pages (verificar en ~10min)
- [ ] Backend funciona en Render (si se hicieron cambios)
- [ ] Base de datos conectada y funcionando
- [ ] URLs de producción funcionando correctamente

#### **✅ VS Code:**
- [ ] Terminales cerrados (no hay procesos activos)
- [ ] Pestañas cerradas o workspace guardado
- [ ] Extensiones funcionando correctamente
- [ ] No hay tareas en background corriendo
- [ ] Workspace guardado (opcional)

#### **✅ Sistema:**
- [ ] Entorno virtual Python se puede desactivar
- [ ] No hay archivos temporales importantes sin guardar
- [ ] Backup realizado (si es una sesión importante)

---

### **🚨 SI ALGO SALE MAL AL CERRAR:**

#### **Servidor no se detiene:**
```powershell
# Forzar cierre de Python/Flask
taskkill /F /IM python.exe

# O usar Task Manager
# Ctrl+Shift+Esc → Buscar python.exe → End Task
```

#### **Git no permite cerrar:**
```powershell
# Si hay conflictos o cambios sin confirmar
git stash  # Guardar cambios temporalmente
# O resolver conflictos y hacer commit normal
```

#### **VS Code no responde:**
```powershell
# Forzar cierre
Alt+F4
# O Task Manager → Code.exe → End Task
```

---

### **⚡ COMANDO RÁPIDO DE CIERRE:**

```powershell
# Script rápido para cerrar sesión limpiamente:
echo "Cerrando sesión de trabajo..."

# 1. Verificar estado
git status

# 2. Si hay cambios, confirmar
$response = Read-Host "¿Hay cambios para guardar? (y/n)"
if ($response -eq "y") {
    git add .
    $message = Read-Host "Mensaje del commit"
    git commit -m $message
    git push origin main
    echo "Cambios guardados y subidos ✅"
}

# 3. Verificar estado final
git status
echo "✅ Sesión cerrada correctamente"
```

---

### **✅ Desarrollo Local:**
- [ ] Frontend funciona correctamente
- [ ] Backend responde a todos los endpoints
- [ ] Formulario envía datos correctamente
- [ ] No hay errores en console del navegador
- [ ] No hay errores en terminal del backend

### **✅ Código:**
- [ ] Cambios guardados (Ctrl+S en todos los archivos)
- [ ] Variables sensibles NO están en el código
- [ ] Comentarios agregados donde sea necesario
- [ ] Código limpio y organizado

### **✅ Git:**
- [ ] `git add .` - Cambios agregados
- [ ] `git commit -m "mensaje descriptivo"` - Commit creado
- [ ] `git push origin main` - Cambios subidos
- [ ] GitHub Pages se actualiza correctamente

### **✅ Producción:**
- [ ] Backend funciona en Render
- [ ] Frontend funciona en GitHub Pages
- [ ] Base de datos recibe datos en MongoDB Atlas
- [ ] Archivos se suben a Cloudinary

---

## 🚀 **8. COMANDOS RÁPIDOS DE REFERENCIA**

### **Inicio Rápido:**
```powershell
cd "C:\Users\alang\Desktop\Proyectos\workwave coast"
.venv\Scripts\Activate.ps1
code .
.\start_backend.bat
```

### **Git Rápido:**
```powershell
git add .
git commit -m "Update: descripción del cambio"
git push origin main
```

### **Verificación Rápida:**
```powershell
# Backend health
curl http://localhost:5000/api/health

# Ver logs backend
# (en terminal donde corre Flask)

# Frontend
# Abrir http://127.0.0.1:5500/frontend/
```

### **Debugging Rápido:**
```powershell
# Ver errores Python
python backend/app.py

# Ver estado Git
git status

# Ver archivos modificados
git diff --name-only
```

---

## 📱 **9. EXTENSIONES VS CODE RECOMENDADAS**

```json
{
  "recommendations": [
    "ms-python.python",
    "ritwickdey.liveserver",
    "ms-python.flake8",
    "ms-vscode.vscode-json",
    "bradlc.vscode-tailwindcss",
    "formulahendry.auto-rename-tag",
    "esbenp.prettier-vscode"
  ]
}
```

---

## 🎯 **10. ESTRUCTURA DE ARCHIVOS PARA DESARROLLO**

```
workwave coast/
├── 📂 backend/           # ← Trabajar aquí para API
│   ├── app.py           # ← Archivo principal Flask
│   ├── .env             # ← Variables de entorno (crear)
│   ├── requirements.txt # ← Dependencias Python
│   └── .pylintrc        # ← Configuración linter
├── 📂 frontend/          # ← Trabajar aquí para UI
│   ├── index.html       # ← Página principal
│   ├── styles.css       # ← Estilos
│   ├── script.js        # ← Lógica frontend
│   └── 📂 img/          # ← Imágenes
├── 📂 .github/workflows/ # ← Deployment automático
├── index.html           # ← Para GitHub Pages
├── CNAME                # ← Dominio personalizado
└── start_backend.bat    # ← Script inicio rápido
```

---

**🎉 ¡Con este workflow tendrás un desarrollo eficiente y organizado!**

**💡 Tip**: Guarda este archivo como referencia y síguelo cada vez que trabajes en el proyecto.
