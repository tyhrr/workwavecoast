# Configuración de Email en Render

## ⚠️ IMPORTANTE: Variables de Entorno Faltantes en Render

Para que los emails de confirmación funcionen en producción, debes agregar estas variables de entorno en Render.

## 📝 Pasos para Configurar Email en Render:

### 1. Accede al Dashboard de Render
- Ve a: https://dashboard.render.com/
- Selecciona tu servicio: **workwavecoast-backend**

### 2. Ve a Environment Variables
- En el menú lateral, click en **"Environment"**
- Scroll hasta la sección **"Environment Variables"**

### 3. Agrega las Siguientes Variables

Haz click en **"Add Environment Variable"** para cada una:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=workwavecoast@gmail.com
MAIL_PASSWORD=yytedtvebaybwpbv
MAIL_DEFAULT_SENDER=workwavecoast@gmail.com
ADMIN_EMAIL=workwavecoast@gmail.com
```

### 4. Guarda y Redespliega
- Click en **"Save Changes"**
- Render redesplegará automáticamente el servicio
- Espera 2-3 minutos para que el despliegue complete

## ✅ Verificar que Funciona

Después de configurar las variables:

1. Envía una aplicación de prueba desde: https://workwavecoast.online
2. Deberías recibir un email de confirmación en el email que usaste
3. También se enviará una notificación a: workwavecoast@gmail.com

## 🔍 Variables Actuales en .env Local (NO SUBIR A GITHUB)

Tu archivo `.env` local ya tiene estas configuraciones:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=workwavecoast@gmail.com
MAIL_PASSWORD=yytedtvebaybwpbv
MAIL_DEFAULT_SENDER=workwavecoast@gmail.com
ADMIN_EMAIL=workwavecoast@gmail.com
```

## 📧 Formato del Email de Confirmación

Los candidatos recibirán un email con:

- ✅ Confirmación de recepción de aplicación
- 📅 Fecha y hora de envío
- 🔔 Información sobre próximos pasos
- 👥 Contacto de soporte
- 🎨 Diseño profesional en HTML

## 🚨 Troubleshooting

### Si los emails no llegan después de configurar:

1. **Verifica en Render Logs:**
   - Ve a "Logs" en el dashboard de Render
   - Busca mensajes como: `INFO - Service operation: send_confirmation_email`
   - Si ves errores, comparte el mensaje exacto

2. **Verifica la carpeta de SPAM:**
   - Los emails automáticos pueden caer en SPAM
   - Marca como "No es spam" si aparece ahí

3. **Verifica las credenciales de Gmail:**
   - La contraseña `yytedtvebaybwpbv` es una App Password de Gmail
   - Debe seguir siendo válida

4. **Prueba local:**
   ```bash
   cd backend
   python test_email.py
   ```
   - Esto enviará un email de prueba

## 📌 Notas Importantes

- ⚠️ **NUNCA** subas el archivo `.env` a GitHub
- ✅ Las variables en Render son seguras y encriptadas
- 🔄 Los cambios en Render requieren redespliegue automático
- 📧 Los emails se envían en segundo plano, no bloquean la aplicación

## 🎯 Siguiente Paso

**Acción requerida:** Ve a Render Dashboard y agrega las variables de entorno listadas arriba.

Después de configurar, prueba enviando una aplicación desde:
- https://workwavecoast.online
- Usa tu email personal: alangabrielsalva@gmail.com
- Deberías recibir el email de confirmación en 5-10 segundos
