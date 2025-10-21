"""
API Routes
Main API endpoints for application management
"""
import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.exceptions import BadRequest
from services import ApplicationService, FileService, EmailService
from middleware import (
    handle_api_errors,
    validate_json_schema,
    validate_application_form,
    validate_file_upload,
    log_requests,
    log_user_actions
)
from utils.rate_limiter import api_rate_limit, strict_rate_limit

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
app_service = ApplicationService(logger)
file_service = FileService(logger)
email_service = EmailService(logger)


@api_bp.route('/submit', methods=['GET', 'POST'])
@api_rate_limit()
@log_requests()
@log_user_actions('submit', 'application')
def submit_application():
    """Handle application submission"""
    if request.method == 'GET':
        # Render the application form
        return render_template('index.html')

    elif request.method == 'POST':
        try:
            # Log submission attempt
            logger.info("New application submission attempt", extra={
                "endpoint": "/api/submit",
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get('User-Agent')
            })

            # Get form data
            form_data = request.form.to_dict()
            files = request.files

            logger.info("Received form data", extra={
                "data_keys": list(form_data.keys()),
                "files_received": list(files.keys())
            })

            # Validate form data using service
            try:
                validation_result = app_service.validate_application_data(form_data)
                if not validation_result[0]:  # validation failed
                    logger.warning("Application validation failed", extra={
                        "validation_errors": validation_result[1]
                    })

                    return jsonify({
                        "success": False,
                        "error": validation_result[1],
                        "error_type": "ValidationError"
                    }), 400
            except Exception as e:
                logger.error(f"Validation error: {e}", exc_info=True)
                return jsonify({
                    "success": False,
                    "error": f"Error en validación: {str(e)}",
                    "error_type": "ValidationError"
                }), 400

            # Process application with service
            try:
                result = app_service.create_application(form_data, files)
            except Exception as e:
                logger.error(f"Application creation error: {e}", exc_info=True)
                return jsonify({
                    "success": False,
                    "error": f"Error al crear aplicación: {str(e)}",
                    "error_type": "ServerError"
                }), 500

            if result["success"]:
                logger.info("Application created successfully", extra={
                    "application_id": result["data"].get("_id")
                })
                return jsonify(result), 201
            else:
                logger.error("Application creation failed", extra={
                    "error": result.get("error", "Unknown error")
                })
                return jsonify(result), 400

        except Exception as e:
            logger.error(f"Unexpected error in submit_application: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Error inesperado del servidor: {str(e)}",
                "error_type": "ServerError"
            }), 500
                else:
                    flash(f"Error al enviar aplicación: {result['error']}", 'error')
                    return redirect(url_for('main.home'))

        except BadRequest as e:
            logger.error("Bad request in application submission", extra={
                "error": str(e),
                "form_data": request.form.to_dict() if request.form else {}
            })

            if request.is_json:
                return jsonify({
                    "success": False,
                    "error": "Invalid request data",
                    "error_type": "BadRequest"
                }), 400
            else:
                flash("Datos de solicitud inválidos", 'error')
                return redirect(url_for('main.home'))

        except Exception as e:
            logger.error("Unexpected error in application submission", extra={
                "error": str(e),
                "form_data": request.form.to_dict() if request.form else {}
            })

            if request.is_json:
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "error_type": "InternalError"
                }), 500
            else:
                flash("Error interno del servidor", 'error')
                return redirect(url_for('main.home'))


