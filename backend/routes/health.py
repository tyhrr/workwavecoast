"""
Health Check Routes
System health monitoring endpoints
"""
import logging
from flask import Blueprint, jsonify
from services import ApplicationService, AdminService, FileService, EmailService

# Create blueprint
health_bp = Blueprint('health', __name__)

# Initialize logger
logger = logging.getLogger(__name__)

@health_bp.route('/health')
def health_check():
    """Overall system health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": None,
            "services": {
                "application": {"status": "unknown"},
                "admin": {"status": "unknown"},
                "file": {"status": "unknown"},
                "email": {"status": "unknown"}
            },
            "database": {"status": "unknown"}
        }

        # Initialize services with logger
        app_service = ApplicationService(logger)
        admin_service = AdminService(logger)
        file_service = FileService(logger)
        email_service = EmailService(logger)

        # Check application service
        try:
            app_health = app_service.health_check()
            health_status["services"]["application"] = app_health
        except Exception as e:
            health_status["services"]["application"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check admin service
        try:
            admin_health = admin_service.health_check()
            health_status["services"]["admin"] = admin_health
        except Exception as e:
            health_status["services"]["admin"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check file service
        try:
            file_health = file_service.health_check()
            health_status["services"]["file"] = file_health
        except Exception as e:
            health_status["services"]["file"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check email service
        try:
            email_health = email_service.health_check()
            health_status["services"]["email"] = email_health
        except Exception as e:
            health_status["services"]["email"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Add timestamp
        from datetime import datetime, timezone
        health_status["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Determine overall status
        service_statuses = [service.get("status") for service in health_status["services"].values()]
        if any(status == "unhealthy" for status in service_statuses):
            health_status["status"] = "degraded"
        elif any(status == "unknown" for status in service_statuses):
            health_status["status"] = "unknown"
        else:
            health_status["status"] = "healthy"

        logger.info("Health check completed", extra={
            "overall_status": health_status["status"],
            "service_count": len(health_status["services"])
        })

        return jsonify(health_status), 200

    except Exception as e:
        logger.error("Health check failed", extra={
            "error": str(e)
        })
        return jsonify({
            "status": "unhealthy",
            "error": "Health check failed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@health_bp.route('/health/quick')
def quick_health():
    """Quick health check - just returns 200 OK"""
    return jsonify({"status": "ok"}), 200

@health_bp.route('/api/info')
def api_info():
    """API information endpoint"""
    try:
        api_info = {
            "name": "WorkWave Coast API",
            "version": "1.0.0",
            "description": "API for WorkWave Coast job application system",
            "endpoints": {
                "applications": {
                    "GET /applications": "List applications",
                    "POST /applications": "Create application",
                    "GET /applications/{id}": "Get application by ID",
                    "PUT /applications/{id}": "Update application",
                    "DELETE /applications/{id}": "Delete application",
                    "PUT /applications/{id}/status": "Update application status",
                    "GET /applications/export": "Export applications"
                },
                "admin": {
                    "POST /admin/login": "Admin login",
                    "POST /admin/logout": "Admin logout",
                    "GET /admin/profile": "Get admin profile",
                    "PUT /admin/profile": "Update admin profile",
                    "PUT /admin/change-password": "Change admin password",
                    "GET /admin/dashboard": "Get dashboard statistics"
                },
                "files": {
                    "POST /files/upload": "Upload file",
                    "GET /files/{filename}": "Download file",
                    "DELETE /files/{filename}": "Delete file",
                    "GET /files": "List files"
                },
                "utilities": {
                    "GET /health": "Overall health check",
                    "GET /health/quick": "Quick health check",
                    "GET /api/info": "API information"
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
