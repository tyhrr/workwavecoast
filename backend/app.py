"""
WorkWave Coast Application
Updated main application with JWT authentication and RBAC
"""
import os
import logging
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables first
import pathlib
env_path = pathlib.Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

# Import configuration
from config.settings import get_config
from config.database import get_database

# Import utilities
from utils.logging_config import setup_logging
from utils.rate_limiter import init_rate_limiter

# Import middleware
from middleware import (
    AuthMiddleware,
    ValidationMiddleware,
    ErrorMiddleware,
    LoggingMiddleware,
    setup_cors_and_security
)
from middleware.rbac_middleware import init_rbac_middleware

# Import route blueprints
from routes import api_bp, files_bp, health_bp
from routes.admin import admin_bp, init_admin_routes
from routes.password_recovery import password_recovery_bp, init_password_recovery_routes

# Import services for initialization
from services import (
    ApplicationService,
    AdminService,
    FileService,
    EmailService,
    JWTService,
    AuditService
)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function with enhanced authentication

    Args:
        config_name: Configuration environment name

    Returns:
        Configured Flask application
    """
    # Create Flask application
    app = Flask(__name__)

    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Setup logging
    logger = setup_logging("workwave_coast", app.config.get('LOG_LEVEL', 'INFO'))
    app.logger = logger

    # Initialize database
    try:
        db = get_database()
        if db is not None:
            logger.info("Database initialized successfully")
        else:
            logger.warning("Database connection failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Initialize services
    try:
        # Core services
        app_service = ApplicationService(logger)
        email_service = EmailService(logger)
        file_service = FileService(logger)

        # Authentication services
        jwt_service = JWTService(config, logger)
        admin_service = AdminService(config, jwt_service, logger)
        audit_service = AuditService(logger)

        # Store services in app context
        app.services = {
            'application': app_service,
            'admin': admin_service,
            'file': file_service,
            'email': email_service,
            'jwt': jwt_service,
            'audit': audit_service
        }
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        app.services = {}

    # Initialize RBAC middleware
    try:
        rbac_middleware = init_rbac_middleware(admin_service, jwt_service, logger)
        app.rbac_middleware = rbac_middleware
        logger.info("RBAC middleware initialized successfully")
    except Exception as e:
        logger.error(f"RBAC middleware initialization failed: {e}")
        app.rbac_middleware = None

    # Initialize route modules with services
    try:
        # Initialize admin routes
        init_admin_routes(
            admin_svc=admin_service,
            app_svc=app_service,
            audit_svc=audit_service,
            rbac_mw=rbac_middleware,
            logger=logger
        )

        # Initialize password recovery routes
        init_password_recovery_routes(
            admin_svc=admin_service,
            jwt_svc=jwt_service,
            email_svc=email_service,
            audit_svc=audit_service,
            logger=logger
        )

        logger.info("Route modules initialized successfully")
    except Exception as e:
        logger.error(f"Route module initialization failed: {e}")

    # Initialize middleware
    try:
        # Setup CORS and Security Headers
        cors_config = {
            'origins': app.config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://127.0.0.1:3000']),
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
            'supports_credentials': True
        }
        setup_cors_and_security(app, cors_config)

        # Initialize other middleware
        AuthMiddleware(app)
        ValidationMiddleware(app)
        ErrorMiddleware(app)
        LoggingMiddleware(app)

        logger.info("Middleware initialized successfully")
    except Exception as e:
        logger.error(f"Middleware initialization failed: {e}")

    # Initialize rate limiting
    try:
        init_rate_limiter(app)
        logger.info("Rate limiter initialized successfully")
    except Exception as e:
        logger.warning(f"Rate limiter initialization failed: {e}")

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)  # Now uses /api/admin prefix
    app.register_blueprint(password_recovery_bp)  # /api/admin/auth prefix
    app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(health_bp)
    logger.info("Blueprints registered successfully")

    # Register error handlers
    register_error_handlers(app)

    # Register main routes
    register_main_routes(app)

    # Add JWT token validation middleware globally for API routes
    @app.before_request
    def validate_api_requests():
        """Global request validation for API endpoints"""
        try:
            # Skip validation for non-API routes
            if not request.path.startswith('/api/'):
                return None

            # Skip validation for auth endpoints
            auth_endpoints = [
                '/api/admin/auth/login',
                '/api/admin/auth/refresh',
                '/api/admin/auth/forgot-password',
                '/api/admin/auth/reset-password',
                '/api/admin/auth/validate-recovery-token'
            ]

            if request.path in auth_endpoints:
                return None

            # Skip validation for health checks and public endpoints
            public_endpoints = ['/api/health', '/api/status']
            if request.path in public_endpoints:
                return None

            # For all other API endpoints, we could add global validation here
            # but we're using decorators on individual routes instead
            return None

        except Exception as e:
            logger.error(f"Global request validation error: {e}")
            return None

    logger.info("Flask application created successfully with JWT authentication")
    return app


def register_error_handlers(app: Flask) -> None:
    """Register application error handlers"""

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return {
                "success": False,
                "message": "Endpoint not found",
                "error_type": "NotFound"
            }, 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        if request.path.startswith('/api/'):
            return {
                "success": False,
                "message": "Internal server error",
                "error_type": "ServerError"
            }, 500
        return render_template('500.html'), 500

    @app.errorhandler(401)
    def unauthorized(error):
        if request.path.startswith('/api/'):
            return {
                "success": False,
                "message": "Authentication required",
                "error_type": "Unauthorized"
            }, 401
        return render_template('401.html'), 401

    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api/'):
            return {
                "success": False,
                "message": "Access forbidden",
                "error_type": "Forbidden"
            }, 403
        return render_template('403.html'), 403


def register_main_routes(app: Flask) -> None:
    """Register main application routes"""

    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')

    @app.route('/admin')
    def admin_redirect():
        """Redirect /admin to frontend admin panel"""
        # In production, this might redirect to your frontend admin panel
        return {
            "message": "Admin panel available at /api/admin endpoints",
            "endpoints": {
                "login": "POST /api/admin/auth/login",
                "dashboard": "GET /api/admin/dashboard",
                "profile": "GET /api/admin/profile"
            }
        }

    @app.route('/api/status')
    def api_status():
        """API status endpoint"""
        services_status = {}

        if hasattr(app, 'services') and app.services:
            for service_name, service in app.services.items():
                try:
                    if hasattr(service, 'health_check'):
                        services_status[service_name] = service.health_check()
                    else:
                        services_status[service_name] = {"status": "available"}
                except Exception as e:
                    services_status[service_name] = {"status": "error", "error": str(e)}

        return {
            "success": True,
            "message": "WorkWave Coast API is running",
            "data": {
                "application": "WorkWave Coast",
                "version": "1.0.0",
                "environment": app.config.get('ENV', 'development'),
                "authentication": "JWT with RBAC",
                "services": services_status
            }
        }


# Production WSGI entry point
if __name__ == '__main__':
    app = create_app()

    # Development server configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
