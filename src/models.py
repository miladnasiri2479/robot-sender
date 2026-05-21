from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from .database import Base

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    soroush_msg_id = Column(String, unique=True, index=True, nullable=False)
    content_type = Column(String)  # text, image, video, etc.
    content_data = Column(JSON)    # original payload or normalized data
    synced_at = Column(DateTime, default=datetime.utcnow)
    
    # Track status per platform
    telegram_status = Column(String, default="pending")
    eitaa_status = Column(String, default="pending")
    rubika_status = Column(String, default="pending")
    bale_status = Column(String, default="pending")
