"""
Email Service
Business logic for email sending and management
"""
import logging
from typing import Dict, Any, Optional, List
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime, timezone
import re

from services.base_service import BaseService
from config.email import get_email_config


class EmailService(BaseService):
    """Service for handling email operations"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self.email_config = None
        self.smtp_server = None
        self._load_email_config()

    def _load_email_config(self):
        """Load email configuration"""
        try:
            import os
            # Get email configuration from environment variables
            smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('MAIL_PORT', '587'))
            use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
            smtp_username = os.getenv('MAIL_USERNAME', '')
            smtp_password = os.getenv('MAIL_PASSWORD', '')

            # Create email config dictionary for our service
            self.email_config = {
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'use_tls': use_tls,
                'smtp_username': smtp_username,
                'smtp_password': smtp_password,
                'from_email': os.getenv('MAIL_DEFAULT_SENDER', smtp_username),
                'admin_email': os.getenv('ADMIN_EMAIL', smtp_username)
            }

            self.log_operation("load_email_config", {"status": "loaded"})
        except Exception as e:
            self.logger.error(f"Failed to load email config: {e}")
            self.email_config = None

    def _create_smtp_connection(self):
        """Create and authenticate SMTP connection"""
        if not self.email_config:
            raise Exception("Email configuration not loaded")

        # Create secure SSL context
        context = ssl.create_default_context()

        # Use SMTP with TLS (not SMTP_SSL) for port 587
        if self.email_config['smtp_port'] == 587:
            # SMTP with STARTTLS (port 587)
            server = smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            )
            server.starttls(context=context)
        else:
            # SMTP_SSL for port 465
            server = smtplib.SMTP_SSL(
                self.email_config['smtp_server'],
                self.email_config['smtp_port'],
                context=context
            )

        # Login with credentials
        server.login(
            self.email_config['smtp_username'],
            self.email_config['smtp_password']
        )

        return server

    def validate_email_address(self, email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False

        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None

    def create_confirmation_email(self, candidate_data: Dict[str, Any]) -> Dict[str, str]:
        """Create confirmation email content"""
        nombre = candidate_data.get('nombre', '')
        apellido = candidate_data.get('apellido', '')
        puesto = candidate_data.get('puesto', '')

        subject = f"Confirmación de Aplicación - {puesto} - WorkWave Coast"

        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Aplicación - WorkWave Coast</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c5aa0;
                    margin-bottom: 10px;
                }}
                .title {{
                    color: #2c5aa0;
                    font-size: 22px;
                    margin-bottom: 20px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .highlight {{
                    background-color: #e8f4fd;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #2c5aa0;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 14px;
                    color: #666;
                }}
                .next-steps {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .next-steps h3 {{
                    color: #2c5aa0;
                    margin-top: 0;
                }}
                ul {{
                    padding-left: 20px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">WorkWave Coast</div>
                    <h1 class="title">¡Aplicación Recibida!</h1>
                </div>

                <div class="content">
                    <p>Estimado/a <strong>{nombre} {apellido}</strong>,</p>

                    <p>Gracias por tu interés en unirte al equipo de WorkWave Coast. Hemos recibido exitosamente tu aplicación para la posición de <strong>{puesto}</strong>.</p>

                    <div class="highlight">
                        <p><strong>✅ Tu aplicación ha sido registrada correctamente</strong></p>
                        <p>Fecha y hora: {datetime.now(timezone.utc).strftime('%d/%m/%Y a las %H:%M UTC')}</p>
                    </div>

                    <div class="next-steps">
                        <h3>Próximos Pasos:</h3>
                        <ul>
                            <li>Nuestro equipo de Recursos Humanos revisará tu aplicación en las próximas 24-48 horas</li>
                            <li>Si tu perfil cumple con los requisitos del puesto, te contactaremos para coordinar una entrevista</li>
                            <li>Mantente atento a tu email y teléfono para futuras comunicaciones</li>
                        </ul>
                    </div>

                    <p>Valoramos tu tiempo e interés en formar parte de nuestro equipo. WorkWave Coast se especializa en conectar talento internacional con oportunidades laborales en la costa este de Estados Unidos.</p>

                    <p>Si tienes alguna pregunta sobre tu aplicación o el proceso de selección, no dudes en contactarnos respondiendo a este email.</p>

                    <p>¡Esperamos poder conocerte pronto!</p>

                    <p>Saludos cordiales,<br>
                    <strong>Equipo de Recursos Humanos</strong><br>
                    WorkWave Coast</p>
                </div>

                <div class="footer">
                    <p>Este es un email automático, por favor no respondas a esta dirección.</p>
                    <p>Para consultas, contacta con nosotros en: info@workwavecoast.com</p>
                    <p>&copy; 2024 WorkWave Coast. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_content = f"""
        Estimado/a {nombre} {apellido},

        Gracias por tu interés en unirte al equipo de WorkWave Coast. Hemos recibido exitosamente tu aplicación para la posición de {puesto}.

        ✅ Tu aplicación ha sido registrada correctamente
        Fecha y hora: {datetime.now(timezone.utc).strftime('%d/%m/%Y a las %H:%M UTC')}

        PRÓXIMOS PASOS:
        - Nuestro equipo de Recursos Humanos revisará tu aplicación en las próximas 24-48 horas
        - Si tu perfil cumple con los requisitos del puesto, te contactaremos para coordinar una entrevista
        - Mantente atento a tu email y teléfono para futuras comunicaciones

        Valoramos tu tiempo e interés en formar parte de nuestro equipo. WorkWave Coast se especializa en conectar talento internacional con oportunidades laborales en la costa este de Estados Unidos.

        Si tienes alguna pregunta sobre tu aplicación o el proceso de selección, no dudes en contactarnos respondiendo a este email.

        ¡Esperamos poder conocerte pronto!

        Saludos cordiales,
        Equipo de Recursos Humanos
        WorkWave Coast

        ---
        Este es un email automático, por favor no respondas a esta dirección.
        Para consultas, contacta con nosotros en: info@workwavecoast.com
        © 2024 WorkWave Coast. Todos los derechos reservados.
        """

        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }

    def create_admin_notification_email(self, candidate_data: Dict[str, Any],
                                      files_info: Dict[str, Any] = None) -> Dict[str, str]:
        """Create admin notification email content"""
        nombre = candidate_data.get('nombre', '')
        apellido = candidate_data.get('apellido', '')
        email = candidate_data.get('email', '')
        telefono = candidate_data.get('telefono', '')
        puesto = candidate_data.get('puesto', '')
        nacionalidad = candidate_data.get('nacionalidad', '')
        ingles_nivel = candidate_data.get('ingles_nivel', '')
        experiencia = candidate_data.get('experiencia', '')

        subject = f"Nueva Aplicación - {puesto} - {nombre} {apellido}"

        # Create files summary
        files_summary = ""
        if files_info:
            files_list = []
            for field_name, file_info in files_info.items():
                if file_info and file_info.get('url'):
                    files_list.append(f"- {field_name}: {file_info.get('original_filename', 'Archivo')}")
            if files_list:
                files_summary = "\n".join(files_list)
            else:
                files_summary = "No se adjuntaron archivos"
        else:
            files_summary = "No se adjuntaron archivos"

        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nueva Aplicación - WorkWave Coast</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background-color: #2c5aa0;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 25px;
                }}
                .info-item {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 3px solid #2c5aa0;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #2c5aa0;
                    font-size: 14px;
                    margin-bottom: 5px;
                }}
                .info-value {{
                    color: #333;
                    font-size: 16px;
                }}
                .full-width {{
                    grid-column: 1 / -1;
                }}
                .files-section {{
                    background-color: #e8f4fd;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .admin-links {{
                    background-color: #28a745;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                    margin-top: 30px;
                }}
                .admin-links a {{
                    color: white;
                    text-decoration: none;
                    font-weight: bold;
                    padding: 10px 20px;
                    background-color: rgba(255,255,255,0.2);
                    border-radius: 5px;
                    margin: 0 10px;
                    display: inline-block;
                }}
                .timestamp {{
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }}
                @media (max-width: 600px) {{
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Nueva Aplicación Recibida</h1>
                    <p>WorkWave Coast - Panel Administrativo</p>
                </div>

                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Candidato</div>
                        <div class="info-value">{nombre} {apellido}</div>
                    </div>

                    <div class="info-item">
                        <div class="info-label">Email</div>
                        <div class="info-value">{email}</div>
                    </div>

                    <div class="info-item">
                        <div class="info-label">Teléfono</div>
                        <div class="info-value">{telefono}</div>
                    </div>

                    <div class="info-item">
                        <div class="info-label">Puesto Solicitado</div>
                        <div class="info-value">{puesto}</div>
                    </div>

                    <div class="info-item">
                        <div class="info-label">Nacionalidad</div>
                        <div class="info-value">{nacionalidad}</div>
                    </div>

                    <div class="info-item">
                        <div class="info-label">Nivel de Inglés</div>
                        <div class="info-value">{ingles_nivel}</div>
                    </div>

                    <div class="info-item full-width">
                        <div class="info-label">Experiencia Laboral</div>
                        <div class="info-value">{experiencia}</div>
                    </div>
                </div>

                <div class="files-section">
                    <h3 style="margin-top: 0; color: #2c5aa0;">📎 Archivos Adjuntos</h3>
                    <pre style="white-space: pre-wrap; font-family: inherit;">{files_summary}</pre>
                </div>

                <div class="admin-links">
                    <h3 style="margin-top: 0;">⚡ Acciones Rápidas</h3>
                    <a href="mailto:{email}">Contactar Candidato</a>
                    <a href="https://workwavecoast.com/admin">Ver en Dashboard</a>
                </div>

                <div class="timestamp">
                    Aplicación recibida el {datetime.now(timezone.utc).strftime('%d/%m/%Y a las %H:%M UTC')}
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_content = f"""
        NUEVA APLICACIÓN RECIBIDA - WORKWAVE COAST
        ==========================================

        INFORMACIÓN DEL CANDIDATO:
        - Nombre: {nombre} {apellido}
        - Email: {email}
        - Teléfono: {telefono}
        - Puesto Solicitado: {puesto}
        - Nacionalidad: {nacionalidad}
        - Nivel de Inglés: {ingles_nivel}

        EXPERIENCIA LABORAL:
        {experiencia}

        ARCHIVOS ADJUNTOS:
        {files_summary}

        ACCIONES RÁPIDAS:
        - Contactar candidato: {email}
        - Ver en dashboard: https://workwavecoast.com/admin

        Aplicación recibida el {datetime.now(timezone.utc).strftime('%d/%m/%Y a las %H:%M UTC')}
        """

        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }

    def send_email(self, to_email: str, subject: str, html_content: str,
                   text_content: str = None, cc_emails: List[str] = None,
                   bcc_emails: List[str] = None) -> Dict[str, Any]:
        """Send an email"""
        try:
            if not self.email_config:
                return self.error_response(
                    "Email configuration not loaded",
                    "ConfigurationError"
                )

            # Validate recipient email
            if not self.validate_email_address(to_email):
                return self.error_response(
                    f"Invalid email address: {to_email}",
                    "ValidationError"
                )

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_config['from_email']
            message["To"] = to_email
            message.set_charset('utf-8')

            if cc_emails:
                message["Cc"] = ", ".join(cc_emails)
            if bcc_emails:
                message["Bcc"] = ", ".join(bcc_emails)

            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)

            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # Create SMTP connection and send
            with self._create_smtp_connection() as server:
                # Prepare recipient list
                recipients = [to_email]
                if cc_emails:
                    recipients.extend(cc_emails)
                if bcc_emails:
                    recipients.extend(bcc_emails)

                # Send email - use as_bytes() for proper encoding
                try:
                    server.send_message(message)
                except AttributeError:
                    # Fallback for older Python versions
                    server.sendmail(
                        self.email_config['from_email'],
                        recipients,
                        message.as_bytes()
                    )

            self.log_operation("send_email", {
                "to_email": to_email,
                "subject": subject,
                "cc_count": len(cc_emails) if cc_emails else 0,
                "bcc_count": len(bcc_emails) if bcc_emails else 0
            })

            return self.success_response({
                "to_email": to_email,
                "subject": subject,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }, "Email sent successfully")

        except smtplib.SMTPAuthenticationError as e:
            return self.handle_error("send_email", e, {
                "to_email": to_email,
                "error_type": "authentication"
            })
        except smtplib.SMTPException as e:
            return self.handle_error("send_email", e, {
                "to_email": to_email,
                "error_type": "smtp"
            })
        except Exception as e:
            return self.handle_error("send_email", e, {"to_email": to_email})

    def send_confirmation_email(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send confirmation email to candidate"""
        try:
            print(f"[EMAIL SERVICE] ENTERED send_confirmation_email for {candidate_data.get('email')}")
            self.logger.info(f"[EMAIL SERVICE] Creating confirmation email for {candidate_data.get('email')}")

            # Check if email config is loaded
            if not self.email_config:
                print("[EMAIL SERVICE] ERROR: Email configuration not loaded")
                self.logger.error("[EMAIL SERVICE] Email configuration not loaded")
                return self.error_response(
                    "Email configuration not available",
                    "ConfigurationError"
                )
            
            print(f"[EMAIL SERVICE] Config loaded: {self.email_config.get('smtp_server')}:{self.email_config.get('smtp_port')}")

            # Log config status (without passwords)
            self.logger.info(f"Email config loaded: server={self.email_config.get('smtp_server')}, port={self.email_config.get('smtp_port')}, from={self.email_config.get('from_email')}")

            email_content = self.create_confirmation_email(candidate_data)
            self.logger.info(f"Email content created, subject: {email_content['subject']}")

            print(f"[EMAIL SERVICE] Calling send_email() to {candidate_data['email']}")
            result = self.send_email(
                to_email=candidate_data['email'],
                subject=email_content['subject'],
                html_content=email_content['html_content'],
                text_content=email_content['text_content']
            )

            print(f"[EMAIL SERVICE] send_email() returned: {result}")

            if result.get('success'):
                print(f"[EMAIL SERVICE] SUCCESS - Email sent to {candidate_data['email']}")
                self.log_operation("send_confirmation_email", {
                    "candidate_email": candidate_data['email'],
                    "candidate_name": f"{candidate_data.get('nombre', '')} {candidate_data.get('apellido', '')}",
                    "puesto": candidate_data.get('puesto', '')
                })
            else:
                print(f"[EMAIL SERVICE] FAILURE - send_email returned: {result}")
                self.logger.error(f"send_email returned failure: {result}")

            return result

        except Exception as e:
            print(f"[EMAIL SERVICE] EXCEPTION: {str(e)}")
            self.logger.error(f"Exception in send_confirmation_email: {str(e)}")
            import traceback
            print(f"[EMAIL SERVICE] TRACEBACK: {traceback.format_exc()}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return self.handle_error("send_confirmation_email", e, {
                "candidate_email": candidate_data.get('email')
            })

    def send_admin_notification(self, candidate_data: Dict[str, Any],
                              files_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send notification to admin about new application"""
        try:
            if not self.email_config or not self.email_config.get('admin_email'):
                return self.error_response(
                    "Admin email not configured",
                    "ConfigurationError"
                )

            email_content = self.create_admin_notification_email(candidate_data, files_info)

            result = self.send_email(
                to_email=self.email_config['admin_email'],
                subject=email_content['subject'],
                html_content=email_content['html_content'],
                text_content=email_content['text_content']
            )

            if result.get('success'):
                self.log_operation("send_admin_notification", {
                    "candidate_email": candidate_data['email'],
                    "candidate_name": f"{candidate_data.get('nombre', '')} {candidate_data.get('apellido', '')}",
                    "puesto": candidate_data.get('puesto', ''),
                    "admin_email": self.email_config['admin_email']
                })

            return result

        except Exception as e:
            return self.handle_error("send_admin_notification", e, {
                "candidate_email": candidate_data.get('email')
            })

    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration by sending a test email"""
        try:
            if not self.email_config:
                return self.error_response(
                    "Email configuration not loaded",
                    "ConfigurationError"
                )

            # Create test message
            test_subject = "WorkWave Coast - Test Email Configuration"
            test_html = """
            <html>
                <body>
                    <h2>Email Configuration Test</h2>
                    <p>This is a test email to verify that the email configuration is working correctly.</p>
                    <p>If you received this email, the configuration is working properly.</p>
                    <hr>
                    <p><small>WorkWave Coast Email Service</small></p>
                </body>
            </html>
            """
            test_text = """
            Email Configuration Test

            This is a test email to verify that the email configuration is working correctly.
            If you received this email, the configuration is working properly.

            WorkWave Coast Email Service
            """

            # Send test email to admin
            result = self.send_email(
                to_email=self.email_config.get('admin_email', self.email_config['from_email']),
                subject=test_subject,
                html_content=test_html,
                text_content=test_text
            )

            if result.get('success'):
                self.log_operation("test_email_configuration", {"status": "success"})
                return self.success_response({
                    "test_email_sent_to": self.email_config.get('admin_email', self.email_config['from_email']),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, "Email configuration test successful")
            else:
                return result

        except Exception as e:
            return self.handle_error("test_email_configuration", e)

    def send_password_recovery_email(self, email: str, username: str, recovery_link: str, expires_at: str) -> Dict[str, Any]:
        """Send password recovery email to admin"""
        try:
            if not self.email_config:
                return self.error_response("Email service not configured", "EmailNotConfigured")

            # Password recovery email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Recovery - WorkWave Coast</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f8f9fa; padding: 30px; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>WorkWave Coast</h1>
                        <h2>Password Recovery</h2>
                    </div>

                    <div class="content">
                        <h3>Hello {username},</h3>
                        <p>We received a request to reset your admin password for WorkWave Coast.</p>

                        <p>Click the button below to reset your password:</p>
                        <a href="{recovery_link}" class="button">Reset Password</a>

                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #007bff;">{recovery_link}</p>

                        <div class="warning">
                            <strong>Important:</strong>
                            <ul>
                                <li>This link will expire at: <strong>{expires_at}</strong></li>
                                <li>If you didn't request this password reset, please ignore this email</li>
                                <li>For security reasons, this link can only be used once</li>
                            </ul>
                        </div>

                        <p>If you have any issues, please contact the system administrator.</p>
                    </div>

                    <div class="footer">
                        <p>This is an automated email from WorkWave Coast Admin System</p>
                        <p>Please do not reply to this email</p>
                    </div>
                </div>
            </body>
            </html>
            """

            result = self.send_email(
                to_email=email,
                subject="Password Recovery - WorkWave Coast Admin",
                html_content=html_content
            )

            if result.get('success'):
                self.log_operation("send_password_recovery_email", {
                    "email": email,
                    "username": username,
                    "expires_at": expires_at
                })

            return result

        except Exception as e:
            return self.handle_error("send_password_recovery_email", e, {
                "email": email,
                "username": username
            })

    def send_password_reset_confirmation_email(self, email: str, username: str) -> Dict[str, Any]:
        """Send password reset confirmation email to admin"""
        try:
            if not self.email_config:
                return self.error_response("Email service not configured", "EmailNotConfigured")

            # Password reset confirmation email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset Confirmation - WorkWave Coast</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f8f9fa; padding: 30px; }}
                    .success {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .security-tips {{ background-color: #e2e3e5; border: 1px solid #d6d8db; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>WorkWave Coast</h1>
                        <h2>Password Reset Successful</h2>
                    </div>

                    <div class="content">
                        <h3>Hello {username},</h3>

                        <div class="success">
                            <h4>✓ Your password has been successfully reset</h4>
                            <p>You can now log in to the WorkWave Coast admin panel with your new password.</p>
                        </div>

                        <p>Reset completed at: <strong>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</strong></p>

                        <div class="security-tips">
                            <h4>Security Tips:</h4>
                            <ul>
                                <li>Keep your password secure and don't share it with anyone</li>
                                <li>Use a strong, unique password for your admin account</li>
                                <li>Consider changing your password regularly</li>
                                <li>If you notice any suspicious activity, contact the system administrator immediately</li>
                            </ul>
                        </div>

                        <p>If you didn't reset your password, please contact the system administrator immediately.</p>
                    </div>

                    <div class="footer">
                        <p>This is an automated email from WorkWave Coast Admin System</p>
                        <p>Please do not reply to this email</p>
                    </div>
                </div>
            </body>
            </html>
            """

            result = self.send_email(
                to_email=email,
                subject="Password Reset Confirmation - WorkWave Coast Admin",
                html_content=html_content
            )

            if result.get('success'):
                self.log_operation("send_password_reset_confirmation_email", {
                    "email": email,
                    "username": username
                })

            return result

        except Exception as e:
            return self.handle_error("send_password_reset_confirmation_email", e, {
                "email": email,
                "username": username
            })

    def send_application_approved_email(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email notification when application is approved

        Args:
            candidate_data: Dictionary with candidate information
        """
        try:
            if not self.email_config:
                return self.error_response("Email service not configured", "EmailNotConfigured")

            email = candidate_data.get('email', '')
            if not self.validate_email_address(email):
                return self.error_response("Invalid email address", "InvalidEmail")

            nombre = candidate_data.get('nombre', '')
            apellido = candidate_data.get('apellido', '')
            puesto = candidate_data.get('puesto', '')

            subject = f"¡Felicitaciones! Tu aplicación ha sido aprobada - WorkWave Coast"

            html_content = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Aplicación Aprobada - WorkWave Coast</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                    .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .content {{ padding: 30px; background-color: #f8f9fa; }}
                    .success-banner {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .success-banner h2 {{ margin: 0 0 10px 0; color: #155724; }}
                    .info-box {{ background-color: #ffffff; padding: 20px; border-radius: 5px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .next-steps {{ background-color: #e7f3ff; border-left: 4px solid #0066cc; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .next-steps h3 {{ margin-top: 0; color: #004085; }}
                    .next-steps ul {{ margin: 10px 0; padding-left: 20px; }}
                    .footer {{ background-color: #343a40; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                    .button {{ display: inline-block; padding: 12px 30px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌊 WorkWave Coast</h1>
                        <p style="margin: 5px 0; font-size: 16px;">Empleos en la Costa Croata</p>
                    </div>

                    <div class="content">
                        <div class="success-banner">
                            <h2>✅ ¡Felicitaciones {nombre}!</h2>
                            <p style="margin: 5px 0; font-size: 18px;"><strong>Tu aplicación ha sido APROBADA</strong></p>
                        </div>

                        <div class="info-box">
                            <h3>Detalles de tu aplicación:</h3>
                            <p><strong>Nombre:</strong> {nombre} {apellido}</p>
                            <p><strong>Puesto:</strong> {puesto}</p>
                            <p><strong>Estado:</strong> <span style="color: #28a745; font-weight: bold;">APROBADO</span></p>
                        </div>

                        <div class="next-steps">
                            <h3>📋 Próximos Pasos</h3>
                            <ul>
                                <li>Nuestro equipo se pondrá en contacto contigo en las próximas 48-72 horas</li>
                                <li>Te enviaremos información detallada sobre el puesto y condiciones</li>
                                <li>Recibirás instrucciones para el proceso de contratación</li>
                                <li>Mantén tu teléfono y email disponibles para recibir nuestra comunicación</li>
                            </ul>
                        </div>

                        <p>Estamos emocionados de tenerte en nuestro equipo para la temporada en la costa croata. ¡Prepárate para una experiencia inolvidable!</p>

                        <p style="margin-top: 20px;"><strong>¿Tienes preguntas?</strong><br>
                        No dudes en responder a este correo y te responderemos lo antes posible.</p>
                    </div>

                    <div class="footer">
                        <p><strong>WorkWave Coast</strong> - Tu oportunidad de trabajar en la costa adriática</p>
                        <p>Este es un correo automático, pero puedes responder para contactarnos</p>
                        <p style="margin-top: 10px;">© 2025 WorkWave Coast. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            result = self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )

            if result.get('success'):
                self.log_operation("send_application_approved_email", {
                    "email": email,
                    "nombre": nombre,
                    "puesto": puesto
                })

            return result

        except Exception as e:
            return self.handle_error("send_application_approved_email", e, {
                "email": candidate_data.get('email', ''),
                "nombre": candidate_data.get('nombre', '')
            })

    def send_application_rejected_email(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email notification when application is rejected

        Args:
            candidate_data: Dictionary with candidate information
        """
        try:
            if not self.email_config:
                return self.error_response("Email service not configured", "EmailNotConfigured")

            email = candidate_data.get('email', '')
            if not self.validate_email_address(email):
                return self.error_response("Invalid email address", "InvalidEmail")

            nombre = candidate_data.get('nombre', '')
            apellido = candidate_data.get('apellido', '')
            puesto = candidate_data.get('puesto', '')

            subject = f"Actualización de tu aplicación - WorkWave Coast"

            html_content = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Actualización de Aplicación - WorkWave Coast</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                    .header {{ background: linear-gradient(135deg, #0066cc 0%, #0099ff 100%); color: white; padding: 30px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .content {{ padding: 30px; background-color: #f8f9fa; }}
                    .info-banner {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .info-box {{ background-color: #ffffff; padding: 20px; border-radius: 5px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .encouragement {{ background-color: #e7f3ff; border-left: 4px solid #0066cc; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .footer {{ background-color: #343a40; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                    .button {{ display: inline-block; padding: 12px 30px; background-color: #0066cc; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌊 WorkWave Coast</h1>
                        <p style="margin: 5px 0; font-size: 16px;">Empleos en la Costa Croata</p>
                    </div>

                    <div class="content">
                        <h2>Hola {nombre},</h2>

                        <div class="info-banner">
                            <p style="margin: 0; font-size: 16px;">Gracias por tu interés en trabajar con nosotros en la costa croata.</p>
                        </div>

                        <div class="info-box">
                            <p>Hemos revisado cuidadosamente tu aplicación para el puesto de <strong>{puesto}</strong>.</p>

                            <p>Lamentablemente, en esta ocasión hemos decidido no avanzar con tu candidatura para esta posición específica. Esta decisión se debe al alto volumen de aplicaciones recibidas y a la necesidad de ajustarnos a requisitos muy específicos para cada puesto.</p>
                        </div>

                        <div class="encouragement">
                            <h3>💡 No te desanimes</h3>
                            <p><strong>Te animamos a postularte nuevamente:</strong></p>
                            <ul>
                                <li>Publicaremos nuevas posiciones regularmente durante la temporada</li>
                                <li>Tus datos quedan en nuestra base de datos para futuras oportunidades</li>
                                <li>Puedes aplicar a otros puestos que mejor se ajusten a tu perfil</li>
                                <li>La experiencia en hostelería y el nivel de idiomas son muy valorados</li>
                            </ul>
                        </div>

                        <p>Valoramos mucho el tiempo que dedicaste a tu aplicación y te deseamos mucho éxito en tu búsqueda laboral.</p>

                        <p style="margin-top: 20px;">Si tienes preguntas o deseas más información, no dudes en contactarnos respondiendo a este correo.</p>

                        <p><strong>¡Te deseamos lo mejor!</strong><br>
                        Equipo WorkWave Coast</p>
                    </div>

                    <div class="footer">
                        <p><strong>WorkWave Coast</strong> - Oportunidades laborales en la costa adriática</p>
                        <p>Puedes responder a este correo para contactarnos</p>
                        <p style="margin-top: 10px;">© 2025 WorkWave Coast. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            result = self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )

            if result.get('success'):
                self.log_operation("send_application_rejected_email", {
                    "email": email,
                    "nombre": nombre,
                    "puesto": puesto
                })

            return result

        except Exception as e:
            return self.handle_error("send_application_rejected_email", e, {
                "email": candidate_data.get('email', ''),
                "nombre": candidate_data.get('nombre', '')
            })

    def send_application_status_change_email(self, candidate_data: Dict[str, Any], new_status: str, old_status: str = None) -> Dict[str, Any]:
        """
        Send email notification when application status changes

        Args:
            candidate_data: Dictionary with candidate information
            new_status: New status of the application
            old_status: Previous status (optional)
        """
        try:
            # Route to specific email based on new status
            if new_status.lower() == 'approved':
                return self.send_application_approved_email(candidate_data)
            elif new_status.lower() == 'rejected':
                return self.send_application_rejected_email(candidate_data)
            else:
                # For other status changes, send a generic notification
                if not self.email_config:
                    return self.error_response("Email service not configured", "EmailNotConfigured")

                email = candidate_data.get('email', '')
                if not self.validate_email_address(email):
                    return self.error_response("Invalid email address", "InvalidEmail")

                nombre = candidate_data.get('nombre', '')
                puesto = candidate_data.get('puesto', '')

                # Translate status to Spanish
                status_translations = {
                    'pending': 'En Revisión',
                    'reviewed': 'Revisada',
                    'approved': 'Aprobada',
                    'rejected': 'No Seleccionada',
                    'contacted': 'Contactado',
                    'interview': 'Entrevista Programada'
                }

                status_display = status_translations.get(new_status.lower(), new_status)

                subject = f"Actualización de tu aplicación - WorkWave Coast"

                html_content = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                        .header {{ background-color: #0066cc; color: white; padding: 30px; text-align: center; }}
                        .content {{ padding: 30px; }}
                        .status-box {{ background-color: #e7f3ff; border-left: 4px solid #0066cc; padding: 15px; margin: 20px 0; }}
                        .footer {{ background-color: #343a40; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🌊 WorkWave Coast</h1>
                        </div>
                        <div class="content">
                            <h2>Hola {nombre},</h2>
                            <p>Tu aplicación para el puesto de <strong>{puesto}</strong> ha sido actualizada.</p>
                            <div class="status-box">
                                <p><strong>Estado actual:</strong> {status_display}</p>
                            </div>
                            <p>Nos pondremos en contacto contigo si necesitamos información adicional.</p>
                            <p>Gracias por tu interés en WorkWave Coast.</p>
                        </div>
                        <div class="footer">
                            <p>© 2025 WorkWave Coast. Todos los derechos reservados.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

                result = self.send_email(
                    to_email=email,
                    subject=subject,
                    html_content=html_content
                )

                if result.get('success'):
                    self.log_operation("send_application_status_change_email", {
                        "email": email,
                        "nombre": nombre,
                        "new_status": new_status,
                        "old_status": old_status
                    })

                return result

        except Exception as e:
            return self.handle_error("send_application_status_change_email", e, {
                "email": candidate_data.get('email', ''),
                "new_status": new_status
            })

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            if not self.email_config:
                return {
                    "status": "unhealthy",
                    "email_configured": False,
                    "error": "Email configuration not loaded",
                    "service": "EmailService"
                }

            # Test SMTP connection
            with self._create_smtp_connection() as server:
                server.noop()  # Simple no-operation command to test connection

            return {
                "status": "healthy",
                "email_configured": True,
                "smtp_server": self.email_config['smtp_server'],
                "service": "EmailService"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "email_configured": bool(self.email_config),
                "error": str(e),
                "service": "EmailService"
            }

