from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"

class UnifiedMessage(BaseModel):
    source_id: str
    source_platform: str
    type: MessageType
    text: Optional[str] = None
    file_url: Optional[str] = None
    media_path: Optional[str] = None  # Local path for cached/downloaded media
    raw_data: Optional[Dict[str, Any]] = None

class PlatformConfig(BaseModel):
    token: str
    channel_id: str
    name: str

class AppConfig(BaseModel):
    source: str
    source_channel_id: str
    interval: int = Field(default=60, ge=10)
    targets: Dict[str, str]  # platform_name: channel_id
    credentials: Dict[str, Dict[str, str]]
    cache_dir: str = "data/cache"
    db_path: str = "data/sync.db"
    log_level: str = "INFO"
