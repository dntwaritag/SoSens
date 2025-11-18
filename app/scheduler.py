from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from .config import settings
from .database import SessionLocal
from .notification_service import notification_service

scheduler = AsyncIOScheduler(timezone=pytz.timezone(settings.TIMEZONE))

async def send_daily_notifications():
    db = SessionLocal()
    try:
        await notification_service.send_daily_weather(db)
        print(f"✓ Daily weather notifications sent at {settings.NOTIFICATION_TIME}")
    finally:
        db.close()

def start_scheduler():
    hour, minute = settings.NOTIFICATION_TIME.split(':')
    scheduler.add_job(
        send_daily_notifications,
        trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=pytz.timezone(settings.TIMEZONE)),
        id='daily_weather',
        name='Send daily weather notifications',
        replace_existing=True
    )
    scheduler.start()
    print(f"✓ Scheduler started - Daily notifications at {settings.NOTIFICATION_TIME}")

def stop_scheduler():
    scheduler.shutdown()