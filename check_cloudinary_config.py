#!/usr/bin/env python3
"""
Cloudinary Configuration Checker
Verifica la configuración de Cloudinary en app.py vs cuenta real
"""

import os
import sys
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar cloudinary
try:
    import cloudinary
    import cloudinary.api
    import cloudinary.uploader
    from cloudinary.exceptions import Error as CloudinaryError
except ImportError:
    print("❌ Error: cloudinary library not found. Install with: pip install cloudinary")
    sys.exit(1)

# Cargar variables de entorno (simulando el comportamiento de app.py)
from dotenv import load_dotenv

# Buscar el archivo .env en backend/
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Archivo .env cargado desde: {env_path}")
else:
    load_dotenv()  # Fallback a buscar en directorio actual
    print("⚠️ Archivo .env no encontrado en backend/, usando variables del sistema")

def get_app_config():
    """Obtiene la configuración de Cloudinary desde app.py"""
    config = {
        'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.getenv('CLOUDINARY_API_KEY'),
        'api_secret': os.getenv('CLOUDINARY_API_SECRET'),
    }
    return config

def test_cloudinary_connection(config):
    """Prueba la conexión a Cloudinary y obtiene información de la cuenta"""
    try:
        # Configurar cloudinary
        cloudinary.config(
            cloud_name=config['cloud_name'],
            api_key=config['api_key'],
            api_secret=config['api_secret']
        )

        # Probar conexión básica
        result = cloudinary.api.ping()

        # Obtener información de la cuenta
        usage = cloudinary.api.usage()

        # Obtener información de configuración
        account_info = {
            'ping_status': result.get('status', 'unknown'),
            'cloud_name': config['cloud_name'],
            'account_type': usage.get('product_name', 'Unknown'),
            'plan': usage.get('plan', 'Unknown'),
            'credits_used': usage.get('credits', {}).get('used', 0),
            'credits_limit': usage.get('credits', {}).get('limit', 0),
            'transformations_used': usage.get('transformations', {}).get('used', 0),
            'transformations_limit': usage.get('transformations', {}).get('limit', 0),
            'bandwidth_used': usage.get('bandwidth', {}).get('used_bytes', 0),
            'bandwidth_limit': usage.get('bandwidth', {}).get('limit_bytes', 0),
            'storage_used': usage.get('storage', {}).get('used_bytes', 0),
            'storage_limit': usage.get('storage', {}).get('limit_bytes', 0),
        }

        return True, account_info, None

    except CloudinaryError as e:
        return False, None, f"Cloudinary API Error: {str(e)}"
    except Exception as e:
        return False, None, f"Connection Error: {str(e)}"

def get_folder_info():
    """Obtiene información sobre la carpeta workwave_coast"""
    try:
        # Buscar archivos en la carpeta workwave_coast
        search_result = cloudinary.Search().expression("folder:workwave_coast").max_results(10).execute()

        folder_info = {
            'total_files': search_result.get('total_count', 0),
            'files_shown': len(search_result.get('resources', [])),
            'files': []
        }

        for resource in search_result.get('resources', []):
            file_info = {
                'public_id': resource.get('public_id'),
                'resource_type': resource.get('resource_type'),
                'format': resource.get('format'),
                'bytes': resource.get('bytes'),
                'url': resource.get('secure_url'),
                'access_mode': resource.get('access_mode', 'unknown'),
                'created_at': resource.get('created_at'),
            }
            folder_info['files'].append(file_info)

        return True, folder_info, None

    except Exception as e:
        return False, None, f"Error getting folder info: {str(e)}"

def print_config_comparison():
    """Imprime una comparación completa de la configuración"""
    print("=" * 80)
    print("🔍 CLOUDINARY CONFIGURATION CHECKER")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. Configuración desde app.py
    print("📋 1. CONFIGURACIÓN EN APP.PY")
    print("-" * 40)
    app_config = get_app_config()

    for key, value in app_config.items():
        if value:
            if key == 'api_secret':
                print(f"   {key}: {'*' * 20} (oculto)")
            else:
                print(f"   {key}: {value}")
        else:
            print(f"   {key}: ❌ NO CONFIGURADO")

    print()

    # 2. Validar variables de entorno
    print("🔐 2. VALIDACIÓN DE VARIABLES DE ENTORNO")
    print("-" * 40)
    required_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    all_configured = True

    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var:
                print(f"   ✅ {var}: {'*' * 20} (configurado)")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NO ENCONTRADO")
            all_configured = False

    print()

    if not all_configured:
        print("❌ Error: Faltan variables de entorno. No se puede continuar.")
        return

    # 3. Probar conexión a Cloudinary
    print("🌐 3. PRUEBA DE CONEXIÓN A CLOUDINARY")
    print("-" * 40)

    success, account_info, error = test_cloudinary_connection(app_config)

    if success and account_info:
        print("   ✅ Conexión exitosa")
        print(f"   📊 Estado: {account_info['ping_status']}")
        print(f"   🏷️  Nombre de la nube: {account_info['cloud_name']}")
        print(f"   📦 Tipo de cuenta: {account_info['account_type']}")
        print(f"   💳 Plan: {account_info['plan']}")
        print()

        print("📈 4. INFORMACIÓN DE USO DE LA CUENTA")
        print("-" * 40)
        print(f"   💰 Créditos: {account_info['credits_used']:,} / {account_info['credits_limit']:,}")
        print(f"   🔄 Transformaciones: {account_info['transformations_used']:,} / {account_info['transformations_limit']:,}")
        print(f"   📶 Ancho de banda: {account_info['bandwidth_used']:,} bytes / {account_info['bandwidth_limit']:,} bytes")
        print(f"   💾 Almacenamiento: {account_info['storage_used']:,} bytes / {account_info['storage_limit']:,} bytes")
        print()

    else:
        print(f"   ❌ Error de conexión: {error}")
        return

    # 5. Información de la carpeta workwave_coast
    print("📁 5. INFORMACIÓN DE LA CARPETA 'workwave_coast'")
    print("-" * 40)

    folder_success, folder_info, folder_error = get_folder_info()

    if folder_success and folder_info:
        print(f"   📊 Total de archivos: {folder_info['total_files']}")
        print(f"   👁️  Archivos mostrados: {folder_info['files_shown']}")
        print()

        if folder_info['files']:
            print("   📄 ARCHIVOS RECIENTES:")
            for i, file_info in enumerate(folder_info['files'][:5], 1):
                print(f"      {i}. {file_info['public_id']}")
                print(f"         - Tipo: {file_info['resource_type']}")
                print(f"         - Formato: {file_info['format']}")
                print(f"         - Tamaño: {file_info['bytes']:,} bytes")
                print(f"         - Modo de acceso: {file_info['access_mode']}")
                print(f"         - URL: {file_info['url'][:60]}...")
                print()
    else:
        print(f"   ❌ Error obteniendo información de carpeta: {folder_error}")

    # 6. Lista de verificación
    print("✅ 6. LISTA DE VERIFICACIÓN IMPORTANTE")
    print("-" * 40)

    checklist = [
        ("Variables de entorno configuradas", all_configured),
        ("Conexión a Cloudinary exitosa", success),
        ("Carpeta workwave_coast accesible", folder_success),
        ("Archivos encontrados en carpeta", folder_success and folder_info and folder_info['total_files'] > 0),
    ]

    for item, status in checklist:
        icon = "✅" if status else "❌"
        print(f"   {icon} {item}")

    print()
    print("=" * 80)

if __name__ == "__main__":
    print_config_comparison()
