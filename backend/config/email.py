"""
Email Configuration and Management
Email sending utilities for WorkWave Coast
"""
import logging
from typing import Dict, Any, Optional, Tuple
from flask import Flask
from flask_mail import Mail, Message
from config.constants import EMAIL_TEMPLATES

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration and utilities"""
    
    def __init__(self, server: str, port: int, use_tls: bool, username: str, password: str):
        """Initialize email configuration
        
        Args:
            server: SMTP server hostname
            port: SMTP server port
            use_tls: Whether to use TLS
            username: SMTP username
            password: SMTP password
        """
        self.server = server
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self._mail: Optional[Mail] = None
        self._app: Optional[Flask] = None
    
    def is_configured(self) -> bool:
        """Check if email is properly configured
        
        Returns:
            bool: True if all required settings are present
        """
        return all([
            self.server,
            self.username,
            self.password
        ])
    
    def setup_mail(self, app: Flask) -> Optional[Mail]:
        """Setup Flask-Mail with the given app
        
        Args:
            app: Flask application instance
            
        Returns:
            Mail: Configured Flask-Mail instance or None if not configured
        """
        if not self.is_configured():
            logger.warning("Email not properly configured")
            return None
            
        # Configure Flask app for email
        app.config.update({
            'MAIL_SERVER': self.server,
            'MAIL_PORT': self.port,
            'MAIL_USE_TLS': self.use_tls,
            'MAIL_USE_SSL': False,
            'MAIL_USERNAME': self.username,
            'MAIL_PASSWORD': self.password,
            'MAIL_DEFAULT_SENDER': self.username
        })
        
        self._mail = Mail(app)
        self._app = app
        
        logger.info(f"Email configured with server: {self.server}:{self.port}")
        return self._mail
    
    def send_confirmation_email(self, applicant_name: str, recipient_email: str) -> Tuple[bool, str]:
        """Send confirmation email to applicant
        
        Args:
            applicant_name: Name of the applicant
            recipient_email: Email address to send to
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self._mail or not self._app:
            return False, "Email not initialized"
            
        try:
            with self._app.app_context():
                # Create confirmation email content
                subject = EMAIL_TEMPLATES['confirmation']['subject']
                
                html_body = self._create_confirmation_html(applicant_name)
                text_body = self._create_confirmation_text(applicant_name)
                
                # Create message
                msg = Message(
                    subject=subject,
                    recipients=[recipient_email],
                    html=html_body,
                    body=text_body,
                    sender=self.username
                )
                
                # Log attempt
                logger.info(
                    "Attempting to send confirmation email",
                    extra={
                        'recipient': recipient_email,
                        'applicant_name': applicant_name,
                        'mail_server': self.server,
                        'mail_port': self.port,
                        'mail_username': self.username
                    }
                )
                
                # Send email
                self._mail.send(msg)
                
                logger.info(f"Confirmation email sent successfully to {recipient_email}")
                return True, "Email sent successfully"
                
        except Exception as e:
            error_msg = str(e)
            logger.error(
                "Failed to send confirmation email",
                extra={
                    'recipient': recipient_email,
                    'applicant_name': applicant_name,
                    'error': error_msg
                }
            )
            return False, f"Failed to send email: {error_msg}"
    
    def send_admin_notification(self, application_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Send notification email to admin about new application
        
        Args:
            application_data: Application data dictionary
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self._mail or not self._app:
            return False, "Email not initialized"
            
        try:
            with self._app.app_context():
                subject = EMAIL_TEMPLATES['admin_notification']['subject']
                
                html_body = self._create_admin_notification_html(application_data)
                text_body = self._create_admin_notification_text(application_data)
                
                # Send to admin email (same as sender for now)
                msg = Message(
                    subject=subject,
                    recipients=[self.username],
                    html=html_body,
                    body=text_body,
                    sender=self.username
                )
                
                self._mail.send(msg)
                
                logger.info("Admin notification email sent successfully")
                return True, "Admin notification sent"
                
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
            return False, f"Failed to send admin notification: {str(e)}"
    
    def test_configuration(self) -> Tuple[bool, str]:
        """Test email configuration
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_configured():
            return False, "Email configuration incomplete"
            
        if not self._mail:
            return False, "Email not initialized with Flask app"
            
        try:
            # Try to send a test email to self
            if self._app is None:
                return False, "Flask app not initialized"
                
            with self._app.app_context():
                msg = Message(
                    subject="WorkWave Coast - Test Email",
                    recipients=[self.username],
                    body="This is a test email to verify email configuration.",
                    sender=self.username
                )
                
                self._mail.send(msg)
                return True, "Test email sent successfully"
                
        except Exception as e:
            return False, f"Test email failed: {str(e)}"
    
    def _create_confirmation_html(self, applicant_name: str) -> str:
        """Create HTML content for confirmation email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Confirmación de Aplicación - WorkWave Coast</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏖️ WorkWave Coast</h1>
                    <h2>Confirmación de Aplicación</h2>
                </div>
                <div class="content">
                    <h3>¡Hola {applicant_name}!</h3>
                    
                    <p>Gracias por tu interés en unirte a nuestro equipo en WorkWave Coast. Hemos recibido tu aplicación exitosamente.</p>
                    
                    <p><strong>¿Qué sigue?</strong></p>
                    <ul>
                        <li>📋 Nuestro equipo revisará tu aplicación cuidadosamente</li>
                        <li>📞 Te contactaremos si tu perfil coincide con nuestras necesidades</li>
                        <li>⏰ El proceso de revisión típicamente toma 1-2 semanas</li>
                    </ul>
                    
                    <p>Mientras tanto, no dudes en seguirnos en nuestras redes sociales para conocer más sobre nuestra cultura laboral.</p>
                    
                    <div class="footer">
                        <p><strong>WorkWave Coast Team</strong></p>
                        <p>🌊 Donde el talento encuentra su lugar perfecto 🌊</p>
                        <p><em>Este es un email automático, por favor no respondas a este mensaje.</em></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_confirmation_text(self, applicant_name: str) -> str:
        """Create text content for confirmation email"""
        return f"""
        WorkWave Coast - Confirmación de Aplicación
        
        ¡Hola {applicant_name}!
        
        Gracias por tu interés en unirte a nuestro equipo en WorkWave Coast. 
        Hemos recibido tu aplicación exitosamente.
        
        ¿Qué sigue?
        - Nuestro equipo revisará tu aplicación cuidadosamente
        - Te contactaremos si tu perfil coincide con nuestras necesidades  
        - El proceso de revisión típicamente toma 1-2 semanas
        
        Mientras tanto, no dudes en seguirnos en nuestras redes sociales 
        para conocer más sobre nuestra cultura laboral.
        
        WorkWave Coast Team
        Donde el talento encuentra su lugar perfecto
        
        Este es un email automático, por favor no respondas a este mensaje.
        """
    
    def _create_admin_notification_html(self, data: Dict[str, Any]) -> str:
        """Create HTML content for admin notification email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Nueva Aplicación - WorkWave Coast</title>
        </head>
        <body>
            <h2>Nueva Aplicación Recibida</h2>
            
            <p><strong>Nombre:</strong> {data.get('nombre', '')} {data.get('apellido', '')}</p>
            <p><strong>Email:</strong> {data.get('email', '')}</p>
            <p><strong>Teléfono:</strong> {data.get('telefono', '')}</p>
            <p><strong>Puesto:</strong> {data.get('puesto', '')}</p>
            <p><strong>Nivel de Inglés:</strong> {data.get('ingles_nivel', '')}</p>
            <p><strong>Nacionalidad:</strong> {data.get('nacionalidad', '')}</p>
            
            <p><strong>Experiencia:</strong></p>
            <p>{data.get('experiencia', '')}</p>
            
            <p>Revisa el panel de administración para más detalles.</p>
        </body>
        </html>
        """
    
    def _create_admin_notification_text(self, data: Dict[str, Any]) -> str:
        """Create text content for admin notification email"""
        return f"""
        Nueva Aplicación Recibida - WorkWave Coast
        
        Nombre: {data.get('nombre', '')} {data.get('apellido', '')}
        Email: {data.get('email', '')}
        Teléfono: {data.get('telefono', '')}
        Puesto: {data.get('puesto', '')}
        Nivel de Inglés: {data.get('ingles_nivel', '')}
        Nacionalidad: {data.get('nacionalidad', '')}
        
        Experiencia:
        {data.get('experiencia', '')}
        
        Revisa el panel de administración para más detalles.
        """
    
    def get_info(self) -> Dict[str, Any]:
        """Get email configuration information
        
        Returns:
            dict: Configuration status and information
        """
        return {
            'configured': self.is_configured(),
            'server': self.server if self.is_configured() else 'Not configured',
            'port': self.port,
            'use_tls': self.use_tls,
            'username_set': bool(self.username),
            'password_set': bool(self.password),
            'mail_initialized': self._mail is not None
        }


class EmailManager:
    """Singleton email manager"""
    
    _instance: Optional['EmailManager'] = None
    _config: Optional[EmailConfig] = None
    
    def __new__(cls) -> 'EmailManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, server: str, port: int, use_tls: bool, username: str, password: str) -> EmailConfig:
        """Initialize email configuration
        
        Args:
            server: SMTP server
            port: SMTP port
            use_tls: Use TLS flag
            username: SMTP username
            password: SMTP password
            
        Returns:
            EmailConfig: Initialized email configuration
        """
        if self._config is None:
            self._config = EmailConfig(server, port, use_tls, username, password)
            
        return self._config
    
    @property
    def config(self) -> Optional[EmailConfig]:
        """Get current email configuration"""
        return self._config


# Global email manager instance
email_manager = EmailManager()


def get_email_config(server: str, port: int, use_tls: bool, username: str, password: str) -> EmailConfig:
    """Get or create email configuration
    
    Args:
        server: SMTP server
        port: SMTP port  
        use_tls: Use TLS flag
        username: SMTP username
        password: SMTP password
        
    Returns:
        EmailConfig: Email configuration instance
    """
    return email_manager.initialize(server, port, use_tls, username, password)


def send_confirmation_email(applicant_name: str, recipient_email: str) -> Tuple[bool, str]:
    """Send confirmation email using global manager
    
    Args:
        applicant_name: Name of applicant
        recipient_email: Email to send to
        
    Returns:
        tuple: (success: bool, message: str)
    """
    config = email_manager.config
    if config:
        return config.send_confirmation_email(applicant_name, recipient_email)
    else:
        logger.error("Email not initialized")
        return False, "Email configuration not initialized"