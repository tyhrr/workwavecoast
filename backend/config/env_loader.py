"""
Environment Configuration Loader
Centralizado para cargar variables de entorno desde .env
"""
import os
import pathlib
from dotenv import load_dotenv

# Flag global para evitar cargar múltiples veces
_env_loaded = False

def load_environment():
    """
    Carga variables de entorno desde .env de forma segura
    Puede ser llamado múltiples veces sin problemas
    """
    global _env_loaded

    if _env_loaded:
        return  # Ya está cargado

    try:
        # Buscar .env en diferentes ubicaciones
        # 1. Directorio del proyecto (parent del backend)
        backend_dir = pathlib.Path(__file__).parent
        project_root = backend_dir.parent
        env_path = project_root / '.env'

        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Environment loaded from: {env_path}")
        else:
            # 2. Buscar en el directorio donde se ejecuta el script
            current_dir = pathlib.Path.cwd()
            env_current = current_dir / '.env'
            if env_current.exists():
                load_dotenv(env_current)
                print(f"✅ Environment loaded from: {env_current}")
            else:
                # 3. Fallback a parent del directorio actual
                env_parent = current_dir.parent / '.env'
                if env_parent.exists():
                    load_dotenv(env_parent)
                    print(f"✅ Environment loaded from: {env_parent}")
                else:
                    # 4. Directorio actual sin archivo
                    load_dotenv()
                    print("✅ Environment loaded from system/current directory")

        _env_loaded = True

    except Exception as e:
        print(f"⚠️ Warning: Could not load .env file: {e}")
        print("Continuing with system environment variables...")

def ensure_env_loaded():
    """
    Garantiza que las variables de entorno estén cargadas
    """
    if not _env_loaded:
        load_environment()

# Cargar automáticamente al importar este módulo
load_environment()
