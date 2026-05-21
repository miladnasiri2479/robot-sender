from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:yourpassword@db:5432/robot_sender"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Bot Tokens
    SOROUSH_TOKEN: str
    TELEGRAM_TOKEN: str
    EITAA_TOKEN: str
    RUBIKA_TOKEN: str
    BALE_TOKEN: str
    
    # Channels
    SOROUSH_CHANNEL_ID: str
    TELEGRAM_CHANNEL_ID: str
    EITAA_CHANNEL_ID: str
    RUBIKA_CHANNEL_ID: str
    BALE_CHANNEL_ID: str
    
    # Polling Interval (seconds)
    POLLING_INTERVAL: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
