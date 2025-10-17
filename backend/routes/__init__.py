"""
Routes Package
Flask route blueprints for WorkWave Coast application
"""

from .api import api_bp
from .admin import admin_bp
from .files import files_bp
from .health import health_bp

__all__ = [
    'api_bp',
    'admin_bp',
    'files_bp',
    'health_bp'
]
