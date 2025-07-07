import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger()

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.SMTP_FROM_EMAIL
    
    def _create_connection(self) -> smtplib.SMTP:
        """Create SMTP connection"""
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            if self.username and self.password:
                server.login(self.username, self.password)
            
            return server
        except Exception as e:
            logger.error("Failed to create SMTP connection", error=str(e))
            raise
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = self._create_connection()
            
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            server.sendmail(self.from_email, recipients, msg.as_string())
            server.quit()
            
            logger.info("Email sent successfully", to=to_email, subject=subject)
            return True
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e), to=to_email, subject=subject)
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to School Management System"
        body = f"""
        Dear {user_name},

        Welcome to the School Management System! Your account has been successfully created.

        You can now log in to your account and start using the system.

        If you have any questions, please don't hesitate to contact us.

        Best regards,
        School Management System Team
        """
        
        return self.send_email(to_email, subject, body)
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        # In a real application, this would contain a link to reset password
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        subject = "Password Reset Request"
        body = f"""
        Dear User,

        You have requested to reset your password. Please click the link below to reset your password:

        {reset_url}

        This link will expire in 1 hour.

        If you did not request this password reset, please ignore this email.

        Best regards,
        School Management System Team
        """
        
        return self.send_email(to_email, subject, body)
    
    def send_attendance_notification(
        self, 
        to_email: str, 
        student_name: str, 
        class_name: str, 
        date: str,
        status: str
    ) -> bool:
        """Send attendance notification"""
        subject = f"Attendance Update - {student_name}"
        body = f"""
        Dear Parent/Guardian,

        This is to inform you about {student_name}'s attendance:

        Class: {class_name}
        Date: {date}
        Status: {status}

        Please contact the school if you have any questions.

        Best regards,
        School Management System Team
        """
        
        return self.send_email(to_email, subject, body)
    
    def send_grade_notification(
        self,
        to_email: str,
        student_name: str,
        quiz_name: str,
        score: float,
        max_score: float
    ) -> bool:
        """Send grade notification"""
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        subject = f"Grade Update - {student_name}"
        body = f"""
        Dear Parent/Guardian,

        {student_name} has received a grade for {quiz_name}:

        Score: {score}/{max_score} ({percentage:.1f}%)

        Please contact the school if you have any questions.

        Best regards,
        School Management System Team
        """
        
        return self.send_email(to_email, subject, body)
    
    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        is_html: bool = False
    ) -> Dict[str, List[str]]:
        """Send bulk email"""
        successful = []
        failed = []
        
        for recipient in recipients:
            if self.send_email(recipient, subject, body, is_html):
                successful.append(recipient)
            else:
                failed.append(recipient)
        
        return {
            "successful": successful,
            "failed": failed
        }

class SMSService:
    """SMS service for sending text messages (placeholder implementation)"""
    
    def __init__(self):
        # This would be configured with SMS provider credentials
        # e.g., Twilio, AWS SNS, etc.
        self.provider_api_key = settings.SMS_API_KEY
        self.provider_url = settings.SMS_PROVIDER_URL
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS message"""
        try:
            # This is a placeholder implementation
            # In a real application, you would integrate with an SMS provider
            logger.info("SMS sent (placeholder)", to=to_phone, message=message)
            return True
        except Exception as e:
            logger.error("Failed to send SMS", error=str(e), to=to_phone)
            return False
    
    def send_attendance_sms(self, to_phone: str, student_name: str, status: str) -> bool:
        """Send attendance SMS notification"""
        message = f"Attendance update for {student_name}: {status}. Contact school for details."
        return self.send_sms(to_phone, message)
    
    def send_verification_sms(self, to_phone: str, code: str) -> bool:
        """Send verification code SMS"""
        message = f"Your verification code is: {code}. This code will expire in 10 minutes."
        return self.send_sms(to_phone, message)

class NotificationService:
    """Unified notification service"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def send_notification(
        self,
        recipient_email: str,
        recipient_phone: Optional[str],
        subject: str,
        message: str,
        send_email: bool = True,
        send_sms: bool = False
    ) -> Dict[str, bool]:
        """Send notification via email and/or SMS"""
        results = {}
        
        if send_email:
            results['email'] = self.email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                body=message
            )
        
        if send_sms and recipient_phone:
            results['sms'] = self.sms_service.send_sms(
                to_phone=recipient_phone,
                message=message
            )
        
        return results
