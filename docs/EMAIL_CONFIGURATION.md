# Configuración de Email para WorkWave Coast

## Resumen
Esta guía explica cómo configurar el sistema de envío de emails de confirmación para los postulantes de WorkWave Coast.

## Configuración con Gmail

### 1. Preparar tu cuenta de Gmail

1. **Activar la verificación en 2 pasos:**
   - Ve a tu cuenta de Google
   - Seguridad → Verificación en 2 pasos
   - Actívala siguiendo las instrucciones

2. **Generar una contraseña de aplicación:**
   - En Seguridad → Contraseñas de aplicaciones
   - Selecciona "Correo" y tu dispositivo
   - Copia la contraseña generada (16 caracteres)

### 2. Variables de entorno

Agrega estas variables a tu archivo `.env`:

```env
# Configuración de Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=contraseña_de_aplicacion_16_caracteres
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

### 3. Configuración alternativa (Outlook/Hotmail)

```env
MAIL_SERVER=smtp.live.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=tu_email@outlook.com
MAIL_PASSWORD=tu_contraseña
MAIL_DEFAULT_SENDER=tu_email@outlook.com
```

## Características del Email

### Contenido del Email
- **Asunto:** "Confirmación de recepción de tu postulación"
- **Saludo personalizado** con el nombre del postulante
- **Mensaje de confirmación** de recepción
- **Sugerencias** para el postulante
- **Diseño responsive** con estilos CSS inline
- **Versión en texto plano** para compatibilidad

### Funcionalidades
- ✅ **HTML y texto plano:** Compatible con todos los clientes de email
- ✅ **Diseño responsive:** Se ve bien en móviles y desktop
- ✅ **Logging completo:** Registra éxitos y errores
- ✅ **Manejo de errores:** No afecta el envío del formulario si falla
- ✅ **Personalización:** Usa el nombre real del postulante

## Solución de Problemas

### Error: "Authentication failed"
- Verifica que hayas activado la verificación en 2 pasos
- Asegúrate de usar la contraseña de aplicación, no tu contraseña normal
- Comprueba que el username sea correcto

### Error: "Connection refused"
- Verifica la configuración del servidor SMTP
- Asegúrate de que el puerto sea correcto (587 para TLS)
- Comprueba que MAIL_USE_TLS=true

### Email no llega
- Revisa la carpeta de spam del destinatario
- Verifica que el email del postulante sea válido
- Consulta los logs de la aplicación para errores

### Limites de envío
- Gmail: ~500 emails/día para cuentas gratuitas
- Para mayor volumen, considera servicios como SendGrid, Mailgun, o Amazon SES

## Logs y Monitoreo

El sistema registra:
- ✅ Emails enviados exitosamente
- ❌ Errores de envío con detalles
- 📧 Email del destinatario (ofuscado en logs de producción)
- 👤 Nombre del postulante

Ejemplo de log exitoso:
```
INFO - Confirmation email sent successfully - recipient: juan@email.com - applicant_name: Juan García
```

## Desarrollo y Testing

Para testing local, puedes usar:
- **Mailtrap:** Servicio de testing de emails
- **Gmail personal:** Para pruebas reales
- **Logs:** El sistema registra si el email se envió o falló

## Producción

En producción (Render.com):
1. Configura las variables de entorno en el dashboard de Render
2. Usa una cuenta de email dedicada para la aplicación
3. Monitorea los logs para asegurar que los emails se envían correctamente
4. Considera implementar notificaciones si los emails fallan frecuentemente
