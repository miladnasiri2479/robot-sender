import httpx
import logging
from typing import List, Optional
from .base import BaseAdapter
from src.models import UnifiedMessage, MessageType

logger = logging.getLogger(__name__)

class RubikaAdapter(BaseAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.token = config["token"]
        self.channel_id = config["channel_id"]
        self.base_url = f"https://botapi.rubika.ir/v3/{self.token}"

    async def fetch_messages(self) -> List[UnifiedMessage]:
        url = f"{self.base_url}/getUpdates"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                data = response.json()
                # Simplified polling logic for Rubika
                return [] 
        except Exception as e:
            logger.error(f"Rubika fetch failed: {e}")
            return []

    async def send_message(self, message: UnifiedMessage) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.channel_id, "text": message.text}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Rubika send failed: {e}")
            return False
