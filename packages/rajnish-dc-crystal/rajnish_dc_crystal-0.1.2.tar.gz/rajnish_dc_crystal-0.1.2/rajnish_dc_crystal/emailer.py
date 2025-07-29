"""
Email notification functionality for Crystal HR Automation.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class EmailNotifier:
    """Handles sending email notifications for HR automation events."""
    
    def __init__(self, gmail_user: str, gmail_app_password: str, recipient_email: str):
        """Initialize the email notifier.
        
        Args:
            gmail_user: Gmail address to send from
            gmail_app_password: App password for Gmail
            recipient_email: Email address to send notifications to
        """
        self.gmail_user = gmail_user
        self.gmail_app_password = gmail_app_password
        self.recipient_email = recipient_email
    
    def send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """Send an email notification.
        
        Args:
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML content
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            if not all([self.gmail_user, self.gmail_app_password, self.recipient_email]):
                logger.warning("Email configuration incomplete, skipping email notification")
                return False
                
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.gmail_user, self.gmail_app_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
