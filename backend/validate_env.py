#!/usr/bin/env python3
"""
Script de Validación de Variables de Entorno - WorkWave Coast
============================================================

Este script verifica que todas las variables de entorno requeridas
estén presentes y tengan valores válidos antes del despliegue.

Uso:
    python validate_env.py

Autor: WorkWave Team
Fecha: 31 de Julio, 2025
"""

import os
import sys
import re
from dotenv import load_dotenv

def validate_environment():
    """Valida que todas las variables de entorno estén configuradas correctamente."""

    # Cargar variables de entorno
    load_dotenv()

    # Variables requeridas
    required_vars = {
        'MONGODB_URI': {
            'required': True,
            'pattern': r'^mongodb(\+srv)?://.+',
            'description': 'URI de conexión a MongoDB Atlas'
        },
        'CLOUDINARY_CLOUD_NAME': {
            'required': True,
            'pattern': r'^[a-zA-Z0-9_-]+$',
            'description': 'Nombre del cloud de Cloudinary'
        },
        'CLOUDINARY_API_KEY': {
            'required': True,
            'pattern': r'^\d+$',
            'description': 'API Key de Cloudinary (solo números)'
        },
        'CLOUDINARY_API_SECRET': {
            'required': True,
            'pattern': r'^[a-zA-Z0-9_-]+$',
            'description': 'API Secret de Cloudinary'
        },
        'SECRET_KEY': {
            'required': True,
            'min_length': 16,
            'description': 'Clave secreta de Flask (mínimo 16 caracteres)'
        },
        'ADMIN_USERNAME': {
            'required': True,
            'pattern': r'^[a-zA-Z0-9_-]{3,20}$',
            'description': 'Usuario administrador (3-20 caracteres alfanuméricos)'
        },
        'ADMIN_PASSWORD': {
            'required': True,
            'min_length': 8,
            'description': 'Contraseña de administrador (mínimo 8 caracteres)'
        },
        'PORT': {
            'required': False,
            'pattern': r'^\d+$',
            'description': 'Puerto de la aplicación (opcional, default: 5000)'
        }
    }

    errors = []
    warnings = []

    print("🔍 Validando variables de entorno...")
    print("=" * 50)

    for var_name, config in required_vars.items():
        value = os.getenv(var_name)

        # Verificar si la variable está presente
        if config['required'] and not value:
            errors.append(f"❌ {var_name}: Variable requerida faltante")
            continue
        elif not value:
            warnings.append(f"⚠️  {var_name}: Variable opcional no configurada")
            continue

        # Verificar longitud mínima
        if config.get('min_length') and len(value) < config['min_length']:
            errors.append(f"❌ {var_name}: Longitud mínima {config['min_length']} caracteres")
            continue

        # Verificar patrón
        if config.get('pattern') and not re.match(config['pattern'], value):
            errors.append(f"❌ {var_name}: Formato inválido - {config['description']}")
            continue

        print(f"✅ {var_name}: OK")

    # Verificaciones adicionales de seguridad
    print("\n🛡️  Verificaciones de seguridad adicionales...")
    print("=" * 50)

    # Verificar credenciales por defecto inseguras
    secret_key = os.getenv('SECRET_KEY', '')
    if 'workwave' in secret_key.lower() or 'ultra-secure' in secret_key.lower():
        errors.append("❌ SECRET_KEY: Usando clave por defecto insegura - debe cambiarla")

    admin_password = os.getenv('ADMIN_PASSWORD', '')
    if admin_password in ['WorkWave2025!Coastal#Admin', 'admin', 'password', '123456']:
        errors.append("❌ ADMIN_PASSWORD: Usando contraseña por defecto insegura")

    mongodb_uri = os.getenv('MONGODB_URI', '')
    if 'EBTGlzgLj09bsrZK' in mongodb_uri:
        errors.append("❌ MONGODB_URI: Usando credenciales de desarrollo - regenerar para producción")

    cloudinary_secret = os.getenv('CLOUDINARY_API_SECRET', '')
    if cloudinary_secret == '8BXn48ifFovNUYJNhho9T39hw_Q':
        errors.append("❌ CLOUDINARY_API_SECRET: Usando secret de desarrollo - regenerar para producción")

    # Mostrar resultados
    print("\n📊 Resultados de la validación:")
    print("=" * 50)

    if warnings:
        print("⚠️  Advertencias:")
        for warning in warnings:
            print(f"   {warning}")
        print()

    if errors:
        print("❌ Errores encontrados:")
        for error in errors:
            print(f"   {error}")
        print(f"\n💡 Para solucionar estos problemas, consulta: SEGURIDAD_CREDENCIALES.md")
        return False
    else:
        print("✅ Todas las validaciones pasaron correctamente")
        print("🚀 El entorno está listo para producción")
        return True

def generate_secure_secret():
    """Genera una clave secreta segura."""
    import secrets
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    print("🛡️  WorkWave Coast - Validador de Variables de Entorno")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "--generate-secret":
        print(f"🔑 Nueva clave secreta generada:")
        print(f"SECRET_KEY={generate_secure_secret()}")
        sys.exit(0)

    success = validate_environment()

    if not success:
        print(f"\n🚨 ACCIÓN REQUERIDA: Corrige los errores antes del despliegue")
        print(f"📖 Consulta SEGURIDAD_CREDENCIALES.md para instrucciones detalladas")
        sys.exit(1)
    else:
        print(f"\n🎉 ¡Validación exitosa! El entorno está configurado correctamente.")
        sys.exit(0)
