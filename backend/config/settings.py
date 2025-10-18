"""
General Application Settings
Centralized configuration management for WorkWave Coast
"""
import os
from dataclasses import dataclass
from typing import Optional

# Ensure environment variables are loaded
from config.env_loader import ensure_env_loaded
ensure_env_loaded()


@dataclass
class Config:
    """Application configuration settings"""

    # Security
    SECRET_KEY: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    # Database
    MONGODB_URI: str

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # Email
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USE_TLS: bool
    MAIL_USERNAME: str
    MAIL_PASSWORD: str

    # Server
    PORT: int = 5000
    DEBUG: bool = False
    TESTING: bool = False

    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        return cls(
            # Security
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key'),
            ADMIN_USERNAME=os.getenv('ADMIN_USERNAME', 'admin'),
            ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD', 'password'),

            # Database
            MONGODB_URI=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/workwave'),

            # Cloudinary
            CLOUDINARY_CLOUD_NAME=os.getenv('CLOUDINARY_CLOUD_NAME', ''),
            CLOUDINARY_API_KEY=os.getenv('CLOUDINARY_API_KEY', ''),
            CLOUDINARY_API_SECRET=os.getenv('CLOUDINARY_API_SECRET', ''),

            # Email
            MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            MAIL_PORT=int(os.getenv('MAIL_PORT', '587')),
            MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
            MAIL_USERNAME=os.getenv('MAIL_USERNAME', ''),
            MAIL_PASSWORD=os.getenv('MAIL_PASSWORD', ''),

            # Server
            PORT=int(os.getenv('PORT', '5000')),
            DEBUG=os.getenv('DEBUG', 'False').lower() == 'true',
            TESTING=os.getenv('TESTING', 'False').lower() == 'true'
        )

    def validate(self) -> bool:
        """Validate that required configuration is present"""
        required_fields = [
            'SECRET_KEY', 'ADMIN_USERNAME', 'ADMIN_PASSWORD',
            'MONGODB_URI', 'MAIL_USERNAME', 'MAIL_PASSWORD'
        ]

        for field in required_fields:
            value = getattr(self, field)
            if not value or value == '':
                print(f"Warning: Required configuration field '{field}' is missing or empty")
                return False

        return True

    def is_cloudinary_configured(self) -> bool:
        """Check if Cloudinary is properly configured"""
        return all([
            self.CLOUDINARY_CLOUD_NAME,
            self.CLOUDINARY_API_KEY,
            self.CLOUDINARY_API_SECRET
        ]) and self.CLOUDINARY_CLOUD_NAME != 'tu_cloud_name'

    def is_email_configured(self) -> bool:
        """Check if email is properly configured"""
        return all([
            self.MAIL_USERNAME,
            self.MAIL_PASSWORD,
            self.MAIL_SERVER
        ])

    def to_flask_config(self) -> dict:
        """Convert to Flask configuration dictionary"""
        return {
            'SECRET_KEY': self.SECRET_KEY,
            'TESTING': self.TESTING,
            'DEBUG': self.DEBUG,
            # Add other Flask-specific configs as needed
        }


# Create global config instance
def get_config() -> Config:
    """Get the application configuration"""
    config = Config.from_env()

    if not config.validate():
        print("Configuration validation failed. Some features may not work properly.")

    return config
