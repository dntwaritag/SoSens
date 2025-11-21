from twilio.rest import Client
from sqlalchemy.orm import Session
from datetime import datetime
from .config import settings
import app.models as models
import requests

class NotificationService:
    def __init__(self):
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                print("SMS Service initialized")
            except Exception as e:
                print(f"SMS initialization failed: {e}")
        
        self.use_sendgrid = bool(settings.SENDGRID_API_KEY)
        self.email_configured = self.use_sendgrid or bool(settings.MAIL_USERNAME)

    async def send_sms(self, to_number: str, message: str, db: Session, user_id: int = None) -> bool:
        """Send SMS via Twilio with sanitization"""
        if settings.DEBUG:
            print(f"DEBUG SMS to {to_number}: {message}")
            self._log(db, user_id, 'sms_mock', 'sms', message, True)
            return True
        
        if not self.twilio_client:
            return False
        
        try:
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            # Ensure plain ascii text
            clean_message = message.encode('ascii', 'ignore').decode('ascii')
            
            self.twilio_client.messages.create(
                body=clean_message[:1600],
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            self._log(db, user_id, 'sms', 'sms', clean_message, True)
            return True
        except Exception as e:
            print(f"SMS failed: {e}")
            self._log(db, user_id, 'sms', 'sms', message, False, str(e))
            return False

    async def send_email(self, to_email: str, subject: str, body: str, db: Session, user_id: int = None) -> bool:
        """Send email with SendGrid preference"""
        if not self.email_configured:
            return False
        if self.use_sendgrid:
            return await self._send_via_sendgrid(to_email, subject, body, db, user_id)
        # SMTP fallback logic would go here
        return False 

    async def _send_via_sendgrid(self, to_email: str, subject: str, body: str, db: Session, user_id: int = None) -> bool:
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            }
            
            clean_subject = subject.encode('ascii', 'ignore').decode('ascii')
            
            data = {
                "personalizations": [{"to": [{"email": to_email}], "subject": clean_subject}],
                "from": {"email": settings.MAIL_FROM, "name": "SoSens Rwanda"},
                "content": [{"type": "text/plain", "value": body}]
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code in [200, 202]:
                self._log(db, user_id, 'email', 'email', body, True)
                return True
            else:
                print(f"SendGrid Error: {response.text}")
                self._log(db, user_id, 'email', 'email', body, False, response.text)
                return False
        except Exception as e:
            self._log(db, user_id, 'email', 'email', body, False, str(e))
            return False

    async def send_prediction_notification(self, user: models.User, prediction: dict, weather_advice: str, db: Session) -> bool:
        """Sends notification based on preference (SMS OR Email)"""
        message = f"""New Crop Recommendation

Hello {user.full_name},

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

Best regards,
SoSens Team"""
        
        # Strict Preference Logic
        if user.preferred_contact == 'sms' and user.phone_number:
            return await self.send_sms(user.phone_number, message, db, user.id)
        elif user.preferred_contact == 'email' and user.email:
            return await self.send_email(user.email, "Your Crop Recommendation - SoSens", message, db, user.id)
        
        return False

    async def send_welcome_notification(self, user: models.User, db: Session) -> bool:
        """Sends welcome message based on preference"""
        message = f"""Welcome to SoSens, {user.full_name}!

Your account has been created successfully.
District: {user.district}

You can now submit soil readings and get crop recommendations.

Best regards,
SoSens Team"""
        
        # Strict Preference Logic
        if user.preferred_contact == 'sms' and user.phone_number:
            return await self.send_sms(user.phone_number, message, db, user.id)
        elif user.preferred_contact == 'email' and user.email:
            return await self.send_email(user.email, "Welcome to SoSens Rwanda", message, db, user.id)
        
        return False

    async def send_password_reset(self, user: models.User, reset_token: str, db: Session) -> bool:
        """Sends reset token. Prioritizes preference, falls back to available channel."""
        link = f"https://sosens.onrender.com/reset-password?token={reset_token}"
        message = f"""Password Reset Request
        
Code: {reset_token[:8]}
Link: {link}

Valid for 1 hour."""
        
        # Attempt to respect preference first
        if user.preferred_contact == 'sms' and user.phone_number:
             return await self.send_sms(user.phone_number, message, db, user.id)
        elif user.preferred_contact == 'email' and user.email:
             return await self.send_email(user.email, "Password Reset - SoSens", message, db, user.id)
        
        # Fallback if preferred method is missing but another exists
        if user.phone_number:
            return await self.send_sms(user.phone_number, message, db, user.id)
        elif user.email:
            return await self.send_email(user.email, "Password Reset - SoSens", message, db, user.id)
            
        return False

    async def send_daily_weather(self, db: Session):
        """Send daily weather based on preference"""
        from .weather_service import weather_service
        users = db.query(models.User).filter(
            models.User.is_active == True,
            models.User.receive_notifications == True,
            models.User.role == models.UserRole.FARMER
        ).all()
        
        sent = 0
        for user in users:
            try:
                weather = weather_service.get_weather(user.district, db)
                message = f"""Daily Weather: {weather['location']}
Temp: {weather['temperature']}C
Humidity: {weather['humidity']}%
{weather['description']}

{weather['advice']}"""

                success = False
                if user.preferred_contact == 'sms' and user.phone_number:
                    success = await self.send_sms(user.phone_number, message, db, user.id)
                elif user.preferred_contact == 'email' and user.email:
                    success = await self.send_email(user.email, f"Daily Weather - {weather['location']}", message, db, user.id)
                
                if success: sent += 1
            except:
                continue
        return {"sent": sent}

    def _log(self, db: Session, user_id: int, notif_type: str, channel: str, message: str, is_sent: bool, error: str = None):
        try:
            log = models.NotificationLog(
                user_id=user_id, notification_type=notif_type, channel=channel,
                message=message[:500], is_sent=is_sent, sent_at=datetime.utcnow() if is_sent else None,
                error_message=error[:200] if error else None
            )
            db.add(log)
            db.commit()
        except:
            db.rollback()

notification_service = NotificationService()