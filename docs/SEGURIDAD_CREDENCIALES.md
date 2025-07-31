# 🛡️ Guía de Seguridad - WorkWave Coast

## ⚠️ ACCIÓN INMEDIATA REQUERIDA

Las credenciales en el archivo `.env` están **EXPUESTAS** y deben ser **REGENERADAS INMEDIATAMENTE** antes del despliegue en producción.

## 🔑 Credenciales a Regenerar

### 1. MongoDB Atlas
- **Estado**: 🔴 COMPROMETIDA
- **Acción**: Regenerar password del usuario `alnsal`
- **URL**: https://cloud.mongodb.com/
- **Pasos**:
  1. Login en MongoDB Atlas
  2. Database Access → Users → Edit user `alnsal`
  3. Edit Password → Auto-generate secure password
  4. Update connection string en `.env`

### 2. Cloudinary
- **Estado**: 🔴 COMPROMETIDA
- **Acción**: Regenerar API Secret
- **URL**: https://console.cloudinary.com/
- **Pasos**:
  1. Login en Cloudinary
  2. Settings → Security → API Keys
  3. Regenerate API Secret
  4. Update `CLOUDINARY_API_SECRET` en `.env`

### 3. Application Secret Key
- **Estado**: 🔴 COMPROMETIDA
- **Acción**: Generar nueva clave
- **Comando**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Admin Credentials
- **Estado**: 🔴 COMPROMETIDAS
- **Acción**: Cambiar username y password
- **Recomendación**: Usar credenciales únicas y complejas

## 🚀 Despliegue Seguro en Producción

### Variables de Entorno en Render.com
```bash
# En el dashboard de Render.com:
MONGODB_URI=mongodb+srv://NEW_USER:NEW_PASSWORD@workwave.mxkpkgw.mongodb.net/?retryWrites=true&w=majority&appName=Workwave
CLOUDINARY_CLOUD_NAME=dde3kelit
CLOUDINARY_API_KEY=746326863757738
CLOUDINARY_API_SECRET=NEW_SECRET_HERE
SECRET_KEY=NEW_SECRET_KEY_HERE
ADMIN_USERNAME=NEW_ADMIN_USERNAME
ADMIN_PASSWORD=NEW_SECURE_PASSWORD
PORT=5000
```

### Variables de Entorno en Heroku
```bash
heroku config:set MONGODB_URI="mongodb+srv://NEW_USER:NEW_PASSWORD@..." --app your-app-name
heroku config:set CLOUDINARY_CLOUD_NAME="dde3kelit" --app your-app-name
heroku config:set CLOUDINARY_API_KEY="746326863757738" --app your-app-name
heroku config:set CLOUDINARY_API_SECRET="NEW_SECRET" --app your-app-name
heroku config:set SECRET_KEY="NEW_SECRET_KEY" --app your-app-name
heroku config:set ADMIN_USERNAME="NEW_USERNAME" --app your-app-name
heroku config:set ADMIN_PASSWORD="NEW_PASSWORD" --app your-app-name
```

## 📋 Checklist de Seguridad

- [ ] **URGENTE**: Regenerar password de MongoDB Atlas
- [ ] **URGENTE**: Regenerar API Secret de Cloudinary
- [ ] **URGENTE**: Generar nuevo SECRET_KEY
- [ ] **URGENTE**: Cambiar credenciales de admin
- [ ] Configurar variables de entorno en plataforma de hosting
- [ ] Verificar que `.env` está en `.gitignore`
- [ ] Eliminar archivo `.env` del repositorio local antes del commit
- [ ] Verificar que no hay credenciales hardcodeadas en el código
- [ ] Implementar rotación periódica de credenciales (cada 90 días)

## 🔄 Rotación de Credenciales (Mantenimiento)

### Frecuencia Recomendada:
- **MongoDB**: Cada 90 días
- **Cloudinary**: Cada 90 días
- **SECRET_KEY**: Cada 30 días en producción
- **Admin Credentials**: Cada 30 días

### Script de Validación:
```python
# validate_env.py - Verificar que todas las variables están presentes
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'MONGODB_URI', 'CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY',
    'CLOUDINARY_API_SECRET', 'SECRET_KEY', 'ADMIN_USERNAME', 'ADMIN_PASSWORD'
]

missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f"❌ Variables faltantes: {', '.join(missing)}")
    exit(1)
else:
    print("✅ Todas las variables de entorno están configuradas")
```

## 🚨 En Caso de Compromiso

1. **Immediately**: Regenerar TODAS las credenciales
2. **Verificar logs** de acceso en MongoDB Atlas y Cloudinary
3. **Revisar aplicaciones** enviadas en las últimas 24 horas
4. **Notificar al equipo** del incidente de seguridad
5. **Documentar** el incidente y las acciones tomadas

## 📞 Contactos de Emergencia

- **MongoDB Support**: https://support.mongodb.com/
- **Cloudinary Support**: https://support.cloudinary.com/
- **Render Support**: https://render.com/docs/support
