"""
WorkWave Coast Application
Updated main application with JWT authentication and RBAC
"""
import os
from flask import Flask, request, send_from_directory, jsonify
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


from typing import Optional


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Application factory function with enhanced authentication

    Args:
        config_name: Configuration environment name (for future use)

    Returns:
        Configured Flask application
    """
    # Create Flask application
    app = Flask(__name__)

    # Load configuration
    # Note: config_name parameter reserved for future multi-environment support
    config = get_config()
    app.config.from_object(config)

    # Setup logging
    logger = setup_logging("workwave_coast", app.config.get('LOG_LEVEL', 'INFO'))
    # Note: app.logger assignment is for convenience, Flask's logger is a cached property
    app.logger = logger  # type: ignore[misc]

    # Initialize database
    try:
        db = get_database()
        if db is not None:
            logger.info("Database initialized successfully")
        else:
            logger.warning("Database connection failed")
    except Exception as e:
        logger.error("Database initialization failed: %s", e)

    # Initialize services - declare variables first to avoid unbound errors
    app_service = None
    email_service = None
    file_service = None
    jwt_service = None
    admin_service = None
    audit_service = None

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
        app.services = {  # type: ignore
            'application': app_service,
            'admin': admin_service,
            'file': file_service,
            'email': email_service,
            'jwt': jwt_service,
            'audit': audit_service
        }
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error("Service initialization failed: %s", e)
        app.services = {}  # type: ignore

    # Initialize RBAC middleware
    rbac_middleware = None
    try:
        if admin_service and jwt_service:
            rbac_middleware = init_rbac_middleware(admin_service, jwt_service, logger)
            app.rbac_middleware = rbac_middleware  # type: ignore
            logger.info("RBAC middleware initialized successfully")
        else:
            logger.warning("Cannot initialize RBAC middleware: services not available")
            app.rbac_middleware = None  # type: ignore
    except Exception as e:
        logger.error("RBAC middleware initialization failed: %s", e)
        app.rbac_middleware = None  # type: ignore

    # Initialize route modules with services
    try:
        # Initialize admin routes
        if admin_service and app_service and audit_service and rbac_middleware:
            init_admin_routes(
                admin_svc=admin_service,
                app_svc=app_service,
                audit_svc=audit_service,
                rbac_mw=rbac_middleware,
                logger=logger
            )
        else:
            logger.warning("Cannot initialize admin routes: required services not available")

        # Initialize password recovery routes
        if admin_service and jwt_service and email_service and audit_service:
            init_password_recovery_routes(
                admin_svc=admin_service,
                jwt_svc=jwt_service,
                email_svc=email_service,
                audit_svc=audit_service,
                logger=logger
            )
        else:
            logger.warning("Cannot initialize password recovery routes: required services not available")

        logger.info("Route modules initialized successfully")
    except Exception as e:
        logger.error("Route module initialization failed: %s", e)

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
        # ErrorMiddleware(app)  # Temporarily disabled - conflicts with error handlers
        LoggingMiddleware(app)

        logger.info("Middleware initialized successfully")
    except Exception as e:
        logger.error("Middleware initialization failed: %s", e)

    # Initialize rate limiting
    try:
        init_rate_limiter(app)
        logger.info("Rate limiter initialized successfully")
    except Exception as e:
        logger.warning("Rate limiter initialization failed: %s", e)

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
            logger.error("Global request validation error: %s", e)
            return None

    logger.info("Flask application created successfully with JWT authentication")
    return app


def register_error_handlers(application: Flask) -> None:
    """Register application error handlers"""

    @application.errorhandler(404)
    def not_found(_error):
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": "Endpoint not found",
                "error_type": "NotFound"
            }), 404
        return jsonify({
            "success": False,
            "message": "Page not found",
            "error_type": "NotFound"
        }), 404

    @application.errorhandler(500)
    def internal_error(_error):
        application.logger.error("Internal server error: %s", _error)
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": "Internal server error",
                "error_type": "ServerError"
            }), 500
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "error_type": "ServerError"
        }), 500

    @application.errorhandler(401)
    def unauthorized(_error):
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": "Authentication required",
                "error_type": "Unauthorized"
            }), 401
        return jsonify({
            "success": False,
            "message": "Authentication required",
            "error_type": "Unauthorized"
        }), 401

    @application.errorhandler(403)
    def forbidden(_error):
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": "Access forbidden",
                "error_type": "Forbidden"
            }), 403
        return jsonify({
            "success": False,
            "message": "Access forbidden",
            "error_type": "Forbidden"
        }), 403


def register_main_routes(application: Flask) -> None:
    """Register main application routes"""

    @application.route('/')
    def index():
        """Main page - API documentation"""
        return jsonify({
            "message": "WorkWave Coast API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "api": "/api",
                "admin": "/admin",
                "admin_api": "/api/admin",
                "files": "/api/files",
                "health": "/api/health"
            }
        })

    @application.route('/admin')
    @application.route('/admin/')
    def admin_panel():
        """Serve admin panel login page"""
        admin_panel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'admin-panel')
        return send_from_directory(admin_panel_path, 'login.html')

    @application.route('/admin/<path:filename>')
    def admin_panel_files(filename):
        """Serve admin panel static files"""
        admin_panel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'admin-panel')
        return send_from_directory(admin_panel_path, filename)

    @application.route('/api/status')
    def api_status():
        """API status endpoint"""
        services_status = {}

        if hasattr(application, 'services') and application.services:  # type: ignore
            for service_name, service in application.services.items():  # type: ignore
                try:
                    if hasattr(service, 'health_check'):
                        services_status[service_name] = service.health_check()
                    else:
                        services_status[service_name] = {"status": "available"}
                except Exception as e:
                    services_status[service_name] = {"status": "error", "error": str(e)}

        return jsonify({
            "success": True,
            "message": "WorkWave Coast API is running",
            "data": {
                "application": "WorkWave Coast",
                "version": "1.0.0",
                "environment": application.config.get('ENV', 'development'),
                "authentication": "JWT with RBAC",
                "services": services_status
            }
        })


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
