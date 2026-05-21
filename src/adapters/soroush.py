import httpx
import logging
from typing import List, Optional
from .base import BaseAdapter
from src.models import UnifiedMessage, MessageType

logger = logging.getLogger(__name__)

class SoroushAdapter(BaseAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.token = config["token"]
        self.channel_id = config.get("channel_id")
        self.base_url = f"https://bot.splus.ir/v2/{self.token}"

    async def fetch_messages(self) -> List[UnifiedMessage]:
        url = f"{self.base_url}/getMessage"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                messages = data if isinstance(data, list) else data.get("result", [])
                
                unified = []
                for msg in messages:
                    unified.append(self._normalize(msg))
                return unified
        except Exception as e:
            logger.error(f"Soroush fetch failed: {e}")
            return []

    async def send_message(self, message: UnifiedMessage) -> bool:
        # Implementation for sending to Soroush
        # Soroush uses POST /sendMessage
        url = f"{self.base_url}/sendMessage"
        payload = {
            "to": self.channel_id,
            "type": "TEXT",
            "body": message.text
        }
        
        if message.type == MessageType.IMAGE:
            payload["type"] = "IMAGE"
            payload["fileUrl"] = message.file_url
        elif message.type == MessageType.VIDEO:
            payload["type"] = "VIDEO"
            payload["fileUrl"] = message.file_url
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Soroush send failed: {e}")
            return False

    def _normalize(self, msg: dict) -> UnifiedMessage:
        msg_id = str(msg.get("id"))
        msg_type = msg.get("type", "TEXT").upper()
        
        m_type = MessageType.TEXT
        if msg_type == "IMAGE": m_type = MessageType.IMAGE
        elif msg_type == "VIDEO": m_type = MessageType.VIDEO
        
        return UnifiedMessage(
            source_id=msg_id,
            source_platform="soroush",
            type=m_type,
            text=msg.get("body"),
            file_url=msg.get("fileUrl"),
            raw_data=msg
        )
