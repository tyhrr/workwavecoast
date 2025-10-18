"""
Main Routes
Flask routes for main application pages and utilities
"""
import logging
from flask import Blueprint, request, jsonify, render_template
from services import ApplicationService, AdminService, FileService, EmailService

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
app_service = ApplicationService(logger)
admin_service = AdminService(logger)
file_service = FileService(logger)
email_service = EmailService(logger)


@main_bp.route('/')
def home():
    """Home page"""
    try:
        logger.info("Home page accessed", extra={
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent')
        })

        return render_template('index.html')

    except Exception as e:
        logger.error("Error rendering home page", extra={
            "error": str(e),
            "remote_addr": request.remote_addr
        })
        return "Error loading page", 500


@main_bp.route('/api')
def api_info():
    """API information endpoint"""
    try:
        api_info = {
            "name": "WorkWave Coast API",
            "version": "1.0.0",
            "description": "API for WorkWave Coast job application system",
            "endpoints": {
                "applications": {
                    "POST /api/submit": "Submit a new application",
                    "GET /api/applications": "Get applications with pagination",
                    "GET /api/applications/{id}": "Get specific application",
                    "PUT /api/applications/{id}": "Update application",
                    "DELETE /api/applications/{id}": "Delete application",
                    "POST /api/applications/bulk-delete": "Delete multiple applications",
                    "GET /api/applications/statistics": "Get application statistics"
                },
                "admin": {
                    "POST /admin/login": "Admin login",
                    "POST /admin/logout": "Admin logout",
                    "GET /admin/dashboard": "Admin dashboard",
                    "GET /admin/api/stats": "Dashboard statistics",
                    "GET /admin/api/profile": "Admin profile",
                    "PUT /admin/api/profile": "Update admin profile",
                    "POST /admin/api/change-password": "Change admin password"
                },
                "files": {
                    "POST /api/upload": "Upload multiple files",
                    "POST /api/upload/{field}": "Upload single file",
                    "DELETE /api/delete/{public_id}": "Delete file",
                    "GET /api/info/{public_id}": "Get file info",
                    "GET /api/list": "List files",
                    "GET /api/signed-url/{public_id}": "Get signed URL",
                    "POST /api/validate": "Validate files",
                    "GET /api/health": "File service health check"
                },
                "utilities": {
                    "GET /api/health": "Overall health check",
                    "GET /api": "API information"
                }
            }
        }

        return jsonify(api_info), 200

    except Exception as e:
        logger.error("Error getting API info", extra={
            "error": str(e)
        })
        return jsonify({
            "error": "Internal server error"
        }), 500


@main_bp.route('/api/health')
def health_check():
    """Overall system health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Will be updated with actual timestamp
            "services": {}
        }

        # Check each service
        services_to_check = [
            ("application", app_service),
            ("admin", admin_service),
            ("file", file_service),
            ("email", email_service)
        ]

        overall_healthy = True

        for service_name, service in services_to_check:
            try:
                service_health = service.health_check()
                health_status["services"][service_name] = service_health

                if service_health.get("status") != "healthy":
                    overall_healthy = False

            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "service": service.__class__.__name__
                }
                overall_healthy = False

        # Set overall status
        health_status["status"] = "healthy" if overall_healthy else "unhealthy"

        # Update timestamp
        from datetime import datetime, timezone
        health_status["timestamp"] = datetime.now(timezone.utc).isoformat()

        status_code = 200 if overall_healthy else 503

        logger.info("Health check performed", extra={
            "overall_status": health_status["status"],
            "services_checked": len(services_to_check)
        })

        return jsonify(health_status), status_code

    except Exception as e:
        logger.error("Error in health check", extra={
            "error": str(e)
        })
        return jsonify({
            "status": "unhealthy",
            "error": "Health check failed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503


@main_bp.route('/api/version')
def version_info():
    """Get version information"""
    try:
        version_info = {
            "name": "WorkWave Coast",
            "version": "1.0.0",
            "api_version": "1.0",
            "build_date": "2024-01-01",
            "environment": "production",  # This could come from config
            "services": {
                "application_service": "1.0.0",
                "admin_service": "1.0.0",
                "file_service": "1.0.0",
                "email_service": "1.0.0"
            }
        }

        return jsonify(version_info), 200

    except Exception as e:
        logger.error("Error getting version info", extra={
            "error": str(e)
        })
        return jsonify({
            "error": "Internal server error"
        }), 500


@main_bp.route('/robots.txt')
def robots_txt():
    """Robots.txt file"""
    response = """User-agent: *
Disallow: /admin/
Disallow: /api/
Allow: /

Sitemap: https://workwavecoast.com/sitemap.xml
"""
    return response, 200, {'Content-Type': 'text/plain'}


@main_bp.route('/sitemap.xml')
def sitemap():
    """Basic sitemap"""
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://workwavecoast.com/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return sitemap_xml, 200, {'Content-Type': 'application/xml'}


# Error handlers for main blueprint
@main_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "message": "Endpoint not found",
            "path": request.path
        }), 404
    else:
        # For web requests, redirect to home page
        return render_template('404.html'), 404


@main_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "success": False,
        "message": "Method not allowed",
        "method": request.method,
        "path": request.path
    }), 405


@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error("Internal server error", extra={
        "path": request.path,
        "method": request.method,
        "remote_addr": request.remote_addr,
        "error": str(error)
    })

    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
    else:
        return render_template('500.html'), 500
