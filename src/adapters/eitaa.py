import httpx
import logging
from typing import List, Optional
from .base import BaseAdapter
from src.models import UnifiedMessage, MessageType

logger = logging.getLogger(__name__)

class EitaaAdapter(BaseAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.token = config["token"]
        self.channel_id = config["channel_id"]
        self.base_url = f"https://eitaayar.ir/api/{self.token}"

    async def fetch_messages(self) -> List[UnifiedMessage]:
        # Eitaayar doesn't support bot polling natively in a standard way
        # Usually requires a dedicated listener or webhook
        return []

    async def send_message(self, message: UnifiedMessage) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.channel_id, "text": message.text}
        
        # If media, we need to download and upload or use remote URL if supported
        if message.type != MessageType.TEXT:
            url = f"{self.base_url}/sendFile"
            # For simplicity, we handle it as a text message or file if URL is provided
            # A full implementation would download the file first
            pass

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload, timeout=30.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Eitaa send failed: {e}")
            return False
