"""
Application Routes
Flask routes for application management
"""
import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.exceptions import BadRequest
from services import ApplicationService, FileService, EmailService

# Create blueprint
applications_bp = Blueprint('applications', __name__, url_prefix='/api')

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
app_service = ApplicationService(logger)
file_service = FileService(logger)
email_service = EmailService(logger)


@applications_bp.route('/submit', methods=['GET', 'POST'])
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
                "data_values": form_data,
                "files_received": list(files.keys())
            })

            # Validate form data using service
            validation_result = app_service.validate_application_data(form_data)
            if not validation_result[0]:  # validation failed
                logger.warning("Invalid application data submitted", extra={
                    "errors": validation_result[1],
                    "remote_addr": request.remote_addr
                })
                return jsonify({
                    "success": False,
                    "errors": validation_result[1]
                }), 400

            # Process file uploads if any
            files_info = {}
            if files:
                upload_result = file_service.upload_multiple_files(files)
                if upload_result.get('success'):
                    files_info = upload_result['data'].get('files', {})
                    if upload_result['data'].get('errors'):
                        logger.warning("Some files failed to upload", extra={
                            "errors": upload_result['data']['errors']
                        })
                else:
                    logger.error("File upload failed", extra={
                        "error": upload_result.get('message', 'Unknown error')
                    })
                    return jsonify({
                        "success": False,
                        "message": "Error uploading files: " + upload_result.get('message', 'Unknown error')
                    }), 500

            # Create application using service
            create_result = app_service.create_application(form_data, files_info)
            if not create_result.get('success'):
                logger.error("Failed to create application", extra={
                    "error": create_result.get('message'),
                    "error_type": create_result.get('error_type'),
                    "email": form_data.get('email')
                })
                # Return error with full details
                return jsonify({
                    "success": False,
                    "error": create_result.get('message', 'Failed to create application'),
                    "error_type": create_result.get('error_type', 'ApplicationError'),
                    "details": create_result.get('details')
                }), 400

            # Send confirmation email
            logger.info("Attempting to send confirmation email", extra={
                "email": form_data.get('email'),
                "nombre": form_data.get('nombre')
            })
            
            email_result = email_service.send_confirmation_email(form_data)
            
            if email_result.get('success'):
                logger.info("Confirmation email sent successfully", extra={
                    "email": form_data.get('email')
                })
            else:
                logger.error("Failed to send confirmation email", extra={
                    "error": email_result.get('message'),
                    "error_type": email_result.get('error_type'),
                    "email": form_data.get('email'),
                    "full_result": email_result
                })

            # Send admin notification
            logger.info("Attempting to send admin notification")
            
            admin_email_result = email_service.send_admin_notification(form_data, files_info)
            
            if admin_email_result.get('success'):
                logger.info("Admin notification sent successfully")
            else:
                logger.error("Failed to send admin notification", extra={
                    "error": admin_email_result.get('message'),
                    "error_type": admin_email_result.get('error_type'),
                    "full_result": admin_email_result
                })

            logger.info("Application submitted successfully", extra={
                "application_id": create_result['data']['_id'],
                "email": form_data.get('email'),
                "puesto": form_data.get('puesto')
            })

            return jsonify({
                "success": True,
                "message": "Aplicación enviada exitosamente",
                "application_id": create_result['data']['_id']
            }), 200

        except BadRequest as e:
            logger.error("Bad request in application submission", extra={
                "error": str(e),
                "remote_addr": request.remote_addr
            })
            return jsonify({
                "success": False,
                "message": "Solicitud incorrecta"
            }), 400

        except Exception as e:
            logger.error("Unexpected error in application submission", extra={
                "error": str(e),
                "remote_addr": request.remote_addr
            })
            return jsonify({
                "success": False,
                "message": "Error interno del servidor"
            }), 500


@applications_bp.route('/applications', methods=['GET'])
def get_applications():
    """Get applications with pagination and filtering"""
    try:
        # Get query parameters
        query_params = {
            'page': int(request.args.get('page', 1)),
            'per_page': min(100, int(request.args.get('per_page', 10))),
            'search': request.args.get('search', '').strip(),
            'status': request.args.get('status', '').strip(),
            'puesto': request.args.get('puesto', '').strip(),
            'ingles_nivel': request.args.get('ingles_nivel', '').strip(),
            'nacionalidad': request.args.get('nacionalidad', '').strip(),
            'sort_by': request.args.get('sort_by', 'created_at'),
            'sort_order': request.args.get('sort_order', 'desc')
        }

        # Remove empty values
        query_params = {k: v for k, v in query_params.items() if v}

        # Get applications using service
        result = app_service.get_applications(query_params)

        if result.get('success'):
            return jsonify(result['data']), 200
        else:
            return jsonify(result), 400

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": "Invalid query parameters"
        }), 400

    except Exception as e:
        logger.error("Error getting applications", extra={
            "error": str(e),
            "query_params": request.args.to_dict()
        })
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


@applications_bp.route('/applications/<string:application_id>', methods=['GET'])
def get_application(application_id):
    """Get a single application by ID"""
    try:
        result = app_service.get_application_by_id(application_id)

        if result.get('success'):
            return jsonify(result['data']), 200
        else:
            status_code = 404 if 'not found' in result.get('message', '').lower() else 400
            return jsonify(result), status_code

    except Exception as e:
        logger.error("Error getting application", extra={
            "error": str(e),
            "application_id": application_id
        })
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


@applications_bp.route('/applications/<string:application_id>', methods=['PUT', 'PATCH'])
def update_application(application_id):
    """Update an application"""
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        result = app_service.update_application(application_id, update_data)

        if result.get('success'):
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result.get('message', '').lower() else 400
            return jsonify(result), status_code

    except Exception as e:
        logger.error("Error updating application", extra={
            "error": str(e),
            "application_id": application_id
        })
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


@applications_bp.route('/applications/<string:application_id>', methods=['DELETE'])
def delete_application(application_id):
    """Delete an application"""
    try:
        result = app_service.delete_application(application_id)

        if result.get('success'):
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result.get('message', '').lower() else 400
            return jsonify(result), status_code

    except Exception as e:
        logger.error("Error deleting application", extra={
            "error": str(e),
            "application_id": application_id
        })
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


@applications_bp.route('/applications/bulk-delete', methods=['POST'])
def bulk_delete_applications():
    """Delete multiple applications"""
    try:
        data = request.get_json()
        if not data or not data.get('application_ids'):
            return jsonify({
                "success": False,
                "message": "No application IDs provided"
            }), 400

        application_ids = data['application_ids']
        if not isinstance(application_ids, list):
            return jsonify({
                "success": False,
                "message": "Application IDs must be a list"
            }), 400

        result = app_service.delete_multiple_applications(application_ids)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error in bulk delete", extra={
            "error": str(e),
            "data": request.get_json()
        })
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


@applications_bp.route('/applications/statistics', methods=['GET'])
def get_statistics():
    """Get application statistics"""
    try:
        result = app_service.get_application_statistics()

        if result.get('success'):
            return jsonify(result['data']), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error getting statistics", extra={
            "error": str(e)
        })
        return jsonify({
            "success": False,
            "message": "Error interno del servidor"
        }), 500


# Error handlers for this blueprint
@applications_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "message": "Solicitud incorrecta"
    }), 400


@applications_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "Recurso no encontrado"
    }), 404


@applications_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "Error interno del servidor"
    }), 500
