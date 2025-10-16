"""
Cloudinary Configuration and Utilities
File upload and management for WorkWave Coast
"""
import os
import logging
from typing import Dict, Any, Optional, Tuple
import cloudinary
import cloudinary.uploader
from config.constants import CLOUDINARY_CONFIG

logger = logging.getLogger(__name__)


class CloudinaryConfig:
    """Cloudinary configuration and utilities"""
    
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """Initialize Cloudinary configuration
        
        Args:
            cloud_name: Cloudinary cloud name
            api_key: Cloudinary API key  
            api_secret: Cloudinary API secret
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        self._configured = False
        
        if self.is_configured():
            self._setup_cloudinary()
    
    def is_configured(self) -> bool:
        """Check if Cloudinary is properly configured
        
        Returns:
            bool: True if all required credentials are present
        """
        return all([
            self.cloud_name,
            self.api_key,
            self.api_secret
        ]) and self.cloud_name != 'tu_cloud_name'
    
    def _setup_cloudinary(self):
        """Setup Cloudinary with credentials"""
        try:
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret,
                secure=True
            )
            self._configured = True
            logger.info("Cloudinary configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Cloudinary: {e}")
            self._configured = False
    
    def upload_file(self, file, field_name: str, **kwargs) -> Dict[str, Any]:
        """Upload file to Cloudinary
        
        Args:
            file: File object to upload
            field_name: Form field name (used for folder organization)
            **kwargs: Additional Cloudinary upload options
            
        Returns:
            dict: Upload result with file information
        """
        if not self.is_configured():
            return {
                'filename': getattr(file, 'filename', 'unknown'),
                'status': 'cloudinary_not_configured',
                'note': 'File received but stored locally due to missing Cloudinary config',
                'system_version': '2.0.2'
            }
        
        try:
            # Prepare upload options
            upload_options = {
                'folder': f"{CLOUDINARY_CONFIG['folder_prefix']}/{field_name}",
                'use_filename': CLOUDINARY_CONFIG['use_filename'],
                'unique_filename': CLOUDINARY_CONFIG['unique_filename'],
                'type': CLOUDINARY_CONFIG['type'],
                'access_mode': CLOUDINARY_CONFIG['access_mode'],
                'sign_url': CLOUDINARY_CONFIG['sign_url'],
                'secure': CLOUDINARY_CONFIG['secure'],
                'quality': CLOUDINARY_CONFIG['quality'],
                'fetch_format': CLOUDINARY_CONFIG['fetch_format'],
                **kwargs  # Allow override of default options
            }
            
            # Upload file
            result = cloudinary.uploader.upload(file, **upload_options)
            
            logger.info(f"File uploaded successfully to Cloudinary: {result.get('public_id')}")
            
            return {
                'status': 'success',
                'public_id': result['public_id'],
                'secure_url': result['secure_url'],
                'bytes': result.get('bytes', 0),
                'format': result.get('format'),
                'resource_type': result.get('resource_type'),
                'created_at': result.get('created_at'),
                'filename': getattr(file, 'filename', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            return {
                'status': 'upload_failed',
                'error': str(e),
                'filename': getattr(file, 'filename', 'unknown')
            }
    
    def delete_file(self, public_id: str) -> bool:
        """Delete file from Cloudinary
        
        Args:
            public_id: Cloudinary public ID of the file
            
        Returns:
            bool: True if deletion was successful
        """
        if not self.is_configured():
            logger.warning("Cloudinary not configured, cannot delete file")
            return False
            
        try:
            result = cloudinary.uploader.destroy(public_id)
            success = result.get('result') == 'ok'
            
            if success:
                logger.info(f"File deleted from Cloudinary: {public_id}")
            else:
                logger.warning(f"File deletion failed: {result}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error deleting file from Cloudinary: {e}")
            return False
    
    def get_signed_url(self, public_id: str, **kwargs) -> str:
        """Generate signed URL for private resource
        
        Args:
            public_id: Cloudinary public ID
            **kwargs: Additional URL transformation options
            
        Returns:
            str: Signed URL or empty string if failed
        """
        if not self.is_configured():
            return ""
            
        try:
            from cloudinary.utils import cloudinary_url
            url, _ = cloudinary_url(public_id, sign_url=True, **kwargs)
            return url
        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            return ""
    
    def get_info(self) -> Dict[str, Any]:
        """Get Cloudinary configuration information
        
        Returns:
            dict: Configuration status and information
        """
        return {
            'configured': self.is_configured(),
            'cloud_name': self.cloud_name if self.is_configured() else 'Not configured',
            'api_key_set': bool(self.api_key),
            'api_secret_set': bool(self.api_secret),
            'upload_folder': f"{CLOUDINARY_CONFIG['folder_prefix']}"
        }


class CloudinaryManager:
    """Singleton Cloudinary manager"""
    
    _instance: Optional['CloudinaryManager'] = None
    _config: Optional[CloudinaryConfig] = None
    
    def __new__(cls) -> 'CloudinaryManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, cloud_name: str, api_key: str, api_secret: str) -> CloudinaryConfig:
        """Initialize Cloudinary configuration
        
        Args:
            cloud_name: Cloudinary cloud name
            api_key: Cloudinary API key
            api_secret: Cloudinary API secret
            
        Returns:
            CloudinaryConfig: Initialized configuration
        """
        if self._config is None:
            self._config = CloudinaryConfig(cloud_name, api_key, api_secret)
            
        return self._config
    
    @property
    def config(self) -> Optional[CloudinaryConfig]:
        """Get current Cloudinary configuration"""
        return self._config


# Global Cloudinary manager instance
cloudinary_manager = CloudinaryManager()


def get_cloudinary_config(cloud_name: str, api_key: str, api_secret: str) -> CloudinaryConfig:
    """Get or create Cloudinary configuration
    
    Args:
        cloud_name: Cloudinary cloud name
        api_key: Cloudinary API key
        api_secret: Cloudinary API secret
        
    Returns:
        CloudinaryConfig: Cloudinary configuration instance
    """
    return cloudinary_manager.initialize(cloud_name, api_key, api_secret)


def upload_file(file, field_name: str, **kwargs) -> Dict[str, Any]:
    """Upload file using global Cloudinary manager
    
    Args:
        file: File object to upload
        field_name: Form field name
        **kwargs: Additional upload options
        
    Returns:
        dict: Upload result
    """
    config = cloudinary_manager.config
    if config:
        return config.upload_file(file, field_name, **kwargs)
    else:
        logger.error("Cloudinary not initialized")
        return {
            'status': 'not_initialized',
            'error': 'Cloudinary configuration not initialized'
        }


def delete_file(public_id: str) -> bool:
    """Delete file using global Cloudinary manager
    
    Args:
        public_id: Cloudinary public ID
        
    Returns:
        bool: True if deletion was successful
    """
    config = cloudinary_manager.config
    if config:
        return config.delete_file(public_id)
    else:
        logger.error("Cloudinary not initialized")
        return False