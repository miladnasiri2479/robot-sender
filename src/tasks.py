import os
import logging
from celery import Celery, chain
from celery.schedules import crontab
import httpx
from .config import settings
from .database import SessionLocal
from .models import MessageLog
from .utils.normalizer import normalize_soroush_message
from .adapters.telegram import TelegramAdapter
from .adapters.bale import BaleAdapter
from .adapters.eitaa import EitaaAdapter
from .adapters.rubika import RubikaAdapter
from datetime import datetime

logger = logging.getLogger(__name__)

app = Celery("robot_sender", broker=settings.REDIS_URL)

# Celery Configuration
app.conf.beat_schedule = {
    'poll-soroush-every-minute': {
        'task': 'src.tasks.poll_soroush',
        'schedule': float(settings.POLLING_INTERVAL),
    },
}
app.conf.timezone = 'UTC'

@app.task
def poll_soroush():
    """Poll Soroush API for new messages and dispatch sync tasks."""
    url = f"https://bot.splus.ir/v2/{settings.SOROUSH_TOKEN}/getMessage"
    
    try:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        # Soroush might wrap messages in a 'result' field or return them directly as a list
        messages = data if isinstance(data, list) else data.get("result", [])
        
        if not messages or not isinstance(messages, list):
            return "No new messages or invalid format"

        db = SessionLocal()
        count = 0
        for msg in messages:
            if not isinstance(msg, dict):
                continue
                
            normalized = normalize_soroush_message(msg)
            
            # Duplicate check
            existing = db.query(MessageLog).filter(MessageLog.soroush_msg_id == normalized["id"]).first()
            if existing:
                continue
            
            count += 1
            # Create log entry
            log = MessageLog(
                soroush_msg_id=normalized["id"],
                content_type=normalized["type"],
                content_data=normalized
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            
            # Dispatch individual sync tasks
            sync_to_all_platforms.delay(log.id)
            
        db.close()
        return f"Processed {count} new messages"
    except Exception as e:
        logger.error(f"Soroush polling failed: {e}")
        return str(e)

@app.task
def sync_to_all_platforms(log_id: int):
    """Entry point for syncing a single message to all platforms."""
    # We trigger individual tasks so they can fail/retry independently
    sync_to_telegram.delay(log_id)
    sync_to_bale.delay(log_id)
    sync_to_eitaa.delay(log_id)
    sync_to_rubika.delay(log_id)

@app.task(bind=True, max_retries=5, default_retry_delay=60)
def sync_to_telegram(self, log_id: int):
    return _sync_task(self, log_id, "telegram", TelegramAdapter(settings.TELEGRAM_TOKEN, settings.TELEGRAM_CHANNEL_ID))

@app.task(bind=True, max_retries=5, default_retry_delay=60)
def sync_to_bale(self, log_id: int):
    return _sync_task(self, log_id, "bale", BaleAdapter(settings.BALE_TOKEN, settings.BALE_CHANNEL_ID))

@app.task(bind=True, max_retries=5, default_retry_delay=60)
def sync_to_eitaa(self, log_id: int):
    return _sync_task(self, log_id, "eitaa", EitaaAdapter(settings.EITAA_TOKEN, settings.EITAA_CHANNEL_ID))

@app.task(bind=True, max_retries=5, default_retry_delay=60)
def sync_to_rubika(self, log_id: int):
    return _sync_task(self, log_id, "rubika", RubikaAdapter(settings.RUBIKA_TOKEN, settings.RUBIKA_CHANNEL_ID))

def _sync_task(task_obj, log_id: int, platform: str, adapter):
    db = SessionLocal()
    log = db.query(MessageLog).get(log_id)
    if not log:
        db.close()
        return "Log not found"

    data = log.content_data
    success = False
    
    try:
        if data["type"] == "text":
            success = adapter.send_text(data["text"])
        elif data["type"] == "image":
            success = adapter.send_image(data["file_url"], data["text"])
        elif data["type"] == "video":
            success = adapter.send_video(data["file_url"], data["text"])
        elif data["type"] == "file":
            success = adapter.send_file(data["file_url"], data["text"])

        if success:
            setattr(log, f"{platform}_status", "success")
        else:
            setattr(log, f"{platform}_status", "failed")
            # Trigger celery retry
            raise Exception(f"{platform} adapter returned False")
            
        db.commit()
    except Exception as exc:
        setattr(log, f"{platform}_status", f"error: {str(exc)}")
        db.commit()
        db.close()
        # Exponential backoff retry
        raise task_obj.retry(exc=exc, countdown=2 ** task_obj.request.retries * 60)
    
    db.close()
    return f"Synced to {platform}"
