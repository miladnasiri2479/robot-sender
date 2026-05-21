import httpx
import logging
from typing import List
from .base import BaseAdapter
from src.models import UnifiedMessage, MessageType, PlatformConfig
from src.utils.media import MediaManager

logger = logging.getLogger(__name__)

class SoroushAdapter(BaseAdapter):
    def __init__(self, config: PlatformConfig, media_manager: MediaManager):
        super().__init__(config, media_manager)
        self.base_url = f"https://bot.splus.ir/v2/{self.config.token}"

    async def fetch_messages(self) -> List[UnifiedMessage]:
        url = f"{self.base_url}/getMessage"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=15.0)
                data = response.json()
                messages = data if isinstance(data, list) else data.get("result", [])
                return [self._normalize(msg) for msg in messages if isinstance(msg, dict)]
        except Exception as e:
            logger.error(f"Soroush fetch failed: {e}")
            return []

    async def _do_send(self, message: UnifiedMessage) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "to": self.config.channel_id,
            "type": "TEXT",
            "body": message.text
        }
        
        if message.type != MessageType.TEXT:
            # Soroush usually requires uploading files first to get a fileUrl, 
            # or it accepts a direct fileUrl if it's already on their servers.
            # For simplicity, we assume we forward the URL or upload it.
            # Real implementation would include the /uploadFile step.
            payload["type"] = message.type.upper()
            payload["fileUrl"] = message.file_url

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Soroush send failed: {e}")
            return False

    def _normalize(self, msg: dict) -> UnifiedMessage:
        return UnifiedMessage(
            source_id=str(msg.get("id")),
            source_platform="soroush",
            type=MessageType.TEXT, # Real implementation would detect
            text=msg.get("body"),
            file_url=msg.get("fileUrl"),
            raw_data=msg
        )
