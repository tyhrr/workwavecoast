"""
WorkWave Coast Backend API
=========================

Flask application for managing job applications on the Croatian coast.
Handles file uploads to Cloudinary and stores application data in MongoDB Atlas.

Author: WorkWave Team
Version: 1.0.0
"""

import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

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
])

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

@app.route('/api/submit', methods=['POST'])
def submit_application():
    """
    Submit a job application with form data and file uploads.

    Accepts form data and files, uploads files to Cloudinary if configured,
    and stores the application data in MongoDB.

    Returns:
        dict: JSON response with success status and application ID
    """
    try:
        # Get form data
        data = request.form.to_dict()

        # Add timestamp
        data['created_at'] = datetime.utcnow().isoformat()
        data['status'] = 'pending'

        # File size limits (in bytes)
        FILE_SIZE_LIMITS = {
            'cv': 1024 * 1024,  # 1MB for CV
            'documentos': 2 * 1024 * 1024  # 2MB for additional documents
        }

        # Handle file uploads
        files = request.files
        file_urls = {}

        for field_name, file in files.items():
            if file and file.filename:
                # Validate file size
                if field_name in FILE_SIZE_LIMITS:
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    if file_size > FILE_SIZE_LIMITS[field_name]:
                        max_size_mb = FILE_SIZE_LIMITS[field_name] / (1024 * 1024)
                        return jsonify({
                            "success": False,
                            "message": f"El archivo {field_name} es demasiado grande. Máximo: {max_size_mb}MB"
                        }), 413

                # Upload to Cloudinary (if configured)
                if os.getenv('CLOUDINARY_CLOUD_NAME') and os.getenv('CLOUDINARY_CLOUD_NAME') != 'tu_cloud_name':
                    try:
                        # Upload with specific options for different file types
                        upload_options = {
                            'folder': 'workwave_coast',
                            'resource_type': 'auto',
                            'use_filename': True,
                            'unique_filename': True
                        }
                        
                        # Add PDF-specific options for CVs
                        if field_name == 'cv' and file.filename.lower().endswith('.pdf'):
                            upload_options['format'] = 'pdf'
                            upload_options['pages'] = True  # Enable page count
                        
                        upload_result = cloudinary.uploader.upload(file, **upload_options)
                        
                        file_urls[field_name] = {
                            'url': upload_result['secure_url'],
                            'public_id': upload_result['public_id'],
                            'format': upload_result.get('format', ''),
                            'bytes': upload_result.get('bytes', 0),
                            'pages': upload_result.get('pages', 1) if 'pages' in upload_result else 1
                        }
                        
                    except Exception as e:
                        print(f"Error uploading {field_name} to Cloudinary: {e}")
                        return jsonify({
                            "success": False,
                            "message": f"Error uploading {field_name}. Please try again."
                        }), 500
                else:
                    # Fallback: save basic file info if Cloudinary not configured
                    file_urls[field_name] = {
                        'filename': file.filename,
                        'note': 'Cloudinary not configured'
                    }

        # Add file URLs to data
        data['files'] = file_urls

        # Insert into MongoDB
        result = candidates.insert_one(data)

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "application_id": str(result.inserted_id)
        }), 201

    except Exception as e:
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
