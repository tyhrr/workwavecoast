# 🌊 WorkWaveCoast

![WorkWaveCoast](https://img.shields.io/badge/Status-En_Desarrollo-blue)

Plataforma web para reclutamiento de personal en hotelería y gastronomía para la costa croata. Este proyecto permite a los candidatos enviar sus aplicaciones a través de un formulario web sencillo, almacenando la información en una base de datos y los documentos en la nube.

## 📋 Características

- Formulario web responsive para envío de candidaturas
- Almacenamiento de datos en MongoDB Atlas
- Subida de CVs y documentación a servicios cloud
- Exportación de datos a CSV para análisis

## 🏗️ Arquitectura

El proyecto está dividido en cuatro componentes principales:

### 1️⃣ Frontend (GitHub Pages)

- Sitio web estático con HTML, CSS y JavaScript vanilla
- Formulario responsive para envío de datos y archivos
- Validación de datos en el cliente

### 2️⃣ Backend (Flask en Render)

- API REST desarrollada en Flask
- Endpoints para recepción de datos y exportación a CSV
- Middleware CORS para permitir conexiones desde GitHub Pages
- Integración con servicios de almacenamiento en la nube

### 3️⃣ Base de datos (MongoDB Atlas)

- Almacenamiento de información de candidatos
- Estructura flexible para documentos
- Tier gratuito de MongoDB Atlas

### 4️⃣ Almacenamiento de archivos (Cloudinary/Firebase)

- Subida segura de CVs y documentación adicional
- URLs permanentes para documentos
- Integración directa desde el backend

## 🚀 Instalación y Configuración

### Prerrequisitos

- Cuenta en GitHub
- Cuenta en MongoDB Atlas
- Cuenta en Cloudinary o Firebase
- Cuenta en Render

### Configuración del Frontend

```bash
# Clonar el repositorio
git clone https://github.com/tyhrr/workwavecoast.git
cd workwavecoast/frontend

# Abrir index.html en tu navegador para pruebas locales
```

### Configuración del Backend

```bash
# Navegar a la carpeta del backend
cd workwavecoast/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (.env)
# Crear archivo .env con las siguientes variables:
# MONGODB_URI=your_mongodb_uri
# CLOUDINARY_CLOUD_NAME=your_cloud_name
# CLOUDINARY_API_KEY=your_api_key
# CLOUDINARY_API_SECRET=your_api_secret
# o las variables para Firebase si usas esa opción

# Iniciar el servidor de desarrollo
python app.py
```

## 📦 Despliegue

### Frontend en GitHub Pages

1. Habilita GitHub Pages en la configuración del repositorio
2. Configura la rama `main` o la carpeta `/docs` como fuente

### Backend en Render

1. Conecta tu cuenta de Render con GitHub
2. Crea un nuevo Web Service y selecciona el repositorio
3. Configura las variables de entorno necesarias
4. Despliega la aplicación

## 🔧 Tecnologías utilizadas

- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Backend**: Python, Flask
- **Base de datos**: MongoDB Atlas
- **Almacenamiento**: Cloudinary/Firebase Storage
- **Hosting**: GitHub Pages, Render

## 📄 Estructura de archivos

```
/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .render.yaml
│   ├── uploads/
│   └── utils/
│       └── cloud_upload.py
└── README.md
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz fork del proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add amazing feature'`)
4. Sube los cambios a tu fork (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## ⚖️ Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 📞 Contacto

Para más información sobre este proyecto, contactar a través de GitHub.

---

Desarrollado con ❤️ para la comunidad de trabajadores internacionales en Croacia 🇭🇷