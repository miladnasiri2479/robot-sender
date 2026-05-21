import httpx
import logging
from typing import List
from .base import BaseAdapter
from src.models import UnifiedMessage, MessageType, PlatformConfig
from src.utils.media import MediaManager

logger = logging.getLogger(__name__)

class EitaaAdapter(BaseAdapter):
    def __init__(self, config: PlatformConfig, media_manager: MediaManager):
        super().__init__(config, media_manager)
        self.base_url = f"https://eitaayar.ir/api/{self.config.token}"

    async def fetch_messages(self) -> List[UnifiedMessage]:
        # Eitaayar doesn't support bot polling natively in a standard way
        return []

    async def _do_send(self, message: UnifiedMessage) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.config.channel_id, "text": message.text}
        
        # If media, we handle it as a text message or file if URL is provided
        if message.type != MessageType.TEXT:
            url = f"{self.base_url}/sendFile"
            # A full implementation would download the file first

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload, timeout=30.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Eitaa send failed: {e}")
            return False
