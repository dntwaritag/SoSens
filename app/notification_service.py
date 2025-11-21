"""
Enhanced notification service with SendGrid for email and Twilio for SMS.
Includes detailed logging and debug mode handling.
FIXED: Password reset notification with better error handling
"""

from twilio.rest import Client
from sqlalchemy.orm import Session
from datetime import datetime
from .config import settings
import app.models as models
import requests  # For SendGrid API
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
        
        # Email setup - if using SendGrid or SMTP
        self.use_sendgrid = bool(settings.SENDGRID_API_KEY)
        self.email_configured = self.use_sendgrid or bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD)
        
        if self.use_sendgrid:
            print(" Email Service configured (SendGrid)")
        elif self.email_configured:
            print(" Email Service configured (SMTP)")
        else:
            print(" Email not configured")
    
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
        """Send email via SendGrid API or SMTP"""
        
        if settings.DEBUG:
            print(f" DEBUG MODE: Email to {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Body preview: {body[:100]}...")
        
        if not self.email_configured:
            print(f" Email not configured")
            self._log(db, user_id, 'email', 'email', body, False, "Email not configured")
            return False
        
        # Use SendGrid if configured
        if self.use_sendgrid:
            return await self._send_via_sendgrid(to_email, subject, body, db, user_id)
        else:
            return await self._send_via_smtp(to_email, subject, body, db, user_id)
    
    async def _send_via_sendgrid(self, to_email: str, subject: str, body: str, db: Session, user_id: int = None) -> bool:
        """Send email via SendGrid API"""
        try:
            print(f" Sending email via SendGrid to {to_email}...")
            
            # HTML version
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
            
            # SendGrid API request
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": subject
                }],
                "from": {
                    "email": settings.MAIL_FROM,
                    "name": "SoSens Rwanda"
                },
                "content": [
                    {
                        "type": "text/plain",
                        "value": body
                    },
                    {
                        "type": "text/html",
                        "value": html_body
                    }
                ]
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code in [200, 202]:
                print(f" Email sent successfully via SendGrid to {to_email}")
                self._log(db, user_id, 'email', 'email', body, True)
                return True
            else:
                error_msg = f"SendGrid error: {response.status_code} - {response.text}"
                print(f" {error_msg}")
                self._log(db, user_id, 'email', 'email', body, False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"SendGrid error: {e}"
            print(f" Email failed to {to_email}: {error_msg}")
            self._log(db, user_id, 'email', 'email', body, False, error_msg)
            return False
    
    async def _send_via_smtp(self, to_email: str, subject: str, body: str, db: Session, user_id: int = None) -> bool:
        """Send email via SMTP (won't work on Render free tier)"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            print(f" Attempting SMTP email to {to_email}...")
            print(f" WARNING: SMTP may be blocked on Render free tier")
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.MAIL_FROM
            msg['To'] = to_email
            
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
            
            text_part = MIMEText(body, 'plain')
            html_part = MIMEText(html_body, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                server.send_message(msg)
            
            print(f" Email sent successfully to {to_email}")
            self._log(db, user_id, 'email', 'email', body, True)
            return True
            
        except Exception as e:
            error_msg = f"SMTP error: {e}"
            print(f" Email failed to {to_email}: {error_msg}")
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
        """Send password reset notification - FIXED VERSION"""
        
        print(f"\n{'='*60}")
        print(f" PASSWORD RESET REQUEST")
        print(f"{'='*60}")
        print(f"User: {user.full_name}")
        print(f"Email: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Token: {reset_token[:10]}...")
        print(f"{'='*60}\n")
        
        # Create reset link - UPDATE WITH YOUR ACTUAL FRONTEND URL
        reset_link = f"https://sosens.onrender.com/reset-password?token={reset_token}"
        
        # Create message
        message = f""" Password Reset Request

Hello {user.full_name},

You requested to reset your password for SoSens.

Your reset code: {reset_token[:8]}

Click this link to reset your password:
{reset_link}

This code expires in 1 hour.

If you didn't request this, please ignore this message.

Best regards,
SoSens Team"""
        
        success = False
        
        # Try email first if available
        if user.email:
            print(f" Attempting to send reset email to: {user.email}")
            try:
                success = await self.send_email(
                    user.email,
                    " Password Reset - SoSens",
                    message,
                    db,
                    user.id
                )
                if success:
                    print(f" Password reset email sent successfully!")
                    return True
                else:
                    print(f" Email sending failed, trying SMS fallback...")
            except Exception as e:
                print(f" Email error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f" No email address for user {user.id}")
        
        # Fallback to SMS if email failed or not available
        if user.phone_number:
            print(f" Attempting to send reset SMS to: {user.phone_number}")
            try:
                sms_message = f"SoSens Password Reset Code: {reset_token[:8]}\n\nValid for 1 hour. Don't share this code.\n\nReset link: {reset_link}"
                success = await self.send_sms(user.phone_number, sms_message, db, user.id)
                if success:
                    print(f" Password reset SMS sent successfully!")
                    return True
                else:
                    print(f" SMS sending failed")
            except Exception as e:
                print(f" SMS error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f" No phone number for user {user.id}")
        
        # If both methods failed
        if not success:
            print(f" Failed to send password reset notification via any channel")
            self._log(db, user.id, 'password_reset_failed', 'none', message, False, "All notification methods failed")
        
        return success
    
    async def send_prediction_notification(self, user: models.User, prediction: dict, weather_advice: str, db: Session) -> bool:
        """Send notification after crop prediction"""
        
        message = f"""🌾 New Crop Recommendation

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
                "🌾 Your Crop Recommendation - SoSens",
                message,
                db,
                user.id
            )
        
        return success
    
    async def send_daily_weather(self, db: Session):
        """Send daily weather to all farmers"""
        from .weather_service import weather_service
        
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
                        f"Daily Weather Update - {weather['location']}",
                        message,
                        db,
                        user.id
                    )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                print(f" Failed to send to user {user.id}: {e}")
                failed_count += 1
        
        print(f" Daily weather sent: {sent_count} successful, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    def _log(self, db: Session, user_id: int, notif_type: str, channel: str, 
                message: str, is_sent: bool, error: str = None):
        """Log notification to database"""
        try:
            log = models.NotificationLog(
                user_id=user_id,
                notification_type=notif_type,
                channel=channel,
                message=message[:500],
                is_sent=is_sent,
                sent_at=datetime.utcnow() if is_sent else None,
                error_message=error[:200] if error else None
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f" Failed to log notification: {e}")
            db.rollback()

# Create singleton instance
notification_service = NotificationService()
