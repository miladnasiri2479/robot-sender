import httpx
import logging
from typing import List
from .base import BaseAdapter
from src.models import UnifiedMessage, PlatformConfig
from src.utils.media import MediaManager

logger = logging.getLogger(__name__)

class RubikaAdapter(BaseAdapter):
    def __init__(self, config: PlatformConfig, media_manager: MediaManager):
        super().__init__(config, media_manager)
        self.base_url = f"https://botapi.rubika.ir/v3/{self.config.token}"

    async def fetch_messages(self) -> List[UnifiedMessage]:
        url = f"{self.base_url}/getUpdates"
        try:
            async with httpx.AsyncClient() as client:
                await client.get(url, timeout=10.0)
                # Simplified polling logic for Rubika
                return [] 
        except Exception as e:
            logger.error(f"Rubika fetch failed: {e}")
            return []

    async def _do_send(self, message: UnifiedMessage) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.config.channel_id, "text": message.text}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Rubika send failed: {e}")
            return False
