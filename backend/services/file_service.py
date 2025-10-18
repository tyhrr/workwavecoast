"""
File Service
Business logic for file upload and management with Cloudinary
"""
import logging
from typing import Dict, Any, Optional, Tuple, List
import os
import uuid
from werkzeug.datastructures import FileStorage
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError

# Ensure environment variables are loaded
from config.env_loader import ensure_env_loaded
ensure_env_loaded()

from services.base_service import BaseService
from config.cloudinary_config import get_cloudinary_config
from config.constants import FILE_SIZE_LIMITS, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES


class FileService(BaseService):
    """Service for handling file upload and management operations"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self.cloudinary_configured = False
        self._configure_cloudinary()

    def _configure_cloudinary(self):
        """Configure Cloudinary with environment variables"""
        try:
            # Get credentials from environment variables
            cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
            api_key = os.getenv('CLOUDINARY_API_KEY')
            api_secret = os.getenv('CLOUDINARY_API_SECRET')

            if not all([cloud_name, api_key, api_secret]):
                self.logger.warning("Cloudinary credentials not found in environment variables")
                self.cloudinary_configured = False
                return

            config = get_cloudinary_config(cloud_name, api_key, api_secret)
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            self.cloudinary_configured = True
            self.log_operation("configure_cloudinary", {"status": "configured"})
        except Exception as e:
            self.logger.error(f"Failed to configure Cloudinary: {e}")
            self.cloudinary_configured = False

    def validate_file(self, file: FileStorage, field_name: str) -> Tuple[bool, Optional[str], int]:
        """Validate uploaded file size, extension, and MIME type"""
        if not file or not file.filename:
            return True, None, 0

        # Validate file extension
        if field_name in ALLOWED_EXTENSIONS:
            file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if f'.{file_extension}' not in ALLOWED_EXTENSIONS[field_name]:
                allowed = ', '.join(ALLOWED_EXTENSIONS[field_name])
                return False, f"Tipo de archivo no permitido para {field_name}. Permitidos: {allowed}", 0

        # Validate MIME type
        if field_name in ALLOWED_MIME_TYPES and hasattr(file, 'content_type') and file.content_type:
            if file.content_type not in ALLOWED_MIME_TYPES[field_name]:
                allowed_mimes = ', '.join(ALLOWED_MIME_TYPES[field_name])
                return False, f"Tipo MIME no permitido para {field_name}. Esperado: {allowed_mimes}, recibido: {file.content_type}", 0

        # Validate file size
        try:
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
        except IOError:
            return False, f"Error al procesar el archivo {field_name}", 0

        if field_name in FILE_SIZE_LIMITS and file_size > FILE_SIZE_LIMITS[field_name]:
            max_size_mb = FILE_SIZE_LIMITS[field_name] / (1024 * 1024)
            return False, f"El archivo {field_name} es demasiado grande. Máximo: {max_size_mb}MB", file_size

        # Additional security validation
        if file_size == 0:
            return False, f"El archivo {field_name} está vacío", 0

        # Validate filename for security
        if not self._is_safe_filename(file.filename):
            return False, f"Nombre de archivo no válido para {field_name}", file_size

        return True, None, file_size

    def _is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe (no path traversal, etc.)"""
        if not filename:
            return False

        # Check for path traversal attempts
        dangerous_patterns = ['../', '..\\', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        for pattern in dangerous_patterns:
            if pattern in filename:
                return False

        # Check length
        if len(filename) > 255:
            return False

        return True

    def generate_unique_filename(self, original_filename: str, prefix: str = "workwave") -> str:
        """Generate a unique filename for upload"""
        if not original_filename:
            return f"{prefix}_{uuid.uuid4().hex}"

        # Get file extension
        file_extension = ""
        if '.' in original_filename:
            file_extension = '.' + original_filename.split('.')[-1].lower()

        # Generate unique name
        unique_id = uuid.uuid4().hex[:12]
        return f"{prefix}_{unique_id}{file_extension}"

    def upload_to_cloudinary(self, file: FileStorage, field_name: str,
                           public_id_prefix: str = "workwave") -> Dict[str, Any]:
        """Upload file to Cloudinary with validation and error handling"""
        try:
            if not self.cloudinary_configured:
                return self.error_response(
                    "Cloudinary not configured",
                    "ConfigurationError"
                )

            # Validate file
            is_valid, error_message, file_size = self.validate_file(file, field_name)
            if not is_valid:
                return self.error_response(error_message, "ValidationError")

            if file_size == 0:  # No file provided
                return self.success_response(None, "No file provided")

            # Generate unique public_id
            public_id = self.generate_unique_filename(file.filename, public_id_prefix)

            # Determine resource type and additional options
            upload_options = {
                'public_id': public_id,
                'resource_type': 'auto',  # Automatically detect resource type
                'folder': f'workwave/{field_name}',  # Organize by field type
                'use_filename': False,
                'unique_filename': True,
                'overwrite': False
            }

            # Add specific options based on file type
            if field_name == 'cv':
                # For CV documents
                upload_options.update({
                    'resource_type': 'raw',
                    'flags': ['attachment'],  # Force download instead of display
                })
            elif field_name == 'foto':
                # For photos with advanced transformations
                upload_options.update({
                    'resource_type': 'image',
                    'transformation': [
                        # Resize and optimize
                        {'width': 800, 'height': 800, 'crop': 'limit'},
                        {'quality': 'auto:good'},
                        {'format': 'auto'},
                        # Add subtle enhancement
                        {'effect': 'auto_brightness:20'},
                        {'effect': 'auto_contrast:10'}
                    ],
                    'eager': [
                        # Generate thumbnail
                        {'width': 150, 'height': 150, 'crop': 'thumb', 'gravity': 'face'},
                        # Generate medium size
                        {'width': 400, 'height': 400, 'crop': 'limit'}
                    ]
                })
            elif field_name in ['carta_presentacion', 'referencias', 'certificados']:
                # For other documents
                upload_options.update({
                    'resource_type': 'auto',
                    'flags': ['attachment']
                })

            # Upload to Cloudinary
            self.logger.info(f"Uploading {field_name} to Cloudinary: {file.filename}")

            result = cloudinary.uploader.upload(file, **upload_options)

            # Prepare response data
            file_info = {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'resource_type': result['resource_type'],
                'format': result.get('format'),
                'size': result.get('bytes', file_size),
                'created_at': result['created_at'],
                'original_filename': file.filename,
                'field_name': field_name
            }

            # Add image-specific info if it's an image
            if result['resource_type'] == 'image':
                file_info.update({
                    'width': result.get('width'),
                    'height': result.get('height'),
                    'thumbnail_url': self._generate_thumbnail_url(result['public_id']),
                    'medium_url': self._generate_medium_url(result['public_id'])
                })

            # Add document-specific info
            if field_name == 'cv':
                file_info.update({
                    'download_url': result['secure_url'],
                    'preview_available': False  # PDFs need special handling for preview
                })

            self.log_operation("upload_to_cloudinary", {
                "field_name": field_name,
                "public_id": result['public_id'],
                "size": file_size,
                "original_filename": file.filename
            })

            return self.success_response(file_info, f"File {field_name} uploaded successfully")

        except CloudinaryError as e:
            return self.handle_error("upload_to_cloudinary", e, {
                "field_name": field_name,
                "filename": file.filename if file else None
            })
        except Exception as e:
            return self.handle_error("upload_to_cloudinary", e, {
                "field_name": field_name,
                "filename": file.filename if file else None
            })

    def upload_multiple_files(self, files: Dict[str, FileStorage],
                            public_id_prefix: str = "workwave") -> Dict[str, Any]:
        """Upload multiple files to Cloudinary"""
        try:
            if not files:
                return self.success_response({}, "No files provided")

            results = {}
            errors = []
            total_size = 0

            for field_name, file in files.items():
                if file and file.filename:
                    # Upload individual file
                    upload_result = self.upload_to_cloudinary(file, field_name, public_id_prefix)

                    if upload_result.get('success'):
                        results[field_name] = upload_result['data']
                        total_size += upload_result['data'].get('size', 0)
                    else:
                        errors.append({
                            'field': field_name,
                            'error': upload_result.get('message', 'Upload failed')
                        })

            # Check if any files were uploaded successfully
            if results:
                self.log_operation("upload_multiple_files", {
                    "files_uploaded": len(results),
                    "total_size": total_size,
                    "errors": len(errors)
                })

                response_data = {
                    'files': results,
                    'summary': {
                        'uploaded_count': len(results),
                        'error_count': len(errors),
                        'total_size': total_size
                    }
                }

                if errors:
                    response_data['errors'] = errors
                    return self.success_response(response_data,
                        f"Uploaded {len(results)} files with {len(errors)} errors")
                else:
                    return self.success_response(response_data,
                        f"Successfully uploaded {len(results)} files")

            else:
                return self.error_response(
                    "No files were uploaded successfully",
                    "UploadError",
                    {"errors": errors}
                )

        except Exception as e:
            return self.handle_error("upload_multiple_files", e, {
                "file_count": len(files) if files else 0
            })

    def delete_file(self, public_id: str, resource_type: str = 'auto') -> Dict[str, Any]:
        """Delete a file from Cloudinary"""
        try:
            if not self.cloudinary_configured:
                return self.error_response(
                    "Cloudinary not configured",
                    "ConfigurationError"
                )

            if not public_id:
                return self.error_response("Public ID is required", "ValidationError")

            # Delete from Cloudinary
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)

            success = result.get('result') == 'ok'

            if success:
                self.log_operation("delete_file", {"public_id": public_id, "resource_type": resource_type})
                return self.success_response(result, "File deleted successfully")
            else:
                return self.error_response(
                    f"Failed to delete file: {result.get('result', 'unknown error')}",
                    "DeletionError",
                    {"cloudinary_result": result}
                )

        except CloudinaryError as e:
            return self.handle_error("delete_file", e, {
                "public_id": public_id,
                "resource_type": resource_type
            })
        except Exception as e:
            return self.handle_error("delete_file", e, {
                "public_id": public_id,
                "resource_type": resource_type
            })

    def delete_multiple_files(self, public_ids: List[str], resource_type: str = 'auto') -> Dict[str, Any]:
        """Delete multiple files from Cloudinary"""
        try:
            if not self.cloudinary_configured:
                return self.error_response(
                    "Cloudinary not configured",
                    "ConfigurationError"
                )

            if not public_ids:
                return self.error_response("No public IDs provided", "ValidationError")

            results = []
            deleted_count = 0

            for public_id in public_ids:
                delete_result = self.delete_file(public_id, resource_type)
                results.append({
                    'public_id': public_id,
                    'success': delete_result.get('success', False),
                    'message': delete_result.get('message', '')
                })

                if delete_result.get('success'):
                    deleted_count += 1

            self.log_operation("delete_multiple_files", {
                "requested_count": len(public_ids),
                "deleted_count": deleted_count
            })

            return self.success_response({
                'results': results,
                'summary': {
                    'requested_count': len(public_ids),
                    'deleted_count': deleted_count,
                    'failed_count': len(public_ids) - deleted_count
                }
            }, f"Deleted {deleted_count} of {len(public_ids)} files")

        except Exception as e:
            return self.handle_error("delete_multiple_files", e, {
                "public_ids_count": len(public_ids) if public_ids else 0
            })

    def get_file_info(self, public_id: str, resource_type: str = 'auto') -> Dict[str, Any]:
        """Get information about a file from Cloudinary"""
        try:
            if not self.cloudinary_configured:
                return self.error_response(
                    "Cloudinary not configured",
                    "ConfigurationError"
                )

            if not public_id:
                return self.error_response("Public ID is required", "ValidationError")

            # Get resource info from Cloudinary
            result = cloudinary.api.resource(public_id, resource_type=resource_type)

            file_info = {
                'public_id': result['public_id'],
                'url': result['secure_url'],
                'resource_type': result['resource_type'],
                'format': result.get('format'),
                'size': result.get('bytes'),
                'created_at': result['created_at'],
                'width': result.get('width'),
                'height': result.get('height'),
                'folder': result.get('folder'),
                'version': result.get('version')
            }

            self.log_operation("get_file_info", {"public_id": public_id})

            return self.success_response(file_info, "File info retrieved successfully")

        except CloudinaryError as e:
            if "not found" in str(e).lower():
                return self.error_response("File not found", "NotFoundError")
            return self.handle_error("get_file_info", e, {"public_id": public_id})
        except Exception as e:
            return self.handle_error("get_file_info", e, {"public_id": public_id})

    def list_files(self, folder: str = "workwave", max_results: int = 100) -> Dict[str, Any]:
        """List files in a Cloudinary folder"""
        try:
            if not self.cloudinary_configured:
                return self.error_response(
                    "Cloudinary not configured",
                    "ConfigurationError"
                )

            # List resources in folder
            result = cloudinary.api.resources(
                type='upload',
                prefix=folder,
                max_results=min(max_results, 500)  # Cloudinary limit
            )

            files = []
            for resource in result.get('resources', []):
                file_info = {
                    'public_id': resource['public_id'],
                    'url': resource['secure_url'],
                    'resource_type': resource['resource_type'],
                    'format': resource.get('format'),
                    'size': resource.get('bytes'),
                    'created_at': resource['created_at'],
                    'width': resource.get('width'),
                    'height': resource.get('height'),
                    'folder': resource.get('folder')
                }
                files.append(file_info)

            self.log_operation("list_files", {
                "folder": folder,
                "file_count": len(files)
            })

            return self.success_response({
                'files': files,
                'total_count': len(files),
                'folder': folder
            }, f"Listed {len(files)} files from folder {folder}")

        except CloudinaryError as e:
            return self.handle_error("list_files", e, {"folder": folder})
        except Exception as e:
            return self.handle_error("list_files", e, {"folder": folder})

    def generate_signed_url(self, public_id: str, expiration_time: int = 3600) -> Dict[str, Any]:
        """Generate a signed URL for private file access"""
        try:
            if not self.cloudinary_configured:
                return self.error_response(
                    "Cloudinary not configured",
                    "ConfigurationError"
                )

            # Generate signed URL
            signed_url = cloudinary.utils.cloudinary_url(
                public_id,
                sign_url=True,
                type='authenticated',
                expires_at=expiration_time
            )[0]

            self.log_operation("generate_signed_url", {
                "public_id": public_id,
                "expiration_time": expiration_time
            })

            return self.success_response({
                'signed_url': signed_url,
                'public_id': public_id,
                'expires_at': expiration_time
            }, "Signed URL generated successfully")

        except CloudinaryError as e:
            return self.handle_error("generate_signed_url", e, {"public_id": public_id})
        except Exception as e:
            return self.handle_error("generate_signed_url", e, {"public_id": public_id})

    def _generate_thumbnail_url(self, public_id: str) -> str:
        """Generate thumbnail URL for images"""
        try:
            thumbnail_url = cloudinary.utils.cloudinary_url(
                public_id,
                width=150,
                height=150,
                crop='thumb',
                gravity='face',
                quality='auto:good'
            )[0]
            return thumbnail_url
        except Exception:
            return ""

    def _generate_medium_url(self, public_id: str) -> str:
        """Generate medium-sized URL for images"""
        try:
            medium_url = cloudinary.utils.cloudinary_url(
                public_id,
                width=400,
                height=400,
                crop='limit',
                quality='auto:good'
            )[0]
            return medium_url
        except Exception:
            return ""

    def get_file_preview_info(self, public_id: str, resource_type: str = 'auto') -> Dict[str, Any]:
        """Get file information optimized for preview display"""
        try:
            file_info_result = self.get_file_info(public_id, resource_type)

            if not file_info_result.get('success'):
                return file_info_result

            file_info = file_info_result['data']

            # Add preview-specific information
            preview_info = file_info.copy()

            if file_info['resource_type'] == 'image':
                preview_info.update({
                    'preview_type': 'image',
                    'thumbnail_url': self._generate_thumbnail_url(public_id),
                    'medium_url': self._generate_medium_url(public_id),
                    'can_preview': True
                })
            elif file_info.get('format') == 'pdf':
                preview_info.update({
                    'preview_type': 'pdf',
                    'can_preview': True,
                    'preview_url': f"https://docs.google.com/viewer?url={file_info['url']}&embedded=true"
                })
            else:
                preview_info.update({
                    'preview_type': 'document',
                    'can_preview': False
                })

            return self.success_response(preview_info, "Preview info retrieved successfully")

        except Exception as e:
            return self.handle_error("get_file_preview_info", e, {"public_id": public_id})

    def get_file_stats(self, folder: str = "workwave") -> Dict[str, Any]:
        """Get statistics about uploaded files"""
        try:
            if not self.cloudinary_configured:
                return self.error_response("Cloudinary not configured", "ConfigurationError")

            # Get folder contents
            result = cloudinary.api.resources(
                type='upload',
                prefix=folder,
                max_results=500
            )

            stats = {
                'total_files': 0,
                'total_size': 0,
                'file_types': {},
                'by_folder': {}
            }

            for resource in result.get('resources', []):
                stats['total_files'] += 1
                stats['total_size'] += resource.get('bytes', 0)

                # Count by format
                format_type = resource.get('format', 'unknown')
                stats['file_types'][format_type] = stats['file_types'].get(format_type, 0) + 1

                # Count by subfolder
                folder_path = resource.get('folder', 'root')
                stats['by_folder'][folder_path] = stats['by_folder'].get(folder_path, 0) + 1

            # Convert total size to human readable
            stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)

            return self.success_response(stats, "File statistics retrieved successfully")

        except Exception as e:
            return self.handle_error("get_file_stats", e, {"folder": folder})

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            if not self.cloudinary_configured:
                return {
                    "status": "unhealthy",
                    "cloudinary_configured": False,
                    "error": "Cloudinary not configured",
                    "service": "FileService"
                }

            # Test Cloudinary connection with a simple API call
            cloudinary.api.ping()

            return {
                "status": "healthy",
                "cloudinary_configured": True,
                "service": "FileService"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "cloudinary_configured": self.cloudinary_configured,
                "error": str(e),
                "service": "FileService"
            }
        """Check service health"""
        try:
            if not self.cloudinary_configured:
                return {
                    "status": "unhealthy",
                    "cloudinary_configured": False,
                    "error": "Cloudinary not configured",
                    "service": "FileService"
                }

            # Test Cloudinary connection with a simple API call
            cloudinary.api.ping()

            return {
                "status": "healthy",
                "cloudinary_configured": True,
                "service": "FileService"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "cloudinary_configured": self.cloudinary_configured,
                "error": str(e),
                "service": "FileService"
            }
