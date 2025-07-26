# WorkWave Coast

Plataforma para la gestión de postulaciones laborales en la costa croata. Incluye frontend moderno y backend robusto con integración a MongoDB Atlas y Firebase Storage.

---

## Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Guía de Instalación y Despliegue](#guía-de-instalación-y-despliegue)
- [Configuración de MongoDB Atlas](#configuración-de-mongodb-atlas)
- [Configuración de Firebase Storage](#configuración-de-firebase-storage)
- [Uso de la Aplicación](#uso-de-la-aplicación)
- [Buenas Prácticas](#buenas-prácticas)
- [Tareas Pendientes](#tareas-pendientes)

---

## Descripción General
WorkWave Coast permite a candidatos postularse a empleos en la costa croata, subiendo su información y documentos. El backend almacena los datos en MongoDB Atlas y los archivos en Firebase Storage.

## Tecnologías Utilizadas
- Frontend: HTML5, CSS3, JavaScript (fetch, FormData)
- Backend: Python 3, Flask, Flask-CORS
- Base de datos: MongoDB Atlas
- Almacenamiento de archivos: Firebase Storage, Cloudinary (opcional)
- Despliegue: Render (backend), Netlify/Vercel (frontend)

## Estructura del Proyecto
```
backend/
  app.py (o main.py)
  .env
  requirements.txt
  .gitignore
frontend/
  index.html
  styles.css
  script.js
  img/
    hero.jpg
    workwave2.png
    ...
docs/
  conexion_backend_mongodb_firebase.md
```

## Guía de Instalación y Despliegue

### 1. Clonar el repositorio
```bash
git clone <repo_url>
cd WorkWave Coast
```

### 2. Configurar el backend
- Ve a la carpeta `/backend`.
- Crea el archivo `.env` con tu URI de MongoDB Atlas:
  ```env
  MONGODB_URI=mongodb+srv://alnsal:E9A9LU6O1CEN5d0W@workwave.mxkpkgw.mongodb.net/?retryWrites=true&w=majority&appName=Workwave
  ```
- Asegúrate de que `.env` esté en `.gitignore`.
- Instala las dependencias localmente (opcional):
  ```bash
  pip install -r requirements.txt
  ```

### 3. Despliegue en Render (backend)
- Sube el proyecto a GitHub.
- En Render, crea un nuevo Web Service y conecta tu repo.
- Elige `/backend` como root.
- Render instalará automáticamente las dependencias de `requirements.txt`.
- En "Start Command" pon: `gunicorn app:app` (o el nombre de tu archivo principal).
- Configura la variable de entorno `MONGODB_URI` en el panel de Render.

### 4. Configurar el frontend
- Ve a la carpeta `/frontend`.
- Sube el contenido a Netlify, Vercel o tu hosting estático favorito.
- Asegúrate de que las rutas de imágenes y scripts sean correctas.

### 5. Pruebas
- Abre el frontend y prueba el envío de formularios.
- Verifica que los datos lleguen a MongoDB y los archivos a Firebase.

---

## Configuración de MongoDB Atlas
Consulta el archivo `docs/conexion_backend_mongodb_firebase.md` para una guía paso a paso sobre cómo crear el cluster, usuario, base de datos y obtener la URI.

## Configuración de Firebase Storage
Consulta el mismo archivo para la integración y subida de archivos desde Flask.

---

## Uso de la Aplicación
1. El usuario accede al frontend y llena el formulario de postulación.
2. El formulario envía los datos y archivos al backend Flask.
3. El backend guarda los datos en MongoDB Atlas y los archivos en Firebase Storage.
4. El usuario recibe confirmación visual en la web.

---

## Buenas Prácticas
- Nunca subas `.env` ni credenciales al repositorio.
- Usa variables de entorno para todas las claves.
- Documenta cualquier cambio relevante en este README y en los archivos de docs.
- Haz pruebas antes de lanzar a producción.

---

## Tareas Pendientes
- [ ] Desplegar el backend en Render y probar la conexión real con MongoDB Atlas.
- [ ] Configurar y probar la subida de archivos a Firebase Storage desde el backend.
- [ ] Desplegar el frontend en Netlify/Vercel y probar el flujo completo.
- [ ] Mejorar validaciones y mensajes de error en el frontend.
- [ ] Agregar autenticación y panel de administración (opcional).
- [ ] Documentar endpoints de la API y ejemplos de uso.
- [ ] Agregar tests automáticos para el backend.

---

¿Dudas? Consulta la documentación en `/docs` o abre un issue en el repositorio.
