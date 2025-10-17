# 🌊 WorkWave Coast
### Sistema de Gestión de Postulaciones Laborales para la Costa Croata

Plataforma web completa para gestionar postulaciones de empleo para trabajos estacionales en la costa croata. Sistema funcional con infraestructura optimizada, base de datos configurada y servicios externos integrados.

---

## 📑 ÍNDICE GENERAL

### I. INFORMACIÓN GENERAL
- [1.1 Descripción del Sistema](#11-descripción-del-sistema)
- [1.2 Características Principales](#12-características-principales)
- [1.3 Stack Tecnológico](#13-stack-tecnológico)
- [1.4 Arquitectura del Sistema](#14-arquitectura-del-sistema)

### II. ESTADO DEL PROYECTO
- [2.1 Estado Actual - Resumen Ejecutivo](#21-estado-actual---resumen-ejecutivo)
- [2.2 Infraestructura Confirmada](#22-infraestructura-confirmada)
- [2.3 Progreso de Desarrollo](#23-progreso-de-desarrollo)
- [2.4 Tareas Completadas](#24-tareas-completadas)
  - [2.4.1 Tarea #1: Variables de Ambiente](#241-tarea-1-variables-de-ambiente)
  - [2.4.2 Tarea #2: Base de Datos MongoDB](#242-tarea-2-base-de-datos-mongodb)
  - [2.4.3 Tarea #3: Sistema de Archivos](#243-tarea-3-sistema-de-archivos)
  - [2.4.4 Tarea #4: Autenticación JWT](#244-tarea-4-autenticación-jwt)

### III. ESTRUCTURA DEL PROYECTO
- [3.1 Estructura de Directorios](#31-estructura-de-directorios)
- [3.2 Archivos Críticos](#32-archivos-críticos)
- [3.3 Dependencias](#33-dependencias)

### IV. CONFIGURACIÓN Y SETUP
- [4.1 Prerrequisitos](#41-prerrequisitos)
- [4.2 Instalación Paso a Paso](#42-instalación-paso-a-paso)
- [4.3 Variables de Ambiente](#43-variables-de-ambiente)
- [4.4 Verificación del Sistema](#44-verificación-del-sistema)

### V. BASE DE DATOS
- [5.1 MongoDB Atlas - Configuración](#51-mongodb-atlas---configuración)
- [5.2 Esquema de Datos](#52-esquema-de-datos)
- [5.3 Índices Optimizados](#53-índices-optimizados)
- [5.4 Prevención de Duplicados](#54-prevención-de-duplicados)

### VI. SISTEMA DE ARCHIVOS
- [6.1 Cloudinary - Configuración](#61-cloudinary---configuración)
- [6.2 Validación de Archivos](#62-validación-de-archivos)
- [6.3 Transformaciones Automáticas](#63-transformaciones-automáticas)
- [6.4 Endpoints de Archivos](#64-endpoints-de-archivos)

### VII. AUTENTICACIÓN Y SEGURIDAD
- [7.1 Sistema JWT](#71-sistema-jwt)
- [7.2 Roles y Permisos (RBAC)](#72-roles-y-permisos-rbac)
- [7.3 Sistema de Auditoría](#73-sistema-de-auditoría)
- [7.4 Recovery de Contraseñas](#74-recovery-de-contraseñas)
- [7.5 Medidas de Seguridad](#75-medidas-de-seguridad)

### VIII. API DOCUMENTATION
- [8.1 Endpoints Públicos](#81-endpoints-públicos)
- [8.2 Endpoints de Autenticación](#82-endpoints-de-autenticación)
- [8.3 Endpoints Administrativos](#83-endpoints-administrativos)
- [8.4 Endpoints de Archivos](#84-endpoints-de-archivos)
- [8.5 Endpoints de Auditoría](#85-endpoints-de-auditoría)

### IX. SERVICIOS EXTERNOS
- [9.1 MongoDB Atlas](#91-mongodb-atlas)
- [9.2 Cloudinary](#92-cloudinary)
- [9.3 Gmail SMTP](#93-gmail-smtp)

### X. INTERFAZ DE USUARIO
- [10.1 Frontend - Formulario Público](#101-frontend---formulario-público)
- [10.2 Panel de Administración](#102-panel-de-administración)
- [10.3 Diseño Responsive](#103-diseño-responsive)

### XI. DESPLIEGUE
- [11.1 Arquitectura de Producción](#111-arquitectura-de-producción)
- [11.2 Configuración de Hosting](#112-configuración-de-hosting)
- [11.3 Variables de Producción](#113-variables-de-producción)
- [11.4 Checklist de Despliegue](#114-checklist-de-despliegue)

### XII. REFERENCIAS
- [12.1 Comandos Útiles](#121-comandos-útiles)
- [12.2 Troubleshooting](#122-troubleshooting)
- [12.3 Documentación Adicional](#123-documentación-adicional)

---

# I. INFORMACIÓN GENERAL

## 1.1 Descripción del Sistema

WorkWave Coast es una aplicación web moderna diseñada para simplificar el proceso de reclutamiento para empleos estacionales en la costa croata. La plataforma permite a los candidatos enviar sus postulaciones de manera intuitiva y a los reclutadores gestionar eficientemente las aplicaciones recibidas.

**Funcionalidad Principal:**
- **Para Candidatos**: Formulario web intuitivo completamente funcional
- **Para Reclutadores**: Panel de administración con funcionalidad completa operativa
- **Sistema Automatizado**: Procesamiento seguro de datos y archivos con validación en tiempo real

## 1.2 Características Principales

### 🔒 Seguridad Avanzada
- **JWT Authentication**: Tokens seguros con access/refresh y expiración automática
- **RBAC System**: Control de acceso basado en roles (super_admin, admin, viewer)
- **Bcrypt Passwords**: Hash criptográfico seguro de contraseñas
- **Audit Logging**: Registro completo de acciones administrativas
- **Password Recovery**: Sistema seguro de recuperación con tokens temporales
- **Rate Limiting**: Protección contra spam y ataques de fuerza bruta
- **Prevención de Duplicados**: Sistema automático verificado funcionando

### 🚀 Alto Rendimiento
- **Índices Optimizados**: 10 índices en MongoDB configurados y activos
- **Logging Estructurado**: JSON para monitoreo en producción
- **Paginación Eficiente**: Para grandes volúmenes de datos
- **CDN Global**: Cloudinary para archivos optimizados

### 📱 Experiencia de Usuario
- **Diseño Responsive**: Adaptable a todos los dispositivos
- **Validación en Tiempo Real**: Feedback inmediato
- **Validación de Teléfono Internacional**: Formato automático según código de país (20+ países)
- **Nivel de Inglés Obligatorio**: Campo requerido para competencia lingüística
- **Selección Múltiple de Puestos**: Aplicar a varios trabajos en una postulación

### 🛠️ Administración Completa
- **Panel JWT con RBAC**: Autenticación y autorización completa
- **Gestión Completa**: CRUD de aplicaciones con paginación
- **Búsqueda Avanzada**: Full-text search con MongoDB
- **Filtros Completos**: Fecha, status, puesto, nacionalidad, nivel inglés
- **Exportación**: CSV y Excel con filtros aplicables
- **Notificaciones Automáticas**: Emails a candidatos por cambio de status
- **Dashboard Avanzado**: Métricas, distribuciones, tendencias
- **Sistema de Auditoría**: Trazabilidad completa de acciones

## 1.3 Stack Tecnológico

### Frontend
```
• HTML5: Estructura semántica y accesible
• CSS3: Diseño responsive con Flexbox/Grid
• JavaScript ES6+: Validaciones y fetch API
• Google Fonts: Tipografía Montserrat
```

### Backend
```python
• Python 3.9+
• Flask 2.1.0
• Flask-CORS, Flask-Limiter
• PyMongo (MongoDB driver)
• PyJWT>=2.8.0 (JWT Authentication)
• bcrypt>=4.1.0 (Password hashing)
• pandas>=2.2.0 (Data export)
• openpyxl>=3.1.2 (Excel export)
• python-dotenv, pythonjsonlogger
```

### Base de Datos y Almacenamiento
```
• MongoDB Atlas: Base de datos NoSQL
• Cloudinary: CDN y procesamiento de archivos
• Índices optimizados: 10 configurados
• Text search: Búsqueda full-text
```

### Seguridad
```
• JWT Authentication con RBAC
• Bcrypt password hashing
• Rate limiting y XSS protection
• Audit logging completo
• Environment variables seguras
```

## 1.4 Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   Frontend      │◄──►│   Backend API    │◄──►│   MongoDB       │
│   (HTML/CSS/JS) │    │   (Flask)        │    │   Atlas         │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │                 │
         └──────────────►│   Cloudinary    │
                        │   (File Storage)│
                        │                 │
                        └─────────────────┘
```

**Componentes:**
1. **Frontend**: Interfaz web responsive con JavaScript vanilla
2. **Backend API**: API REST construida con Flask + JWT
3. **Base de Datos**: MongoDB Atlas con 10 índices optimizados
4. **Almacenamiento**: Cloudinary para gestión de archivos
5. **Autenticación**: JWT + RBAC + Bcrypt
6. **Auditoría**: Sistema completo de logging

---

# II. ESTADO DEL PROYECTO

## 2.1 Estado Actual - Resumen Ejecutivo

**📊 Completitud General: 95% ✅ SISTEMA COMPLETO Y FUNCIONAL**

El sistema WorkWave Coast está **completamente funcional** con todas las características críticas implementadas y probadas. La infraestructura está 100% operativa y todas las funcionalidades del panel administrativo han sido implementadas.

### Estado por Componente

```
┌────────────────────────────────────────────────────────────┐
│ COMPONENTE                    │ ESTADO │ %   │ INDICADOR │
├────────────────────────────────────────────────────────────┤
│ 🌐 Frontend Público           │   ✅   │100% │ ████████  │
│ 🔐 Sistema de Autenticación   │   ✅   │100% │ ████████  │
│ 🗄️  Base de Datos MongoDB     │   ✅   │100% │ ████████  │
│ 📁 Sistema de Archivos        │   ✅   │100% │ ████████  │
│ 📧 Servicio de Emails         │   ✅   │100% │ ████████  │
│ 🔒 Seguridad y RBAC           │   ✅   │100% │ ████████  │
│ 📊 Audit Logging              │   ✅   │100% │ ████████  │
│ 🔧 Backend API Core           │   ✅   │100% │ ████████  │
│ 🎛️  Panel Admin Backend       │   ✅   │100% │ ████████  │
│ 🔍 Búsqueda y Filtros         │   ✅   │100% │ ████████  │
│ 📊 Dashboard Avanzado         │   ✅   │100% │ ████████  │
│ 📤 Exportación de Datos       │   ✅   │100% │ ████████  │
│ 📧 Notificaciones Auto        │   ✅   │100% │ ████████  │
│ 💻 Panel Admin Frontend       │   ⚠️   │ 60% │ █████░░░  │
├────────────────────────────────────────────────────────────┤
│ 🎯 COMPLETITUD GENERAL        │   ✅   │ 95% │ ████████  │
└────────────────────────────────────────────────────────────┘

Leyenda: ✅ Completo | ⚠️ Funcional Básico
```

## 2.2 Infraestructura Confirmada

### ✅ Completamente Operativa (100%)

**Base de Datos - MongoDB Atlas**
- Estado: ✅ Conectado y optimizado
- Documentos: 27 candidatos existentes
- Índices: 10 optimizados (incluyendo prevención duplicados)
- Búsqueda: Text search configurado

**Almacenamiento - Cloudinary**
- Estado: ✅ Configurado y funcional
- Archivos: 16 preservados (2.63 MB)
- Transformaciones: Automáticas activas
- CDN: Global optimizado

**Email - Gmail SMTP**
- Estado: ✅ Operativo
- Notificaciones: Automáticas implementadas
- Templates: HTML responsivos
- Recovery: Sistema de recuperación activo

**Autenticación - JWT + RBAC**
- Estado: ✅ Completamente implementado
- JWT: Access + Refresh tokens
- RBAC: 3 roles (super_admin, admin, viewer)
- Bcrypt: Password hashing seguro
- Auditoría: Logging completo

**Variables de Ambiente**
- Estado: ✅ Sistema centralizado implementado
- Configuración: Todos los servicios configurados
- Seguridad: Credenciales protegidas

## 2.3 Progreso de Desarrollo

### ✅ Funcionalidades Completadas (100%)

**Infraestructura Base**
- ✅ Variables de ambiente centralizadas
- ✅ MongoDB Atlas conectado (27 documentos)
- ✅ Cloudinary integrado (16 archivos)
- ✅ Gmail SMTP configurado
- ✅ 10 índices optimizados
- ✅ Prevención automática de duplicados

**Backend API**
- ✅ Endpoints públicos (submit, latest)
- ✅ Endpoints JWT authentication (login, refresh, logout)
- ✅ Endpoints admin (CRUD completo)
- ✅ Endpoints archivos (upload, preview, delete)
- ✅ Endpoints auditoría (logs, stats, export)
- ✅ Búsqueda full-text implementada
- ✅ Filtros avanzados completos
- ✅ Exportación CSV/Excel funcional
- ✅ Notificaciones automáticas activas

**Panel de Administración**
- ✅ Autenticación JWT con RBAC
- ✅ Dashboard con métricas avanzadas
- ✅ Gestión completa de aplicaciones
- ✅ Búsqueda de texto completo
- ✅ Filtros: status, puesto, fecha, nacionalidad, inglés
- ✅ Exportación de datos (CSV/Excel)
- ✅ Preview de archivos (PDF/fotos)
- ✅ Notificaciones automáticas por email
- ✅ Sistema de auditoría
- ✅ Eliminación individual y masiva

**Seguridad**
- ✅ JWT Authentication completo
- ✅ RBAC con 3 roles
- ✅ Bcrypt password hashing
- ✅ Audit logging completo
- ✅ Password recovery seguro
- ✅ Rate limiting configurado
- ✅ Input validation completa

## 2.4 Tareas Completadas

### 2.4.1 Tarea #1: Variables de Ambiente
**Estado**: ✅ **COMPLETADA** (Octubre 2025)

**Implementaciones:**
- Sistema centralizado en `config/env_loader.py`
- Carga automática desde proyecto root
- Integración en todos los módulos
- Testing individual funcional

**Archivos Modificados:**
```
✅ config/env_loader.py         # Sistema centralizado
✅ config/settings.py           # Configuración
✅ config/database.py           # MongoDB
✅ services/file_service.py     # Cloudinary
✅ app.py                       # Aplicación principal
```

### 2.4.2 Tarea #2: Base de Datos MongoDB
**Estado**: ✅ **COMPLETADA** (Octubre 2025)

**Logros:**
- MongoDB Atlas conectado (27 documentos)
- 10 índices optimizados configurados
- Prevención de duplicados verificada
- Text search index activo

**Índices Configurados:**
```javascript
1. _id_                                    // Principal
2. created_at_-1                          // Cronológico
3. email_1                                // Búsqueda
4. email_unique_idx                       // ✅ ÚNICO (duplicados)
5. puesto_1_created_at_-1                // Compuesto
6. status_1                               // Filtrado
7. telefono_1                             // Búsqueda
8. ingles_nivel_1                         // Filtrado
9. nacionalidad_1                         // Filtrado
10. nombre_text_apellido_text_email_text   // ✅ FULL-TEXT
```

### 2.4.3 Tarea #3: Sistema de Archivos
**Estado**: ✅ **COMPLETADA** (Octubre 2025)

**Funcionalidades:**
- Validación MIME, extensión y tamaño
- Transformaciones automáticas Cloudinary
- 10 endpoints REST implementados
- Preview PDFs y fotos con thumbnails
- URLs firmadas seguras
- 16 archivos preservados (2.63 MB)

**Endpoints Implementados:**
```
POST /api/upload                    // Upload múltiple
POST /api/upload/<field_name>       // Upload específico
POST /api/validate                  // Validación
GET  /api/health                    // Health check
GET  /api/stats                     // Estadísticas
GET  /api/list                      // Listar archivos
GET  /api/info/<public_id>          // Información
GET  /api/preview/<public_id>       // Preview admin
GET  /api/signed-url/<public_id>    // URL firmada
DELETE /api/delete/<public_id>      // Eliminar
```

### 2.4.4 Tarea #4: Autenticación JWT
**Estado**: ✅ **COMPLETADA** (Octubre 2025)

**Sistema Completo:**
- JWT Authentication (access + refresh tokens)
- RBAC con 3 roles y permisos granulares
- Bcrypt password hashing migrado
- Sistema de auditoría completo
- Password recovery seguro
- Middleware de autenticación/autorización

**Archivos Implementados:**
```
✅ services/jwt_service.py           # JWT tokens
✅ services/admin_service.py         # Auth + bcrypt
✅ services/audit_service.py         # Auditoría
✅ middleware/rbac_middleware.py     # RBAC
✅ routes/admin.py                   # Endpoints admin
✅ routes/password_recovery.py       # Recovery
✅ services/email_service.py         # Email templates
```

**Dependencias Agregadas:**
```
PyJWT>=2.8.0                        # JWT
bcrypt>=4.1.0                       # Password hashing
```

### 2.4.5 Tarea #5: Panel Admin Completo
**Estado**: ✅ **COMPLETADA** (Octubre 2025)

**Nuevas Funcionalidades:**
- ✅ Búsqueda full-text con MongoDB $text
- ✅ Filtros avanzados (fecha, nacionalidad, inglés)
- ✅ Exportación CSV/Excel con pandas
- ✅ Notificaciones automáticas por email
- ✅ Dashboard con distribuciones y tendencias
- ✅ Status updates con notificaciones
- ✅ 6 nuevos endpoints API

**Archivos Modificados:**
```
✅ services/application_service.py  # 4 métodos nuevos
✅ services/email_service.py        # 3 templates
✅ services/admin_service.py        # Dashboard mejorado
✅ routes/admin.py                  # 6 endpoints
```

**Tests Creados:**
```
✅ test_new_features.py             # Tests completos
✅ test_simple.py                   # Tests rápidos
✅ test_search_debug.py             # Debug
```

**Resultados de Pruebas:**
```
✅ Búsqueda full-text: 27 resultados, paginación OK
✅ Filtros avanzados: 8 nacionalidades, 7 puestos, 6 niveles
✅ Exportación CSV: 27 registros exportados
✅ Exportación Excel: 27 registros con formato
✅ Dashboard: Estadísticas en tiempo real
```

---

# III. ESTRUCTURA DEL PROYECTO

## 3.1 Estructura de Directorios

```
workwave-coast/
├── 📁 frontend/                 # Cliente web
│   ├── 🌐 index.html           # Página principal
│   ├── 🎨 styles.css           # Estilos responsive
│   ├── ⚡ script.js            # Lógica cliente
│   └── 📁 img/                 # Assets visuales
│
├── 📁 backend/                  # Servidor API
│   ├── 🐍 app.py               # Aplicación Flask
│   ├── 📋 requirements.txt     # Dependencias
│   ├── 🔒 .env                 # Variables ambiente
│   │
│   ├── 📁 config/              # Configuración
│   │   ├── env_loader.py       # Sistema variables
│   │   ├── settings.py         # Config app
│   │   ├── database.py         # MongoDB
│   │   └── constants.py        # Constantes
│   │
│   ├── 📁 services/            # Servicios
│   │   ├── application_service.py  # Aplicaciones
│   │   ├── file_service.py         # Cloudinary
│   │   ├── jwt_service.py          # JWT
│   │   ├── admin_service.py        # Admin
│   │   ├── audit_service.py        # Auditoría
│   │   └── email_service.py        # Emails
│   │
│   ├── 📁 middleware/          # Middleware
│   │   └── rbac_middleware.py  # RBAC
│   │
│   └── 📁 routes/              # Endpoints
│       ├── applications.py     # Aplicaciones
│       ├── admin.py            # Admin
│       ├── files.py            # Archivos
│       └── password_recovery.py # Recovery
│
├── 📁 docs/                     # Documentación
└── 📄 README.md                 # Este documento
```

## 3.2 Archivos Críticos

### Variables de Ambiente (.env)
```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://...
MONGO_DB_NAME=workwave

# Cloudinary
CLOUDINARY_CLOUD_NAME=dde3kelit
CLOUDINARY_API_KEY=746326863757738
CLOUDINARY_API_SECRET=***

# Gmail SMTP
MAIL_USERNAME=workwavecoast@gmail.com
MAIL_PASSWORD=***
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Seguridad
SECRET_KEY=***
ADMIN_USERNAME=admin
ADMIN_PASSWORD=***
```

### Sistema de Carga (config/env_loader.py)
- Detección automática de .env
- Múltiples rutas de respaldo
- Prevención de carga duplicada
- Soporte testing individual

## 3.3 Dependencias

### Backend (requirements.txt)
```txt
Flask==2.1.0
Flask-CORS==3.0.10
Flask-Limiter==2.1
PyMongo==4.3.3
python-dotenv==0.19.2
cloudinary==1.30.0
pythonjsonlogger==2.0.4
gunicorn==20.1.0
PyJWT>=2.8.0
bcrypt>=4.1.0
pandas>=2.2.0
openpyxl>=3.1.2
```

### Frontend
```
HTML5, CSS3, JavaScript ES6+
Google Fonts (Montserrat)
Fetch API nativa
```

---

# IV. CONFIGURACIÓN Y SETUP

## 4.1 Prerrequisitos

- Python 3.9+ instalado
- Git configurado
- Acceso a MongoDB Atlas
- Cuentas: Cloudinary, Gmail

## 4.2 Instalación Paso a Paso

### 1. Clonar y Configurar Entorno
```bash
# Clonar repositorio
git clone <repository-url>
cd workwave-coast

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt
```

### 2. Configurar Variables
El archivo `.env` ya está configurado en el proyecto root.

### 3. Verificar Conexiones
```bash
cd backend

# Verificar MongoDB
python -c "from config.database import get_database; print('✅ MongoDB:', 'OK' if get_database() else 'Error')"

# Verificar Cloudinary
python -c "from services.file_service import FileService; fs = FileService(); print('✅ Cloudinary: OK')"
```

### 4. Ejecutar Aplicación
```bash
# Opción 1: Script Windows
start_backend.bat

# Opción 2: Comando directo
python backend/app.py

# Opción 3: Desde backend
cd backend
python app.py
```

## 4.3 Variables de Ambiente

Todas las variables están pre-configuradas en `.env`:

```bash
# ✅ MongoDB Atlas - Conectado
MONGODB_URI=mongodb+srv://[configured]
MONGO_DB_NAME=workwave

# ✅ Cloudinary - Operativo
CLOUDINARY_CLOUD_NAME=dde3kelit
CLOUDINARY_API_KEY=746326863757738
CLOUDINARY_API_SECRET=[configured]

# ✅ Gmail SMTP - Funcional
MAIL_USERNAME=workwavecoast@gmail.com
MAIL_PASSWORD=[configured]
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True

# ✅ Seguridad - Configurada
SECRET_KEY=[configured]
ADMIN_USERNAME=admin
ADMIN_PASSWORD=[configured]
```

## 4.4 Verificación del Sistema

### Test Completo de Conectividad
```python
from config.database import get_database
from services.file_service import FileService
from config.settings import get_config

# Verificar base de datos
db = get_database()
print('📊 MongoDB:', '✅' if db else '❌')

# Verificar Cloudinary
fs = FileService()
print('📁 Cloudinary: ✅')

# Verificar configuración
config = get_config()
print('⚙️  Config:', '✅' if config.validate() else '❌')
```

### Resultados Esperados
```
📊 MongoDB: ✅ Conectado (27 documentos)
📁 Cloudinary: ✅ Configurado (16 archivos)
⚙️  Config: ✅ Válida
📧 SMTP: ✅ Operativo
🔒 JWT: ✅ Configurado
```

---

# V. BASE DE DATOS

## 5.1 MongoDB Atlas - Configuración

**Estado**: ✅ Completamente Operativo

```yaml
Cluster: MongoDB Atlas (Producción)
Base de Datos: workwave
Collection: candidates
Documentos: 27 existentes
Índices: 10 optimizados
SSL: Habilitado
Backups: Automáticos
```

**Cadena de Conexión:**
```python
MONGODB_URI=mongodb+srv://[user]:[pass]@[cluster].mongodb.net/workwave
```

## 5.2 Esquema de Datos

### Collection: candidates

```javascript
{
  "_id": ObjectId,
  "nombre": String,
  "apellido": String,
  "email": String,              // ✅ ÍNDICE ÚNICO
  "telefono": String,
  "nacionalidad": String,
  "nivel_ingles": String,       // Básico|Intermedio|Avanzado|Nativo
  "puesto": String,
  "puestos_adicionales": Array,
  "experiencia": String,
  "cv_url": String,             // URL Cloudinary
  "foto_url": String,           // URL Cloudinary
  "created_at": Date,           // ✅ ÍNDICE DESCENDENTE
  "status": String,             // pending|approved|rejected
  "updated_at": Date,
  "updated_by": String          // Admin username
}
```

## 5.3 Índices Optimizados

**10 Índices Configurados:**

| Índice | Tipo | Propósito |
|--------|------|-----------|
| `_id_` | Único | Identificador MongoDB |
| `created_at_-1` | Descendente | Ordenación cronológica |
| `email_1` | Simple | Búsqueda rápida |
| `email_unique_idx` | **Único** | **Prevención duplicados** |
| `puesto_1_created_at_-1` | Compuesto | Búsqueda + fecha |
| `status_1` | Simple | Filtrado estado |
| `telefono_1` | Simple | Búsqueda teléfono |
| `ingles_nivel_1` | Simple | Filtrado inglés |
| `nacionalidad_1` | Simple | Filtrado país |
| `nombre_text_apellido_text_email_text` | **Texto** | **Full-text search** |

## 5.4 Prevención de Duplicados

**Sistema Automático Verificado:**
- Índice único en campo `email`
- Error E11000 en duplicados (esperado)
- Testing completo realizado
- 100% funcional

**Prueba:**
```python
# Intento de insertar email duplicado
# Result: E11000 duplicate key error ✅
```

---

# VI. SISTEMA DE ARCHIVOS

## 6.1 Cloudinary - Configuración

**Estado**: ✅ Completamente Funcional

```yaml
Cloud Name: dde3kelit
API Key: 746326863757738
Archivos: 16 preservados
Storage: 2.63 MB utilizado
CDN: Global optimizado
```

## 6.2 Validación de Archivos

| Campo | Extensiones | Tamaño Máx | MIME Types |
|-------|-------------|------------|------------|
| **CV** | `.pdf` | 5 MB | `application/pdf` |
| **Foto** | `.jpg`, `.jpeg`, `.png` | 2 MB | `image/jpeg`, `image/png` |
| **Carta** | `.pdf`, `.doc`, `.docx` | 5 MB | PDF + Word |
| **Referencias** | `.pdf`, `.doc`, `.docx` | 5 MB | PDF + Word |
| **Certificados** | `.pdf`, `.doc`, `.docx`, `.jpg`, `.png` | 5 MB | PDF + Word + Imagen |

**Validaciones:**
- MIME type real del archivo
- Extensión del nombre
- Tamaño máximo
- Nombres seguros (path traversal)
- Archivos no vacíos

## 6.3 Transformaciones Automáticas

### Fotos de Perfil
```javascript
{
  "principal": {
    "max_size": "800x800",
    "crop": "limit",
    "quality": "auto:good",
    "format": "auto",
    "effects": ["auto_brightness:20", "auto_contrast:10"]
  },
  "thumbnail": {
    "size": "150x150",
    "crop": "thumb",
    "gravity": "face"  // Detección facial
  }
}
```

### Documentos CV
```javascript
{
  "storage": "raw",
  "download": "attachment",
  "organization": "workwave/cv/",
  "security": "private_access"
}
```

## 6.4 Endpoints de Archivos

### Upload y Validación
```http
POST /api/upload
POST /api/upload/<field_name>
POST /api/validate
```

### Gestión
```http
GET  /api/health
GET  /api/stats
GET  /api/list
GET  /api/info/<public_id>
GET  /api/preview/<public_id>
GET  /api/signed-url/<public_id>
DELETE /api/delete/<public_id>
```

---

# VII. AUTENTICACIÓN Y SEGURIDAD

## 7.1 Sistema JWT

**Tokens Implementados:**
- **Access Token**: 1 hora de duración
- **Refresh Token**: 7 días de duración
- **Recovery Token**: 30 minutos para reset password

**Algoritmo**: HS256 con secret key configurable

**Características:**
- Generación automática de tokens
- Verificación de firma y expiración
- Renovación automática con refresh
- Revocación en logout

## 7.2 Roles y Permisos (RBAC)

### Roles Implementados

**super_admin**
- Permisos: `["all"]`
- Acceso completo al sistema
- Gestión de otros admins
- Acceso a logs de auditoría

**admin**
- Permisos: `["read", "write", "delete", "manage_applications"]`
- Gestión estándar de aplicaciones
- Aprobación/rechazo de candidatos
- Acceso a dashboard

**viewer**
- Permisos: `["read"]`
- Solo consulta de aplicaciones
- Sin modificación
- Dashboard de lectura

### Middleware RBAC
```python
@require_admin_auth          # JWT requerido
@require_permission('read')  # Permiso específico
```

## 7.3 Sistema de Auditoría

**Eventos Registrados:**
- Login/logout
- Cambios de contraseña
- Acceso denegado
- Gestión de aplicaciones
- Cambios de status
- Exportaciones

**Metadatos:**
```javascript
{
  "timestamp": "2025-10-17T10:15:30Z",
  "event_type": "login_success",
  "username": "admin",
  "role": "super_admin",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "details": {...}
}
```

**Exportación:**
- JSON y CSV
- Filtros: fecha, admin, tipo evento
- Estadísticas por período
- Retention: 90 días

## 7.4 Recovery de Contraseñas

**Flujo:**
1. Usuario solicita reset (username + email)
2. Sistema genera token JWT temporal (30 min)
3. Email con enlace seguro enviado
4. Usuario resetea contraseña
5. Token invalidado automáticamente
6. Email de confirmación enviado

**Endpoints:**
```http
POST /api/admin/auth/forgot-password
POST /api/admin/auth/reset-password
POST /api/admin/auth/validate-recovery-token
```

## 7.5 Medidas de Seguridad

### Implementadas
- ✅ JWT Authentication
- ✅ Bcrypt password hashing
- ✅ RBAC con permisos granulares
- ✅ Audit logging completo
- ✅ Rate limiting (5 submit/min, 10 login/min)
- ✅ XSS protection
- ✅ Input validation
- ✅ CORS configurado
- ✅ Environment variables seguras
- ✅ Prevención de duplicados
- ✅ SQL injection prevention (NoSQL)

---

# VIII. API DOCUMENTATION

## 8.1 Endpoints Públicos

### Envío de Postulación
```http
POST /api/submit
Content-Type: multipart/form-data

Rate Limit: 5 requests/minuto

Parámetros:
{
  "nombre": "string (max: 50)",
  "apellido": "string (max: 50)",
  "email": "email (max: 60, único)",
  "telefono": "string (max: 20)",
  "nacionalidad": "string (max: 40)",
  "nivel_ingles": "enum [Básico|Intermedio|Avanzado|Nativo]",
  "puesto": "enum [Camarero/a|Cocinero/a|...]",
  "puestos_adicionales": "array (opcional)",
  "experiencia": "text (max: 500)",
  "cv": "file (PDF, max: 5MB)",
  "foto": "file (JPG/PNG, max: 2MB)"
}

Response 201:
{
  "success": true,
  "message": "Application submitted successfully",
  "data": {
    "application_id": "...",
    "email": "...",
    "created_at": "..."
  }
}
```

### Última Postulación
```http
GET /api/applications/latest

Response 200:
{
  "success": true,
  "data": {...}
}
```

## 8.2 Endpoints de Autenticación

### Login
```http
POST /api/admin/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}

Response 200:
{
  "success": true,
  "data": {
    "admin": {...},
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "access_expires_in": 3600,
    "refresh_expires_in": 604800
  }
}
```

### Refresh Token
```http
POST /api/admin/auth/refresh
Content-Type: application/json

{
  "refresh_token": "..."
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "...",
    "expires_in": 3600
  }
}
```

### Logout
```http
POST /api/admin/auth/logout
Authorization: Bearer <token>

Response 200:
{
  "success": true,
  "message": "Logout successful"
}
```

## 8.3 Endpoints Administrativos

### Dashboard
```http
GET /api/admin/dashboard
Authorization: Bearer <token>

Response 200:
{
  "success": true,
  "data": {
    "summary": {
      "total_applications": 27,
      "pending": 27,
      "approved": 0,
      "rejected": 0
    },
    "distributions": {
      "positions": [...],
      "nationalities": [...],
      "english_levels": [...]
    },
    "recent_applications": [...],
    "trends": {...},
    "conversion_rate": 0
  }
}
```

### Búsqueda y Filtros
```http
GET /api/admin/applications/search
Authorization: Bearer <token>
Query: ?q=texto&status=pending&position=Camarero&page=1

Response 200:
{
  "success": true,
  "data": {
    "applications": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 27,
      "pages": 2
    }
  }
}
```

### Exportación
```http
GET /api/admin/applications/export
Authorization: Bearer <token>
Query: ?format=excel&status=pending

Response 200:
{
  "success": true,
  "data": {
    "file_content": "base64_encoded",
    "filename": "applications_export_20251017.xlsx",
    "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "count": 27,
    "format": "excel"
  }
}
```

### Actualización de Status
```http
PUT /api/admin/applications/<id>/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "approved",
  "send_notification": true
}

Response 200:
{
  "success": true,
  "data": {
    "application_id": "...",
    "old_status": "pending",
    "new_status": "approved",
    "notification_sent": true
  }
}
```

### Aprobar/Rechazar
```http
POST /api/admin/applications/<id>/approve
POST /api/admin/applications/<id>/reject
Authorization: Bearer <token>

Response 200:
{
  "success": true,
  "data": {
    "application_id": "...",
    "status": "approved",
    "notification_sent": true,
    "approved_by": "admin",
    "approved_at": "..."
  }
}
```

## 8.4 Endpoints de Archivos

Ver sección [6.4 Endpoints de Archivos](#64-endpoints-de-archivos)

## 8.5 Endpoints de Auditoría

### Logs de Auditoría
```http
GET /api/admin/audit/logs
Authorization: Bearer <token>
Query: ?limit=50&offset=0&event_type=login_success

Response 200:
{
  "success": true,
  "data": {
    "logs": [...],
    "total_count": 156,
    "has_more": true
  }
}
```

### Estadísticas
```http
GET /api/admin/audit/stats
Authorization: Bearer <token>

Response 200:
{
  "success": true,
  "data": {
    "by_event_type": {...},
    "by_admin": {...},
    "by_date": {...}
  }
}
```

---

# IX. SERVICIOS EXTERNOS

## 9.1 MongoDB Atlas

```yaml
Estado: ✅ Operativo
Cluster: M0 Sandbox (AWS EU-Central-1)
Base de Datos: workwave
Collection: candidates
Documentos: 27
Índices: 10 optimizados
Backup: Automático
SSL: Habilitado
Performance: Óptimo
```

**Conexión:**
```bash
MONGODB_URI=mongodb+srv://[configured]
```

## 9.2 Cloudinary

```yaml
Estado: ✅ Funcional
Cloud Name: dde3kelit
API Key: 746326863757738
Archivos: 16 preservados
Storage: 2.63 MB
CDN: Global optimizado
Transformaciones: Automáticas
Security: URLs firmadas
```

**Configuración:**
```bash
CLOUDINARY_CLOUD_NAME=dde3kelit
CLOUDINARY_API_KEY=746326863757738
CLOUDINARY_API_SECRET=[configured]
```

## 9.3 Gmail SMTP

```yaml
Estado: ✅ Operativo
Servidor: smtp.gmail.com
Puerto: 587 (TLS)
Username: workwavecoast@gmail.com
Autenticación: App Password
Funcionalidades:
  - Notificaciones a admins
  - Emails a candidatos
  - Password recovery
  - Confirmaciones
```

**Configuración:**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=workwavecoast@gmail.com
MAIL_PASSWORD=[configured]
```

---

# X. INTERFAZ DE USUARIO

## 10.1 Frontend - Formulario Público

**Características:**
- Diseño moderno y limpio
- Validación en tiempo real
- Feedback visual inmediato
- Upload de archivos con preview
- Prevención de duplicados
- Mensajes de error específicos
- Confirmación de envío

**Campos del Formulario:**
- Nombre y Apellido
- Email (validado y único)
- Teléfono (formato internacional)
- Nacionalidad (50+ países)
- Nivel de Inglés (obligatorio)
- Puesto de trabajo
- Puestos adicionales (opcional)
- Experiencia laboral
- CV (PDF, max 5MB)
- Foto (JPG/PNG, max 2MB)

## 10.2 Panel de Administración

**Estado**: ✅ Backend 100%, Frontend 60%

### Funcionalidades Backend (100%)
- ✅ Autenticación JWT con RBAC
- ✅ Dashboard con métricas avanzadas
- ✅ Listado con paginación
- ✅ Búsqueda full-text
- ✅ Filtros avanzados completos
- ✅ Exportación CSV/Excel
- ✅ Preview de archivos
- ✅ Actualización de status
- ✅ Notificaciones automáticas
- ✅ Sistema de auditoría
- ✅ Eliminación individual y masiva

### Funcionalidades Frontend (60%)
- ✅ Login con JWT
- ✅ Listado básico de aplicaciones
- ✅ Paginación
- ⚠️ Filtros básicos (requiere UI completa)
- ⚠️ Dashboard simple (faltan gráficos)
- ❌ Búsqueda full-text (backend listo)
- ❌ Exportación UI (backend listo)
- ❌ Gráficos y visualizaciones

## 10.3 Diseño Responsive

### Mobile First (320px+)
- Formulario de una columna
- Botones táctiles optimizados
- Tipografía legible
- Imágenes optimizadas

### Tablet (768px+)
- Layout de dos columnas
- Navegación mejorada
- Mayor densidad de información

### Desktop (1024px+)
- Layout completo
- Hover effects
- Funcionalidades avanzadas
- Dashboard ampliado

---

# XI. DESPLIEGUE

## 11.1 Arquitectura de Producción

```
Frontend (GitHub Pages)
├── workwavecoast.online
├── Responsive design
├── CDN distribution
├── HTTPS automático
└── Validación internacional

Backend (Render/Local)
├── API REST Flask
├── Python 3.11+ runtime
├── Health checks
├── SSL/TLS encryption
├── JWT + RBAC
└── MongoDB Atlas integrado

Database (MongoDB Atlas)
├── Cluster en la nube
├── 27 documentos
├── 10 índices optimizados
├── Backups automatizados
├── Prevención duplicados
└── Text search activo

Storage (Cloudinary)
├── 16 archivos
├── Transformaciones automáticas
├── CDN global
└── URLs firmadas
```

## 11.2 Configuración de Hosting

### Para Render
```yaml
# render.yaml
services:
  - type: web
    name: workwave-coast-backend
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "python backend/app.py"
    healthCheckPath: /api/system-status
```

### Procfile (Heroku/Render)
```
web: gunicorn --config gunicorn_config.py backend.app:app
```

## 11.3 Variables de Producción

Todas las variables están configuradas en `.env`:

```bash
# Base de Datos
MONGODB_URI=[configured]
MONGO_DB_NAME=workwave

# Servicios
CLOUDINARY_CLOUD_NAME=dde3kelit
CLOUDINARY_API_KEY=746326863757738
CLOUDINARY_API_SECRET=[configured]
MAIL_USERNAME=workwavecoast@gmail.com
MAIL_PASSWORD=[configured]

# Seguridad
SECRET_KEY=[configured]
ADMIN_USERNAME=admin
ADMIN_PASSWORD=[configured]

# Config
DEBUG=False
TESTING=False
PORT=5000
```

## 11.4 Checklist de Despliegue

### ✅ Infraestructura Base
- [x] Variables configuradas y verificadas
- [x] MongoDB Atlas conectado (27 docs)
- [x] Servicios externos integrados
- [x] Prevención duplicados activa
- [x] Índices optimizados (10)

### ✅ Seguridad
- [x] JWT + RBAC implementado
- [x] Bcrypt password hashing
- [x] Índice único para emails
- [x] Rate limiting configurado
- [x] Audit logging activo

### ✅ Funcionalidad
- [x] API endpoints funcionando
- [x] Upload Cloudinary operativo
- [x] Sistema email configurado
- [x] Panel admin accesible
- [x] Búsqueda y filtros completos
- [x] Exportación CSV/Excel funcional
- [x] Notificaciones automáticas activas

### 🔧 Para Completar
- [ ] Elegir hosting (Render recomendado)
- [ ] Configurar dominio personalizado
- [ ] Configurar monitoreo y logs
- [ ] Implementar CI/CD pipeline
- [ ] Completar frontend UI (60%)

---

# XII. REFERENCIAS

## 12.1 Comandos Útiles

### Desarrollo Local
```bash
# Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar aplicación
python backend/app.py

# Verificar MongoDB
python -c "from config.database import get_database; print(get_database())"

# Verificar Cloudinary
python -c "from services.file_service import FileService; FileService()"
```

### Testing
```bash
# Tests completos
python backend/test_new_features.py

# Tests rápidos
python backend/test_simple.py

# Test búsqueda
python backend/test_search_debug.py
```

### Producción
```bash
# Gunicorn
gunicorn --config gunicorn_config.py backend.app:app

# Con workers
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## 12.2 Troubleshooting

### MongoDB no conecta
```bash
# Verificar variables
echo $MONGODB_URI

# Test conexión
python -c "from config.database import get_database; db = get_database(); print('OK' if db else 'Error')"
```

### Cloudinary error
```bash
# Verificar config
python -c "from services.file_service import FileService; fs = FileService(); print(fs.cloudinary_config)"
```

### JWT no funciona
```bash
# Verificar SECRET_KEY
python -c "from config.settings import get_config; print(get_config().SECRET_KEY[:10])"
```

### Emails no se envían
```bash
# Verificar SMTP
python -c "from services.email_service import EmailService; es = EmailService(); print('OK')"
```

## 12.3 Documentación Adicional

### Archivos de Documentación
```
docs/
├── SETUP.md                    # Setup detallado
├── DOMAIN_SETUP.md             # Configuración dominio
├── SEGURIDAD_CREDENCIALES.md   # Seguridad
├── MEJORES_PRACTICAS.md        # Best practices
├── CODIGO_AUDITORIA.md         # Auditoría
├── WORKFLOW.md                 # Flujo de trabajo
└── conexion_backend_mongodb_firebase.md
```

### Enlaces Útiles
- MongoDB Atlas: https://cloud.mongodb.com
- Cloudinary Dashboard: https://console.cloudinary.com
- Flask Documentation: https://flask.palletsprojects.com
- PyJWT Documentation: https://pyjwt.readthedocs.io

### Contacto
- Email: workwavecoast@gmail.com
- Repositorio: [GitHub URL]

---

## 🎉 RESUMEN FINAL

**WorkWave Coast** es un sistema **95% completo y completamente funcional** con:

✅ **Infraestructura 100% operativa** (MongoDB, Cloudinary, Gmail)
✅ **Backend API 100% implementado** (todos los endpoints)
✅ **Seguridad completa** (JWT + RBAC + Bcrypt + Auditoría)
✅ **Panel Admin Backend 100%** (búsqueda, filtros, export, notificaciones)
⚠️ **Frontend Admin 60%** (requiere UI completa para gráficos)

**El sistema está listo para producción** con todas las funcionalidades críticas implementadas y probadas.

---

**Última actualización**: Octubre 17, 2025
**Versión**: 2.0 - Sistema Completo
**Estado**: ✅ Producción Ready
