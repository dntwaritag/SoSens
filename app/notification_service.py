import os
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from twilio.rest import Client
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import models

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Email Configuration
email_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME', 'Rwanda Soil Monitoring'),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

class NotificationService:
    """Handle SMS and Email notifications"""
    
    def __init__(self):
        self.twilio_client = None
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        self.fastmail = FastMail(email_conf)
    
    async def send_sms(self, to_number: str, message: str, db: Session, user_id: int = None) -> bool:
        """Send SMS notification"""
        if not self.twilio_client:
            print("SMS service not configured")
            return False
        
        try:
            sms = self.twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            # Log notification
            self._log_notification(db, user_id, 'daily', 'sms', message, True)
            return True
            
        except Exception as e:
            print(f"SMS error: {e}")
            self._log_notification(db, user_id, 'daily', 'sms', message, False, str(e))
            return False
    
    async def send_email(self, to_email: str, subject: str, body: str, db: Session, user_id: int = None) -> bool:
        """Send email notification"""
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=body,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            
            # Log notification
            self._log_notification(db, user_id, 'daily', 'email', body, True)
            return True
            
        except Exception as e:
            print(f"Email error: {e}")
            self._log_notification(db, user_id, 'daily', 'email', body, False, str(e))
            return False
    
    def _log_notification(self, db: Session, user_id: int, notif_type: str, 
                        channel: str, message: str, is_sent: bool, error: str = None):
        """Log notification in database"""
        try:
            log = models.NotificationLog(
                user_id=user_id,
                notification_type=notif_type,
                channel=channel,
                message=message,
                is_sent=is_sent,
                sent_at=datetime.utcnow() if is_sent else None,
                error_message=error
            )
            db.add(log)
            db.commit()
        except:
            pass
    
    async def send_daily_update(self, db: Session):
        """Send daily updates to all active users"""
        users = db.query(models.User).filter(
            models.User.is_active == True,
            models.User.receive_notifications == True
        ).all()
        
        for user in users:
            # Get latest recommendation
            latest_rec = db.query(models.Recommendation).filter(
                models.Recommendation.user_id == user.id
            ).order_by(models.Recommendation.created_at.desc()).first()
            
            if latest_rec:
                message = f"""Good morning {user.full_name}!

Your latest soil recommendation:
Crop: {latest_rec.recommended_crop}
Fertilizer: {latest_rec.fertilizer_recommendation}

Have a productive day!
- Rwanda Soil Monitoring Team"""
                
                if user.preferred_contact == 'sms' and user.phone_number:
                    await self.send_sms(user.phone_number, message, db, user.id)
                elif user.preferred_contact == 'email' and user.email:
                    await self.send_email(
                        user.email,
                        "Daily Soil Recommendation",
                        message,
                        db,
                        user.id
                    )

notification_service = NotificationService()