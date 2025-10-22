"""
Script para probar el envío de emails
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from config.env_loader import ensure_env_loaded
ensure_env_loaded()

from services.email_service import EmailService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_email_service():
    """Test email service configuration and sending"""
    print("\n" + "="*60)
    print("TESTING EMAIL SERVICE")
    print("="*60 + "\n")

    # Initialize email service
    email_service = EmailService(logger)

    # Check configuration
    print("📧 Email Configuration:")
    if email_service.email_config:
        print(f"  ✅ SMTP Server: {email_service.email_config['smtp_server']}")
        print(f"  ✅ SMTP Port: {email_service.email_config['smtp_port']}")
        print(f"  ✅ Use TLS: {email_service.email_config['use_tls']}")
        print(f"  ✅ Username: {email_service.email_config['smtp_username']}")
        print(f"  ✅ From Email: {email_service.email_config['from_email']}")
        print(f"  ✅ Admin Email: {email_service.email_config['admin_email']}")
        print(f"  ✅ Password: {'*' * len(email_service.email_config['smtp_password'])}\n")
    else:
        print("  ❌ Email configuration not loaded!\n")
        return

    # Test confirmation email
    print("📨 Testing Confirmation Email...")
    test_candidate = {
        'nombre': 'Test',
        'apellido': 'Usuario',
        'email': email_service.email_config['admin_email'],  # Send to admin for testing
        'puesto': 'Desarrollador Backend',
        'telefono': '+1 234567890',
        'nacionalidad': 'Argentina',
        'ingles_nivel': 'Avanzado',
        'experiencia': 'Test experience'
    }

    result = email_service.send_confirmation_email(test_candidate)

    if result.get('success'):
        print(f"  ✅ SUCCESS: {result.get('message')}")
        print(f"  📬 Sent to: {test_candidate['email']}")
        print(f"  📅 Sent at: {result.get('data', {}).get('sent_at')}")
    else:
        print(f"  ❌ FAILED: {result.get('message')}")
        print(f"  🔍 Error type: {result.get('error_type')}")

    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        test_email_service()
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
