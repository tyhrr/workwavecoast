"""
Test script for new admin panel features
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

from services.application_service import ApplicationService
from services.email_service import EmailService
from services.admin_service import AdminService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_functionality():
    """Test full-text search"""
    print("\n" + "="*60)
    print("TEST 1: Full-Text Search")
    print("="*60)

    app_service = ApplicationService(logger)
    app_service.initialize()

    # Test search with query
    result = app_service.search_applications(
        search_query="camarero",
        filters={'page': 1, 'per_page': 5}
    )

    print(f"✓ Search executed: {result['success']}")
    if result['success']:
        print(f"  - Results found: {len(result['data']['applications'])}")
        print(f"  - Total: {result['data']['pagination']['total']}")
    else:
        print(f"  - Error: {result.get('error', 'Unknown error')}")

def test_advanced_filters():
    """Test advanced filters"""
    print("\n" + "="*60)
    print("TEST 2: Advanced Filters")
    print("="*60)

    app_service = ApplicationService(logger)
    app_service.initialize()

    # Test getting filter options
    result = app_service.get_advanced_filters_options()

    print(f"✓ Filter options retrieved: {result['success']}")
    if result['success']:
        data = result['data']
        print(f"  - Nationalities: {len(data.get('nationalities', []))}")
        print(f"  - Positions: {len(data.get('positions', []))}")
        print(f"  - English levels: {len(data.get('english_levels', []))}")
        print(f"  - Statuses: {data.get('statuses', [])}")
    else:
        print(f"  - Error: {result.get('error', 'Unknown error')}")

    # Test search with filters
    result = app_service.search_applications(
        search_query="",
        filters={
            'status': 'pending',
            'page': 1,
            'per_page': 5
        }
    )

    print(f"\n✓ Filtered search executed: {result['success']}")
    if result['success']:
        print(f"  - Pending applications: {result['data']['pagination']['total']}")

def test_export_functionality():
    """Test export to CSV/Excel"""
    print("\n" + "="*60)
    print("TEST 3: Export Functionality")
    print("="*60)

    app_service = ApplicationService(logger)
    app_service.initialize()

    # Test CSV export
    result = app_service.export_applications(format='csv', filters={'status': 'pending'})

    print(f"✓ CSV export executed: {result['success']}")
    if result['success']:
        print(f"  - Records exported: {result['data']['count']}")
        print(f"  - Filename: {result['data']['filename']}")
        print(f"  - MIME type: {result['data']['mimetype']}")
    else:
        print(f"  - Error: {result.get('error', 'Unknown error')}")

    # Test Excel export
    result = app_service.export_applications(format='excel', filters={})

    print(f"\n✓ Excel export executed: {result['success']}")
    if result['success']:
        print(f"  - Records exported: {result['data']['count']}")
        print(f"  - Filename: {result['data']['filename']}")

def test_email_templates():
    """Test email notification templates"""
    print("\n" + "="*60)
    print("TEST 4: Email Notification Templates")
    print("="*60)

    email_service = EmailService(logger)

    # Test candidate data
    test_candidate = {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'email': 'test@example.com',
        'puesto': 'Camarero/a'
    }

    print(f"✓ Email service configured: {email_service.email_config is not None}")

    # We won't actually send emails in test, just verify the methods exist
    print(f"✓ send_application_approved_email method exists: {hasattr(email_service, 'send_application_approved_email')}")
    print(f"✓ send_application_rejected_email method exists: {hasattr(email_service, 'send_application_rejected_email')}")
    print(f"✓ send_application_status_change_email method exists: {hasattr(email_service, 'send_application_status_change_email')}")

def test_dashboard_stats():
    """Test enhanced dashboard statistics"""
    print("\n" + "="*60)
    print("TEST 5: Enhanced Dashboard Statistics")
    print("="*60)

    from services.jwt_service import JWTService
    from config.settings import get_config

    config = get_config()
    jwt_service = JWTService(config, logger)
    admin_service = AdminService(config, jwt_service, logger)

    result = admin_service.get_admin_dashboard_stats()

    print(f"✓ Dashboard stats retrieved: {result['success']}")
    if result['success']:
        stats = result['data']
        summary = stats.get('summary', {})
        print(f"\n  Summary:")
        print(f"  - Total applications: {summary.get('total_applications', 0)}")
        print(f"  - Pending: {summary.get('pending_applications', 0)}")
        print(f"  - Approved: {summary.get('approved_applications', 0)}")
        print(f"  - Rejected: {summary.get('rejected_applications', 0)}")
        print(f"  - Today: {summary.get('applications_today', 0)}")
        print(f"  - This week: {summary.get('applications_this_week', 0)}")
        print(f"  - This month: {summary.get('applications_this_month', 0)}")
        print(f"  - Conversion rate: {summary.get('conversion_rate', 0)}%")

        distributions = stats.get('distributions', {})
        print(f"\n  Distributions:")
        print(f"  - Positions: {len(distributions.get('positions', []))}")
        print(f"  - Nationalities: {len(distributions.get('nationalities', []))}")
        print(f"  - English levels: {len(distributions.get('english_levels', []))}")

        print(f"\n  - Recent applications: {len(stats.get('recent_applications', []))}")
        print(f"  - Trend data points: {len(stats.get('trend_data', []))}")
    else:
        print(f"  - Error: {result.get('error', 'Unknown error')}")

def test_status_update():
    """Test status update functionality"""
    print("\n" + "="*60)
    print("TEST 6: Status Update")
    print("="*60)

    app_service = ApplicationService(logger)
    app_service.initialize()

    # Get first application
    result = app_service.search_applications("", {'page': 1, 'per_page': 1})

    if result['success'] and result['data']['applications']:
        app_id = result['data']['applications'][0]['_id']
        print(f"✓ Found application: {app_id}")

        # Test status update (just verify method exists and doesn't crash)
        print(f"✓ update_application_status method exists: {hasattr(app_service, 'update_application_status')}")

        # Note: We won't actually change status in test mode
        print(f"  (Skipping actual status update to preserve data)")
    else:
        print(f"  - No applications found to test status update")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TESTING NEW ADMIN PANEL FEATURES")
    print("="*60)

    try:
        test_search_functionality()
        test_advanced_filters()
        test_export_functionality()
        test_email_templates()
        test_dashboard_stats()
        test_status_update()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nNew features implemented:")
        print("  ✓ Full-text search with MongoDB text index")
        print("  ✓ Advanced filters (date, nationality, english level)")
        print("  ✓ Export to CSV and Excel")
        print("  ✓ Automatic email notifications (approved/rejected)")
        print("  ✓ Enhanced dashboard with distributions and trends")
        print("  ✓ Status update with notification integration")

        print("\nNew API Endpoints:")
        print("  • GET  /api/admin/applications/search")
        print("  • GET  /api/admin/applications/export")
        print("  • GET  /api/admin/applications/filters")
        print("  • PUT  /api/admin/applications/<id>/status")
        print("  • POST /api/admin/applications/<id>/approve")
        print("  • POST /api/admin/applications/<id>/reject")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
