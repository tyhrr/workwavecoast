"""
Application Configuration
Main Flask application configuration
"""
import os
from datetime import timedelta


def get_config():
    """Get Flask application configuration"""
    config = {
        # Flask settings
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        'TESTING': os.getenv('FLASK_TESTING', 'False').lower() == 'true',

        # Session settings
        'PERMANENT_SESSION_LIFETIME': timedelta(hours=24),
        'SESSION_COOKIE_SECURE': os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',

        # File upload settings
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB max file size
        'UPLOAD_FOLDER': os.getenv('UPLOAD_FOLDER', 'uploads'),

        # JSON settings
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': True,

        # Security headers
        'SEND_FILE_MAX_AGE_DEFAULT': timedelta(hours=12),

        # CORS settings (handled in app factory)
        'CORS_ORIGINS': os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://workwavecoast.com').split(','),

        # Application-specific settings
        'APP_NAME': 'WorkWave Coast',
        'APP_VERSION': '1.0.0',
        'API_VERSION': '1.0',

        # Pagination defaults
        'DEFAULT_PAGE_SIZE': 10,
        'MAX_PAGE_SIZE': 100,

        # Rate limiting (for future implementation)
        'RATELIMIT_DEFAULT': '100 per hour',
        'RATELIMIT_STORAGE_URL': os.getenv('RATELIMIT_STORAGE_URL', 'memory://'),

        # Template settings
        'TEMPLATES_AUTO_RELOAD': os.getenv('TEMPLATES_AUTO_RELOAD', 'False').lower() == 'true',

        # Logging
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_FILE': os.getenv('LOG_FILE'),

        # Environment
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'production'),
    }

    return config


def get_flask_config_class():
    """Get Flask config class based on environment"""

    class Config:
        """Base configuration"""
        config_dict = get_config()

        # Apply all config values as class attributes
        for key, value in config_dict.items():
            locals()[key] = value

    class DevelopmentConfig(Config):
        """Development configuration"""
        DEBUG = True
        TESTING = False
        SESSION_COOKIE_SECURE = False
        TEMPLATES_AUTO_RELOAD = True

    class ProductionConfig(Config):
        """Production configuration"""
        DEBUG = False
        TESTING = False
        SESSION_COOKIE_SECURE = True
        TEMPLATES_AUTO_RELOAD = False

    class TestingConfig(Config):
        """Testing configuration"""
        DEBUG = False
        TESTING = True
        SESSION_COOKIE_SECURE = False
        WTF_CSRF_ENABLED = False

    # Select config based on environment
    env = os.getenv('ENVIRONMENT', 'production').lower()

    config_mapping = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }

    return config_mapping.get(env, ProductionConfig)
