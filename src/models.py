from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"

class UnifiedMessage(BaseModel):
    source_id: str          # Original message ID from the source platform
    source_platform: str    # e.g., "soroush", "telegram"
    type: MessageType
    text: Optional[str] = None
    file_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