@api_bp.route('/applications', methods=['GET'])
@api_rate_limit()
@handle_api_errors
def list_applications():
    """List all applications with pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        search = request.args.get('search')

        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        # Get applications using service
        result = app_service.get_applications(
            page=page,
            per_page=per_page,
            status=status,
            search=search
        )

        if result["success"]:
            logger.info("Applications retrieved successfully", extra={
                "page": page,
                "per_page": per_page,
                "total": result["data"]["pagination"]["total"]
            })
            return jsonify(result), 200
        else:
            logger.error("Failed to retrieve applications", extra={
                "error": result["error"]
            })
            return jsonify(result), 500

    except Exception as e:
        logger.error("Error listing applications", extra={
            "error": str(e),
            "page": page,
            "per_page": per_page
        })
        return jsonify({
            "success": False,
            "error": "Failed to retrieve applications",
            "error_type": "InternalError"
        }), 500


@api_bp.route('/applications/<application_id>', methods=['GET'])
@api_rate_limit()
@handle_api_errors
def get_application(application_id):
    """Get specific application by ID"""
    try:
        result = app_service.get_application_by_id(application_id)

        if result["success"]:
            logger.info("Application retrieved successfully", extra={
                "application_id": application_id
            })
            return jsonify(result), 200
        else:
            logger.warning("Application not found", extra={
                "application_id": application_id,
                "error": result["error"]
            })
            return jsonify(result), 404

    except Exception as e:
        logger.error("Error retrieving application", extra={
            "error": str(e),
            "application_id": application_id
        })
        return jsonify({
            "success": False,
            "error": "Failed to retrieve application",
            "error_type": "InternalError"
        }), 500


@api_bp.route('/applications/<application_id>', methods=['PUT'])
@api_rate_limit()
@validate_json_schema()
@handle_api_errors
def update_application(application_id):
    """Update application"""
    try:
        update_data = request.get_json()

        result = app_service.update_application(application_id, update_data)

        if result["success"]:
            logger.info("Application updated successfully", extra={
                "application_id": application_id,
                "updated_fields": list(update_data.keys())
            })
            return jsonify(result), 200
        else:
            logger.error("Failed to update application", extra={
                "application_id": application_id,
                "error": result["error"]
            })
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error updating application", extra={
            "error": str(e),
            "application_id": application_id
        })
        return jsonify({
            "success": False,
            "error": "Failed to update application",
            "error_type": "InternalError"
        }), 500


@api_bp.route('/applications/<application_id>', methods=['DELETE'])
@strict_rate_limit()
@handle_api_errors
def delete_application(application_id):
    """Delete application"""
    try:
        result = app_service.delete_application(application_id)

        if result["success"]:
            logger.info("Application deleted successfully", extra={
                "application_id": application_id
            })
            return jsonify(result), 200
        else:
            logger.error("Failed to delete application", extra={
                "application_id": application_id,
                "error": result["error"]
            })
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error deleting application", extra={
            "error": str(e),
            "application_id": application_id
        })
        return jsonify({
            "success": False,
            "error": "Failed to delete application",
            "error_type": "InternalError"
        }), 500


@api_bp.route('/applications/<application_id>/status', methods=['PUT'])
@api_rate_limit()
@validate_json_schema(['status'])
@handle_api_errors
def update_application_status(application_id):
    """Update application status"""
    try:
        data = request.get_json()
        new_status = data['status']

        result = app_service.update_application_status(application_id, new_status)

        if result["success"]:
            logger.info("Application status updated successfully", extra={
                "application_id": application_id,
                "new_status": new_status
            })
            return jsonify(result), 200
        else:
            logger.error("Failed to update application status", extra={
                "application_id": application_id,
                "new_status": new_status,
                "error": result["error"]
            })
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error updating application status", extra={
            "error": str(e),
            "application_id": application_id
        })
        return jsonify({
            "success": False,
            "error": "Failed to update application status",
            "error_type": "InternalError"
        }), 500


@api_bp.route('/applications/export', methods=['GET'])
@strict_rate_limit()
@handle_api_errors
def export_applications():
    """Export applications to Excel"""
    try:
        # Get query parameters for filtering
        status = request.args.get('status')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        result = app_service.export_applications(
            status=status,
            from_date=from_date,
            to_date=to_date
        )

        if result["success"]:
            logger.info("Applications exported successfully", extra={
                "status_filter": status,
                "from_date": from_date,
                "to_date": to_date
            })
            return jsonify(result), 200
        else:
            logger.error("Failed to export applications", extra={
                "error": result["error"]
            })
            return jsonify(result), 500

    except Exception as e:
        logger.error("Error exporting applications", extra={
            "error": str(e)
        })
        return jsonify({
            "success": False,
            "error": "Failed to export applications",
            "error_type": "InternalError"
        }), 500
