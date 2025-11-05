from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import os
from database import SessionLocal
from notification_service import notification_service

TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Africa/Kigali'))
NOTIFICATION_TIME = os.getenv('NOTIFICATION_TIME', '06:00')

scheduler = AsyncIOScheduler(timezone=TIMEZONE)

async def send_daily_notifications():
    """Job to send daily notifications"""
    db = SessionLocal()
    try:
        await notification_service.send_daily_update(db)
        print(f"Daily notifications sent at {NOTIFICATION_TIME}")
    finally:
        db.close()

def start_scheduler():
    """Start the task scheduler"""
    hour, minute = NOTIFICATION_TIME.split(':')
    
    scheduler.add_job(
        send_daily_notifications,
        trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=TIMEZONE),
        id='daily_notifications',
        name='Send daily soil recommendations',
        replace_existing=True
    )
    
    scheduler.start()
    print(f" Scheduler started - Daily notifications at {NOTIFICATION_TIME} {TIMEZONE}")

def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()