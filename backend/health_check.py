#!/usr/bin/env python3
"""
Health check script for WorkWave Coast Backend
Verifies all dependencies and configurations before deployment
"""

import sys
import os
import traceback

def check_environment():
    """Check environment variables"""
    print("🔍 Checking environment variables...")

    required_vars = [
        'MONGODB_URI',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False

    print("✅ All required environment variables are set")
    return True

def check_imports():
    """Check if all required packages can be imported"""
    print("🔍 Checking Python imports...")

    try:
        import flask
        import pymongo
        import cloudinary
        import gunicorn
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_mongodb():
    """Check MongoDB connection"""
    print("🔍 Checking MongoDB connection...")

    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def check_cloudinary():
    """Check Cloudinary configuration"""
    print("🔍 Checking Cloudinary configuration...")

    try:
        import cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        print("✅ Cloudinary configuration successful")
        return True
    except Exception as e:
        print(f"❌ Cloudinary configuration failed: {e}")
        return False

def main():
    """Run all health checks"""
    print("🏥 WorkWave Coast Backend Health Check")
    print("=" * 50)

    checks = [
        check_environment,
        check_imports,
        check_mongodb,
        check_cloudinary
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Error in {check.__name__}: {e}")
            traceback.print_exc()
            results.append(False)
        print()

    if all(results):
        print("🎉 All health checks passed! Backend is ready for deployment.")
        sys.exit(0)
    else:
        print("💥 Some health checks failed. Please fix the issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
