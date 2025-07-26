"""
Utilidades para subida de archivos a servicios cloud
"""
import os
from typing import Optional

try:
    import cloudinary
    import cloudinary.uploader
except ImportError as e:
    print(f"Error importing cloudinary: {e}")
    print("Please install cloudinary: pip install cloudinary")

def configure_cloudinary() -> None:
    """Configurar Cloudinary con variables de entorno"""
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )

def upload_file_to_cloudinary(file_path: str, folder: str = "workwavecoast", resource_type: str = "auto") -> Optional[str]:
    """
    Subir archivo a Cloudinary
    
    Args:
        file_path (str): Ruta del archivo local
        folder (str): Carpeta en Cloudinary
        resource_type (str): Tipo de recurso (auto, image, video, raw)
    
    Returns:
        str: URL segura del archivo subido o None si falla
    """
    try:
        result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            folder=folder,
            use_filename=True,
            unique_filename=True
        )
        return result.get('secure_url')
    except cloudinary.exceptions.Error as e:
        print(f"Error subiendo archivo a Cloudinary: {e}")
        return None
    except (FileNotFoundError, OSError) as e:
        print(f"Error con archivo local: {e}")
        return None

def delete_file_from_cloudinary(public_id: str, resource_type: str = "auto") -> bool:
    """
    Eliminar archivo de Cloudinary
    
    Args:
        public_id (str): ID público del archivo en Cloudinary
        resource_type (str): Tipo de recurso
    
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get('result') == 'ok'
    except cloudinary.exceptions.Error as e:
        print(f"Error eliminando archivo de Cloudinary: {e}")
        return False
    except RuntimeError as e:
        print(f"Error inesperado: {e}")
        return False

def get_cloudinary_url(public_id: str, **options) -> str:
    """
    Generar URL de Cloudinary con transformaciones
    
    Args:
        public_id (str): ID público del archivo
        **options: Opciones de transformación
    
    Returns:
        str: URL transformada
    """
    return cloudinary.CloudinaryImage(public_id).build_url(**options)
