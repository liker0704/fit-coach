"""Email service for sending emails."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    @staticmethod
    def _create_message(
        subject: str,
        body: str,
        to_emails: List[str],
        from_email: Optional[str] = None,
        html: bool = False,
    ) -> MIMEMultipart:
        """Create email message.

        Args:
            subject: Email subject
            body: Email body content
            to_emails: List of recipient email addresses
            from_email: Sender email address (defaults to settings.SMTP_USER)
            html: Whether body is HTML content

        Returns:
            MIMEMultipart message
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_email or settings.SMTP_USER
        message["To"] = ", ".join(to_emails)

        # Attach body
        mime_type = "html" if html else "plain"
        message.attach(MIMEText(body, mime_type))

        return message

    @staticmethod
    def send_email(
        subject: str,
        body: str,
        to_emails: List[str],
        html: bool = False,
    ) -> bool:
        """Send email via SMTP.

        Args:
            subject: Email subject
            body: Email body content
            to_emails: List of recipient email addresses
            html: Whether body is HTML content

        Returns:
            True if email sent successfully, False otherwise
        """
        # Check if email is enabled
        if not settings.ENABLE_EMAIL:
            logger.warning("Email service is disabled. Email not sent.")
            logger.info(f"Would have sent email to {to_emails} with subject: {subject}")
            return False

        try:
            # Create message
            message = EmailService._create_message(subject, body, to_emails, html=html)

            # Connect to SMTP server and send
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)

            logger.info(f"Email sent successfully to {to_emails}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(email: str, token: str) -> bool:
        """Send password reset email with token.

        Args:
            email: User's email address
            token: Password reset token

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"{settings.PROJECT_NAME} - Password Reset Request"

        # Create reset link (assuming frontend handles this)
        # In production, replace with your actual frontend URL
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your {settings.PROJECT_NAME} account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>{settings.PROJECT_NAME} Team</p>
        </body>
        </html>
        """

        return EmailService.send_email(subject, body, [email], html=True)

    @staticmethod
    def send_verification_email(email: str, token: str) -> bool:
        """Send email verification email with token.

        Args:
            email: User's email address
            token: Email verification token

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"{settings.PROJECT_NAME} - Email Verification"

        # Create verification link
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        body = f"""
        <html>
        <body>
            <h2>Welcome to {settings.PROJECT_NAME}!</h2>
            <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_link}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create this account, please ignore this email.</p>
            <br>
            <p>Best regards,<br>{settings.PROJECT_NAME} Team</p>
        </body>
        </html>
        """

        return EmailService.send_email(subject, body, [email], html=True)

    @staticmethod
    def send_welcome_email(email: str, name: str) -> bool:
        """Send welcome email to new user.

        Args:
            email: User's email address
            name: User's name

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Welcome to {settings.PROJECT_NAME}!"

        body = f"""
        <html>
        <body>
            <h2>Welcome to {settings.PROJECT_NAME}, {name}!</h2>
            <p>Your account has been successfully created.</p>
            <p>You can now start tracking your health and fitness goals.</p>
            <p>If you have any questions, feel free to contact our support team.</p>
            <br>
            <p>Best regards,<br>{settings.PROJECT_NAME} Team</p>
        </body>
        </html>
        """

        return EmailService.send_email(subject, body, [email], html=True)
