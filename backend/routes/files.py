"""
File Routes
Flask routes for file operations and Cloudinary proxy
"""
import logging
from flask import Blueprint, request, jsonify, redirect, url_for
from services import FileService

# Create blueprint
files_bp = Blueprint('files', __name__, url_prefix='/api')

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
file_service = FileService(logger)


@files_bp.route('/upload', methods=['POST'])
def upload_files():
    """Upload files to Cloudinary"""
    try:
        # Check if files were uploaded
        if not request.files:
            return jsonify({
                "success": False,
                "message": "No files provided"
            }), 400

        logger.info("File upload request", extra={
            "files": list(request.files.keys()),
            "remote_addr": request.remote_addr
        })

        # Upload files using service
        result = file_service.upload_multiple_files(request.files)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error uploading files", extra={
            "error": str(e),
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/upload/<string:field_name>', methods=['POST'])
def upload_single_file(field_name):
    """Upload a single file for a specific field"""
    try:
        # Check if file was uploaded
        if field_name not in request.files:
            return jsonify({
                "success": False,
                "message": f"No file provided for field {field_name}"
            }), 400

        file = request.files[field_name]
        if not file.filename:
            return jsonify({
                "success": False,
                "message": "No file selected"
            }), 400

        logger.info("Single file upload request", extra={
            "field_name": field_name,
            "filename": file.filename,
            "remote_addr": request.remote_addr
        })

        # Upload file using service
        result = file_service.upload_to_cloudinary(file, field_name)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error uploading single file", extra={
            "error": str(e),
            "field_name": field_name,
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/delete/<string:public_id>', methods=['DELETE'])
def delete_file(public_id):
    """Delete a file from Cloudinary"""
    try:
        # Get resource type from query params (default to auto)
        resource_type = request.args.get('resource_type', 'auto')

        logger.info("File deletion request", extra={
            "public_id": public_id,
            "resource_type": resource_type,
            "remote_addr": request.remote_addr
        })

        # Delete file using service
        result = file_service.delete_file(public_id, resource_type)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error deleting file", extra={
            "error": str(e),
            "public_id": public_id,
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/info/<string:public_id>', methods=['GET'])
def get_file_info(public_id):
    """Get information about a file"""
    try:
        # Get resource type from query params (default to auto)
        resource_type = request.args.get('resource_type', 'auto')

        # Get file info using service
        result = file_service.get_file_info(public_id, resource_type)

        if result.get('success'):
            return jsonify(result['data']), 200
        else:
            status_code = 404 if 'not found' in result.get('message', '').lower() else 400
            return jsonify(result), status_code

    except Exception as e:
        logger.error("Error getting file info", extra={
            "error": str(e),
            "public_id": public_id,
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/list', methods=['GET'])
def list_files():
    """List files in Cloudinary"""
    try:
        # Get query parameters
        folder = request.args.get('folder', 'workwave')
        max_results = min(500, int(request.args.get('max_results', 100)))

        # List files using service
        result = file_service.list_files(folder, max_results)

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
        logger.error("Error listing files", extra={
            "error": str(e),
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/signed-url/<string:public_id>', methods=['GET'])
def get_signed_url(public_id):
    """Get a signed URL for private file access"""
    try:
        # Get expiration time from query params (default to 1 hour)
        expiration_time = int(request.args.get('expiration_time', 3600))

        # Generate signed URL using service
        result = file_service.generate_signed_url(public_id, expiration_time)

        if result.get('success'):
            return jsonify(result['data']), 200
        else:
            return jsonify(result), 400

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": "Invalid expiration time"
        }), 400

    except Exception as e:
        logger.error("Error generating signed URL", extra={
            "error": str(e),
            "public_id": public_id,
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/cloudinary/<path:filename>')
def cloudinary_proxy(filename):
    """Proxy for Cloudinary files (legacy endpoint)"""
    try:
        # This is a legacy endpoint that redirects to Cloudinary
        # In the future, this could be enhanced to provide access control

        logger.info("Cloudinary proxy request", extra={
            "filename": filename,
            "remote_addr": request.remote_addr
        })

        # For now, just construct the Cloudinary URL and redirect
        # This maintains compatibility with existing frontend code
        cloudinary_url = f"https://res.cloudinary.com/workwave/{filename}"
        return redirect(cloudinary_url)

    except Exception as e:
        logger.error("Error in Cloudinary proxy", extra={
            "error": str(e),
            "filename": filename,
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "File not found"
        }), 404


@files_bp.route('/validate', methods=['POST'])
def validate_files():
    """Validate files without uploading"""
    try:
        # Check if files were provided
        if not request.files:
            return jsonify({
                "success": False,
                "message": "No files provided"
            }), 400

        results = {}
        all_valid = True

        for field_name, file in request.files.items():
            if file.filename:
                is_valid, error_message, file_size = file_service.validate_file(file, field_name)
                results[field_name] = {
                    "valid": is_valid,
                    "error": error_message,
                    "size": file_size,
                    "filename": file.filename
                }
                if not is_valid:
                    all_valid = False
            else:
                results[field_name] = {
                    "valid": False,
                    "error": "No file selected",
                    "size": 0,
                    "filename": ""
                }
                all_valid = False

        return jsonify({
            "success": all_valid,
            "results": results,
            "message": "Validation complete" if all_valid else "Some files failed validation"
        }), 200

    except Exception as e:
        logger.error("Error validating files", extra={
            "error": str(e),
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/health', methods=['GET'])
def health_check():
    """Check file service health"""
    try:
        health = file_service.health_check()

        if health.get('status') == 'healthy':
            return jsonify(health), 200
        else:
            return jsonify(health), 503

    except Exception as e:
        logger.error("Error in file service health check", extra={
            "error": str(e)
        })
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "service": "FileService"
        }), 503


@files_bp.route('/preview/<string:public_id>', methods=['GET'])
def get_file_preview(public_id):
    """Get file preview information for admin panel"""
    try:
        # Get resource type from query params (default to auto)
        resource_type = request.args.get('resource_type', 'auto')

        logger.info("File preview request", extra={
            "public_id": public_id,
            "resource_type": resource_type,
            "remote_addr": request.remote_addr
        })

        # Get preview info using service
        result = file_service.get_file_preview_info(public_id, resource_type)

        if result.get('success'):
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result.get('message', '').lower() else 400
            return jsonify(result), status_code

    except Exception as e:
        logger.error("Error getting file preview", extra={
            "error": str(e),
            "public_id": public_id,
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/stats', methods=['GET'])
def get_file_stats():
    """Get file usage statistics"""
    try:
        folder = request.args.get('folder', 'workwave')

        logger.info("File stats request", extra={
            "folder": folder,
            "remote_addr": request.remote_addr
        })

        # Get stats using service
        result = file_service.get_file_stats(folder)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error getting file stats", extra={
            "error": str(e),
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@files_bp.route('/signed-url/<string:public_id>', methods=['GET'])
def generate_signed_url(public_id):
    """Generate a signed URL for secure file access"""
    try:
        expiration_time = int(request.args.get('expires_in', 3600))  # Default 1 hour

        logger.info("Signed URL request", extra={
            "public_id": public_id,
            "expiration_time": expiration_time,
            "remote_addr": request.remote_addr
        })

        # Generate signed URL using service
        result = file_service.generate_signed_url(public_id, expiration_time)

        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error("Error generating signed URL", extra={
            "error": str(e),
            "public_id": public_id,
            "remote_addr": request.remote_addr
        })
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


# Error handlers for this blueprint
@files_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "message": "Bad request"
    }), 400


@files_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "File not found"
    }), 404


@files_bp.errorhandler(413)  # Payload Too Large
def payload_too_large(error):
    return jsonify({
        "success": False,
        "message": "File too large"
    }), 413


@files_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500
