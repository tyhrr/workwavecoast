# Panel de Administración - WorkWave Coast

Panel de administración completo para gestionar las aplicaciones de candidatos.

## 📁 Estructura de Archivos

```
admin-panel/
├── login.html          # Página de inicio de sesión
├── dashboard.html      # Panel principal con lista de aplicaciones
├── styles.css          # Estilos CSS para todas las páginas
├── login.js           # Lógica de autenticación
├── dashboard.js       # Lógica del panel principal
└── README.md          # Este archivo
```

## 🚀 Características

### Página de Login (login.html)
- ✅ Formulario de autenticación seguro
- ✅ Validación de credenciales contra API backend
- ✅ Almacenamiento de tokens JWT
- ✅ Redirección automática si ya está autenticado

### Panel Principal (dashboard.html)
- ✅ **Estadísticas en tiempo real:**
  - Total de aplicaciones
  - Aplicaciones de hoy
  - Aplicaciones pendientes
  - Aplicaciones aprobadas

- ✅ **Filtros avanzados:**
  - Búsqueda por nombre, email o teléfono
  - Filtro por estado (pendiente, aprobada, rechazada)
  - Filtro por puesto de trabajo

- ✅ **Gestión de aplicaciones:**
  - Ver detalles completos de cada aplicación
  - Aprobar/rechazar aplicaciones
  - Acceso a archivos adjuntos (CV, carta de presentación, etc.)
  - Exportar a CSV

- ✅ **Diseño responsivo:**
  - Optimizado para desktop, tablet y móvil
  - Interfaz moderna y amigable

## 🔧 Configuración

### 1. URL de la API

En `login.js` y `dashboard.js`, la URL de la API se configura automáticamente:

```javascript
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : 'https://workwavecoast-backend.onrender.com';
```

Si tu backend está en otra URL, modifica la línea en ambos archivos.

### 2. Credenciales de Admin

Las credenciales se configuran en el backend mediante variables de entorno:
- `ADMIN_USERNAME` (por defecto: "admin")
- `ADMIN_PASSWORD` (por defecto: "workwave2025")

## 📖 Uso

### Para Desarrollo Local

1. Asegúrate de que el backend esté corriendo en `http://localhost:5000`
2. Abre `login.html` en tu navegador
3. Inicia sesión con las credenciales de admin
4. Serás redirigido al dashboard

### Para Producción

1. Sube los archivos a tu servidor web o CDN
2. Asegúrate de que la URL del backend esté correctamente configurada
3. Accede a través de tu dominio (ej: `https://workwavecoast.online/admin-panel/login.html`)

## 🔐 Seguridad

- ✅ Autenticación JWT con tokens de acceso y refresh
- ✅ Verificación automática de tokens expirados
- ✅ Redirección a login si no está autenticado
- ✅ Cierre de sesión seguro que limpia el almacenamiento local

## 🎨 Personalización

### Colores
Los colores principales se pueden modificar en `styles.css`:
- Primary: `#667eea` (azul púrpura)
- Success: `#28a745` (verde)
- Danger: `#dc3545` (rojo)
- Warning: `#ffc107` (amarillo)

### Logos
El emoji 🏖️ puede ser reemplazado por un logo real en ambos archivos HTML.

## 📱 Compatibilidad

- ✅ Chrome/Edge (últimas 2 versiones)
- ✅ Firefox (últimas 2 versiones)
- ✅ Safari (últimas 2 versiones)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🐛 Troubleshooting

### Error: "Error al cargar aplicaciones"
- Verifica que el backend esté corriendo
- Verifica la URL del API en los archivos JS
- Verifica la consola del navegador para más detalles

### No puedo iniciar sesión
- Verifica las credenciales
- Verifica que el backend tenga configuradas las credenciales correctas
- Verifica la consola del navegador para errores de CORS

### Los archivos no se descargan
- Verifica que Cloudinary esté configurado correctamente en el backend
- Verifica que las URLs de los archivos sean accesibles

## 🔄 Próximas Mejoras

- [ ] Paginación para listas largas
- [ ] Edición de aplicaciones
- [ ] Búsqueda avanzada con múltiples criterios
- [ ] Notificaciones en tiempo real
- [ ] Análisis y reportes avanzados
- [ ] Gestión de múltiples administradores

## 📞 Soporte

Para problemas o preguntas, contacta al equipo de desarrollo.
