# WorkWave Coast

Plataforma para la gestión de postulaciones laborales en la costa croata. Incluye frontend moderno y backend robusto con integración a MongoDB Atlas y Firebase Storage.

---

## Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Estructura del Proyecto](#estructura-del-proyecto)
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
