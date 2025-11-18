"""
Enhanced notification service with proper email and SMS support
FIXED: Email actually sends, not just mocked
"""

from twilio.rest import Client
from sqlalchemy.orm import Session
from datetime import datetime
from .config import settings
from . import models
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio

class NotificationService:
    def __init__(self):
        # SMS Setup
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                print(" SMS Service initialized")
            except Exception as e:
                print(f" SMS initialization failed: {e}")
        
        # Email setup
        self.email_configured = bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD)
        if self.email_configured:
            print(" Email Service configured")
        else:
            print(" Email not fully configured")
    
    async def send_sms(self, to_number: str, message: str, db: Session, user_id: int = None) -> bool:
        """Send SMS via Twilio"""
        
        # Mock in debug mode
        if settings.DEBUG:
            print(f" DEBUG MOCK: SMS to {to_number}")
            print(f"   Body: {message[:100]}...")
            self._log(db, user_id, 'sms_mock', 'sms', message, True, "Debug mode mock send")
            return True
        
        # Ensure Twilio is configured
        if not self.twilio_client:
            print(f" SMS not configured, would send to {to_number}: {message[:50]}...")
            self._log(db, user_id, 'sms', 'sms', message, False, "SMS not configured")
            return False
        
        try:
            # Ensure phone number is in correct format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            self.twilio_client.messages.create(
                body=message[:1600],  # SMS length limit
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            print(f" SMS sent to {to_number}")
            self._log(db, user_id, 'sms', 'sms', message, True)
            return True
        except Exception as e:
            print(f" SMS failed to {to_number}: {e}")
            self._log(db, user_id, 'sms', 'sms', message, False, str(e))
            return False
    
    async def send_email(self, to_email: str, subject: str, body: str, db: Session, user_id: int = None) -> bool:
        """Send email via SMTP - ACTUALLY SENDS, not just debug"""
        
        # In DEBUG mode, also log to console but STILL SEND REAL EMAIL
        if settings.DEBUG:
            print(f" DEBUG MODE: Email to {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Body preview: {body[:100]}...")
        
        # Check if email is configured
        if not self.email_configured:
            print(f" Email not configured")
            print(f"   MAIL_USERNAME: {settings.MAIL_USERNAME}")
            print(f"   MAIL_PASSWORD: {'*' * 5 if settings.MAIL_PASSWORD else 'NOT SET'}")
            self._log(db, user_id, 'email', 'email', body, False, "Email not configured")
            return False
        
        try:
            print(f" Attempting to send email to {to_email}...")
            
            # Build email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.MAIL_FROM
            msg['To'] = to_email
            
            # HTML version of email
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9f9f9;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #2e7d32; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">🌱 SoSens Rwanda</h2>
                        <div style="margin: 20px 0; line-height: 1.6; color: #333;">
                            {body.replace(chr(10), '<br>')}
                        </div>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                        <p style="color: #999; font-size: 12px; text-align: center;">
                            This is an automated message from SoSens Soil Monitoring System.<br>
                            Do not reply to this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Attach both plain text and HTML
            text_part = MIMEText(body, 'plain')
            html_part = MIMEText(html_body, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email via SMTP
            print(f"   Connecting to {settings.MAIL_SERVER}:{settings.MAIL_PORT}...")
            with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10) as server:
                print(f"   Connected! Starting TLS...")
                server.starttls()  # Upgrade to secure connection
                
                print(f"   Logging in as {settings.MAIL_USERNAME}...")
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                
                print(f"   Sending message...")
                server.send_message(msg)
            
            print(f"✓ Email sent successfully to {to_email}")
            self._log(db, user_id, 'email', 'email', body, True)
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Email authentication failed - check MAIL_USERNAME and MAIL_PASSWORD: {e}"
            print(f"✗ {error_msg}")
            self._log(db, user_id, 'email', 'email', body, False, error_msg)
            return False
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            print(f"✗ {error_msg}")
            self._log(db, user_id, 'email', 'email', body, False, error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"✗ Email failed to {to_email}: {error_msg}")
            self._log(db, user_id, 'email', 'email', body, False, error_msg)
            return False
    
    async def send_welcome_notification(self, user: models.User, db: Session) -> bool:
        """Send welcome notification after registration"""
        message = f"""Welcome to SoSens, {user.full_name}!

Your account has been created successfully.

District: {user.district}
Role: {user.role.value.title()}

You can now:
- Submit soil readings
- Get crop recommendations
- Receive daily weather updates

Start monitoring your soil quality today!

Best regards,
SoSens Team"""
        
        success = False
        if user.preferred_contact == 'sms' and user.phone_number:
            success = await self.send_sms(user.phone_number, message, db, user.id)
        elif user.preferred_contact == 'email' and user.email:
            success = await self.send_email(
                user.email,
                "Welcome to SoSens Rwanda",
                message,
                db,
                user.id
            )
        
        return success
    
    async def send_password_reset(self, user: models.User, reset_token: str, db: Session) -> bool:
        """Send password reset notification - ACTUALLY SENDS EMAIL"""
        
        # Create reset link
        reset_link = f"https://sosens.rw/reset-password?token={reset_token}"
        
        message = f"""Password Reset Request

Hello {user.full_name},

You requested to reset your password for SoSens.

Your reset code: {reset_token[:8]}

Click this link to reset: {reset_link}

This code expires in 1 hour.

If you didn't request this, please ignore this message.

Best regards,
SoSens Team"""
        
        success = False
        if user.email:
            # PRIORITY: Send to email first
            print(f"\n Sending password reset email to {user.email}...")
            success = await self.send_email(
                user.email,
                " Password Reset - SoSens",
                message,
                db,
                user.id
            )
            if success:
                print(f" Password reset email sent successfully!")
            else:
                print(f" Failed to send password reset email")
        elif user.phone_number:
            # Fallback to SMS
            sms_message = f"SoSens Password Reset Code: {reset_token[:8]}. Valid for 1 hour. Don't share this code."
            success = await self.send_sms(user.phone_number, sms_message, db, user.id)
        
        return success
    
    async def send_prediction_notification(self, user: models.User, prediction: dict, weather_advice: str, db: Session) -> bool:
        """Send notification after crop prediction"""
        
        message = f""" New Crop Recommendation

Hello {user.full_name}!

Based on your soil analysis:

Recommended Crop: {prediction['crop']}
Confidence: {prediction['confidence']:.0%}
Soil Health: {prediction.get('soil_health', 'Unknown')}

Fertilizer Advice:
{prediction.get('fertilizer_advice', 'Contact extension officer')}

Planting Season:
{prediction.get('planting_season', 'Consult local calendar')}

Weather Update:
{weather_advice or 'Check weather for latest conditions'}

Good luck with your farming!

Best regards,
SoSens Team"""
        
        success = False
        if user.preferred_contact == 'sms' and user.phone_number:
            success = await self.send_sms(user.phone_number, message, db, user.id)
        elif user.preferred_contact == 'email' and user.email:
            success = await self.send_email(
                user.email,
                " Your Crop Recommendation - SoSens",
                message,
                db,
                user.id
            )
        
        return success
    
    async def send_daily_weather(self, db: Session):
        """Send daily weather to all farmers - called by scheduler"""
        from weather_service import weather_service
        
        users = db.query(models.User).filter(
            models.User.is_active == True,
            models.User.receive_notifications == True,
            models.User.role == models.UserRole.FARMER
        ).all()
        
        sent_count = 0
        failed_count = 0
        
        print(f" Sending daily weather notifications to {len(users)} farmers...")
        
        for user in users:
            try:
                weather = weather_service.get_weather(user.district, db)
                
                message = f"""Good morning {user.full_name}!

Today's Weather in {weather['location']}:
   Temperature: {weather['temperature']}°C
   Humidity: {weather['humidity']}%
   Conditions: {weather['description']}

Farming Advice:
{weather['advice']}

Have a productive day!

Best regards,
SoSens Team"""
                
                success = False
                if user.preferred_contact == 'sms' and user.phone_number:
                    success = await self.send_sms(user.phone_number, message, db, user.id)
                elif user.preferred_contact == 'email' and user.email:
                    success = await self.send_email(
                        user.email,
                        f" Daily Weather Update - {weather['location']}",
                        message,
                        db,
                        user.id
                    )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                print(f"✗ Failed to send to user {user.id}: {e}")
                failed_count += 1
        
        print(f"✓ Daily weather sent: {sent_count} successful, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    def _log(self, db: Session, user_id: int, notif_type: str, channel: str, 
                message: str, is_sent: bool, error: str = None):
        """Log notification to database"""
        try:
            log = models.NotificationLog(
                user_id=user_id,
                notification_type=notif_type,
                channel=channel,
                message=message[:500],  # Limit message length
                is_sent=is_sent,
                sent_at=datetime.utcnow() if is_sent else None,
                error_message=error[:200] if error else None
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"✗ Failed to log notification: {e}")
            db.rollback()

# Create singleton instance
notification_service = NotificationService()