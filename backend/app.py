"""
WorkWave Coast Backend API
=========================

Flask application for managing job applications on the Croatian coast.
Handles file uploads to Cloudinary and stores application data in MongoDB Atlas.

Author: WorkWave Team
Version: 1.1.1 - Force Environment Variables Refresh
"""

import os
import json
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS for your custom domain
CORS(app, origins=[
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://workwavecoast.online",
    "http://www.workwavecoast.online",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5000"
], supports_credentials=True)

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['workwave']  # Database name
candidates = db['candidates']  # Collection name

# Cloudinary configuration (if needed)
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint that returns basic API information.

    Returns:
        dict: JSON response with API status and message
    """
    return jsonify({"message": "WorkWave Coast Backend API", "status": "running"})

@app.route('/api/submit', methods=['OPTIONS'])
@cross_origin(origins=[
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://workwavecoast.online",
    "http://www.workwavecoast.online"
], supports_credentials=True)
def submit_options():
    """Handle preflight OPTIONS request for CORS."""
    return '', 204

@app.route('/api/submit', methods=['POST'])
@cross_origin(origins=[
    "https://workwavecoast.online",
    "https://www.workwavecoast.online",
    "http://workwavecoast.online",
    "http://www.workwavecoast.online"
], supports_credentials=True)
def submit_application():
    """
    Submit a job application with form data and file uploads.

    Accepts form data and files, uploads files to Cloudinary if configured,
    and stores the application data in MongoDB.

    Returns:
        dict: JSON response with success status and application ID
    """
    try:
        print("=== Submit Application Debug ===")
        print(f"Request method: {request.method}")
        print(f"Request content type: {request.content_type}")
        print(f"Form data: {dict(request.form)}")
        print(f"Files: {list(request.files.keys())}")

        # Get form data
        data = request.form.to_dict()

        # Add timestamp
        data['created_at'] = datetime.utcnow().isoformat()
        data['status'] = 'pending'

        # File size limits (in bytes)
        file_size_limits = {
            'cv': 1024 * 1024,  # 1MB for CV
            'documentos': 2 * 1024 * 1024  # 2MB for additional documents
        }

        # Handle file uploads
        files = request.files
        file_urls = {}

        for field_name, file in files.items():
            if file and file.filename:
                print(f"Processing file: {field_name} - {file.filename}")
                file_size = 0  # Initialize file_size

                # Validate file size
                if field_name in file_size_limits:
                    try:
                        file.seek(0, 2)  # Seek to end
                        file_size = file.tell()
                        file.seek(0)  # Reset to beginning
                        print(f"File size: {file_size} bytes")
                    except Exception as e:
                        print(f"Error checking file size: {e}")
                        return jsonify({
                            "success": False,
                            "message": f"Error al procesar el archivo {field_name}"
                        }), 400

                    if file_size > file_size_limits[field_name]:
                        max_size_mb = file_size_limits[field_name] / (1024 * 1024)
                        return jsonify({
                            "success": False,
                            "message": (f"El archivo {field_name} es demasiado grande. "
                                       f"Máximo: {max_size_mb}MB")
                        }), 413

                # Upload to Cloudinary (if configured)
                cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
                print(f"Cloudinary cloud_name: {cloud_name}")

                if cloud_name and cloud_name != 'tu_cloud_name':
                    try:
                        print(f"Attempting to upload {field_name} to Cloudinary...")

                        # Upload with specific options for different file types
                        upload_options = {
                            'folder': 'workwave_coast',
                            'resource_type': 'auto',
                            'use_filename': True,
                            'unique_filename': True
                        }

                        # Add PDF-specific options for CVs
                        if (field_name == 'cv' and
                            file.filename.lower().endswith('.pdf')):
                            upload_options['format'] = 'pdf'
                            upload_options['pages'] = True  # Enable page count

                        print(f"Upload options: {upload_options}")
                        upload_result = cloudinary.uploader.upload(
                            file, **upload_options)
                        print(f"Upload successful: {upload_result.get('secure_url', 'No URL')}")

                        file_urls[field_name] = {
                            'url': upload_result['secure_url'],
                            'public_id': upload_result['public_id'],
                            'format': upload_result.get('format', ''),
                            'bytes': upload_result.get('bytes', 0),
                            'pages': (upload_result.get('pages', 1)
                                     if 'pages' in upload_result else 1),
                            'status': 'cloudinary_upload_success'
                        }

                    except Exception as e:
                        print(f"Error uploading {field_name} to Cloudinary: {e}")
                        # Fallback: save basic file info instead of failing
                        file_urls[field_name] = {
                            'filename': file.filename,
                            'size_bytes': file_size,
                            'status': 'cloudinary_upload_failed',
                            'error': str(e),
                            'note': 'File received but not uploaded to cloud storage'
                        }
                        print(f"Saved file info as fallback: {file_urls[field_name]}")
                else:
                    # Fallback: save basic file info if Cloudinary not configured
                    print(f"Cloudinary not configured, saving file info: {file.filename}")
                    file_urls[field_name] = {
                        'filename': file.filename,
                        'size_bytes': file_size,
                        'status': 'cloudinary_not_configured',
                        'note': 'File received but stored locally due to missing Cloudinary config'
                    }        # Add file URLs to data (convert to JSON string for MongoDB storage)
        data['files'] = json.dumps(file_urls) if file_urls else "{}"

        print(f"Final data to insert: {data}")
        print(f"MongoDB URI configured: {bool(MONGODB_URI)}")
        print(f"Database name: {db.name}")
        print(f"Collection name: candidates")

        # Insert into MongoDB
        result = candidates.insert_one(data)
        print(f"Insert result: {result.inserted_id}")

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "application_id": str(result.inserted_id)
        }), 201

    except (ValueError, KeyError, TypeError, ConnectionError, OSError,
            RuntimeError) as e:
        print(f"Error submitting application: {e}")
        return jsonify({
            "success": False,
            "message": "Error submitting application",
            "error": str(e)
        }), 500

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """
    Retrieve all job applications from the database.

    Returns:
        dict: JSON response with list of applications and count
    """
    try:
        # Get all applications
        applications = list(candidates.find({}, {"_id": 0}))

        return jsonify({
            "success": True,
            "applications": applications,
            "count": len(applications)
        })

    except (ConnectionError, TimeoutError) as e:
        print(f"Database connection error: {e}")
        return jsonify({
            "success": False,
            "message": "Database connection error",
            "error": str(e)
        }), 503
    except (ValueError, TypeError, OSError) as e:
        print(f"Unexpected error fetching applications: {e}")
        return jsonify({
            "success": False,
            "message": "Error fetching applications",
            "error": str(e)
        }), 500

@app.route('/api/applications/latest', methods=['GET'])
def get_latest_application():
    """
    Retrieve the most recent job application from the database.

    Returns:
        dict: JSON response with the latest application details
    """
    try:
        # Get the most recent application
        latest_app = candidates.find().sort('created_at', -1).limit(1)
        applications = list(latest_app)

        if applications:
            app = applications[0]
            # Convert ObjectId to string for JSON serialization
            app['_id'] = str(app['_id'])

            return jsonify({
                "success": True,
                "application": app
            })
        else:
            return jsonify({
                "success": True,
                "application": None,
                "message": "No applications found"
            })

    except (ConnectionError, TimeoutError, ValueError, TypeError, OSError,
            RuntimeError) as e:
        print(f"Error fetching latest application: {e}")
        return jsonify({
            "success": False,
            "message": "Error fetching latest application",
            "error": str(e)
        }), 500

@app.route('/api/test-cloudinary', methods=['GET'])
def test_cloudinary():
    """Test Cloudinary configuration and connection."""
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')

        response_data = {
            "success": False,
            "environment_variables": {
                "cloud_name": cloud_name if cloud_name else "NOT_SET",
                "api_key": "SET" if api_key else "NOT_SET",
                "api_secret": "SET" if api_secret else "NOT_SET"
            }
        }

        if not cloud_name or not api_key or not api_secret:
            response_data.update({
                "message": "Cloudinary environment variables not configured",
                "instructions": {
                    "step1": "Go to https://cloudinary.com and create a free account",
                    "step2": "Get your Cloud Name, API Key, and API Secret from the dashboard",
                    "step3": "Set these as environment variables in Render",
                    "variables_needed": ["CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"]
                }
            })
            return jsonify(response_data), 400

        # Test Cloudinary connection
        try:
            result = cloudinary.api.ping()

            response_data.update({
                "success": True,
                "message": "Cloudinary connection successful",
                "cloudinary_response": result
            })
            return jsonify(response_data)

        except Exception as cloudinary_error:
            response_data.update({
                "message": f"Cloudinary connection failed: {str(cloudinary_error)}",
                "possible_causes": [
                    "Invalid cloud_name - check if it matches your Cloudinary dashboard",
                    "Invalid API key or secret",
                    "Network connectivity issues",
                    "Cloudinary service temporarily unavailable"
                ],
                "current_cloud_name": cloud_name
            })
            return jsonify(response_data), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Unexpected error testing Cloudinary",
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify database connectivity.

    Tests the MongoDB connection and returns the health status.

    Returns:
        dict: JSON response with health status and timestamp
    """
    try:
        # Test MongoDB connection
        client.admin.command('ping')

        # Check Cloudinary configuration
        cloudinary_status = "configured" if (
            os.getenv('CLOUDINARY_CLOUD_NAME') and
            os.getenv('CLOUDINARY_CLOUD_NAME') != 'tu_cloud_name'
        ) else "not_configured"

        return jsonify({
            "status": "healthy",
            "mongodb": "connected",
            "cloudinary": cloudinary_status,
            "timestamp": datetime.utcnow().isoformat()
        })

    except (ConnectionError, TimeoutError) as e:
        return jsonify({
            "status": "unhealthy",
            "mongodb": "disconnected",
            "cloudinary": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503
    except (ValueError, TypeError, OSError, RuntimeError) as e:
        return jsonify({
            "status": "unhealthy",
            "mongodb": "unknown_error",
            "cloudinary": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
