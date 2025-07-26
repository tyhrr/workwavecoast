# Guía Paso a Paso: Conectar el Backend Flask con MongoDB Atlas y Firebase Storage

## 1. Conectar Flask con MongoDB Atlas

### 1.1. Crear una cuenta y cluster en MongoDB Atlas
- Ve a https://www.mongodb.com/cloud/atlas y crea una cuenta gratuita.
- Crea un nuevo cluster (elige el Free Tier).
- Crea una base de datos llamada `job_applications` y una colección llamada `candidates`.

### 1.2. Obtener la URI de conexión
- En el dashboard de Atlas, haz clic en "Connect" > "Connect your application".
- Copia la URI de tu base de datos (por ejemplo):
  ```
  mongodb+srv://alnsal:<db_password>@workwave.mxkpkgw.mongodb.net/?retryWrites=true&w=majority&appName=Workwave
  ```

### 1.3. Configurar variables de entorno en Flask
- Crea un archivo `.env` en la carpeta `/backend`:
  ```env
  MONGODB_URI=mongodb+srv://alnsal:E9A9LU6O1CEN5d0W@workwave.mxkpkgw.mongodb.net/?retryWrites=true&w=majority&appName=Workwave
  ```
- Reemplaza `<db_password>` por la contraseña real de tu usuario de base de datos.
- Antes de continuar, asegúrate de que el archivo `.env` esté listado en `.gitignore` para evitar subirlo al repositorio.

### 1.4. Instalar dependencias en el backend
```bash
pip install pymongo python-dotenv
```

### 1.5. Código de ejemplo para conectar y guardar datos
```python
from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
# Selecciona la base de datos y colección correctas
db = client['workwave']  # Nombre de tu base de datos en Atlas
candidates = db['candidates']

app = Flask(__name__)

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    # Agrega aquí la lógica para subir archivos y obtener URLs
    candidates.insert_one(data)
    return jsonify({'success': True})
```

---

## 2. Subir archivos a Firebase Storage desde Flask

### 2.1. Crear un proyecto en Firebase
- Ve a https://console.firebase.google.com/ y crea un nuevo proyecto.
- Habilita Firebase Storage en la consola.

### 2.2. Descargar credenciales de servicio
- En la configuración del proyecto, ve a "Cuentas de servicio" y descarga el archivo JSON de credenciales.
- Guarda este archivo en `/backend` y agrégalo a `.gitignore`.

### 2.3. Instalar dependencias
```bash
pip install google-cloud-storage
```

### 2.4. Código de ejemplo para subir archivos
```python
from google.cloud import storage
import os

# Inicializar cliente
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ruta/credenciales.json"
storage_client = storage.Client()
bucket = storage_client.bucket('nombre-del-bucket')

def upload_file_to_firebase(file_stream, filename):
    blob = bucket.blob(filename)
    blob.upload_from_file(file_stream)
    blob.make_public()
    return blob.public_url
```

### 2.5. Integrar con Flask
- Al recibir un archivo en el endpoint, llama a `upload_file_to_firebase()` y guarda la URL en MongoDB junto con el resto de los datos.

---

## 3. Consejos y buenas prácticas
- Nunca subas archivos de credenciales o `.env` a tu repositorio.
- Usa variables de entorno para todas las claves y URIs.
- Documenta en README y en este archivo cualquier cambio de configuración.
- Prueba la conexión a MongoDB y la subida a Firebase antes de lanzar a producción.

---

¿Dudas? Consulta la documentación oficial de [MongoDB Atlas](https://www.mongodb.com/docs/atlas/) y [Firebase Storage](https://firebase.google.com/docs/storage).
