import httpx
import logging
from typing import List
from .base import BaseAdapter
from src.models import UnifiedMessage, MessageType, PlatformConfig
from src.utils.media import MediaManager

logger = logging.getLogger(__name__)

class BaleAdapter(BaseAdapter):
    def __init__(self, config: PlatformConfig, media_manager: MediaManager):
        super().__init__(config, media_manager)
        self.base_url = f"https://tapi.bale.ai/bot{self.config.token}"
        self.last_update_id = 0

    async def fetch_messages(self) -> List[UnifiedMessage]:
        url = f"{self.base_url}/getUpdates"
        params = {"offset": self.last_update_id + 1}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
                if not data.get("ok"):
                    return []
                
                updates = data.get("result", [])
                unified = []
                for update in updates:
                    self.last_update_id = max(self.last_update_id, update["update_id"])
                    msg = update.get("message")
                    if msg:
                        unified.append(self._normalize(msg))
                return unified
        except Exception as e:
            logger.error(f"Bale fetch failed: {e}")
            return []

    async def _do_send(self, message: UnifiedMessage) -> bool:
        method = "sendMessage"
        payload = {"chat_id": self.config.channel_id}
        
        if message.type == MessageType.TEXT:
            payload["text"] = message.text
        elif message.type == MessageType.IMAGE:
            method = "sendPhoto"
            payload["photo"] = message.file_url
            payload["caption"] = message.text
        elif message.type == MessageType.VIDEO:
            method = "sendVideo"
            payload["video"] = message.file_url
            payload["caption"] = message.text
            
        url = f"{self.base_url}/{method}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Bale send failed: {e}")
            return False

    def _normalize(self, msg: dict) -> UnifiedMessage:
        m_type = MessageType.TEXT
        file_url = None
        if "photo" in msg:
            m_type = MessageType.IMAGE
        elif "video" in msg:
            m_type = MessageType.VIDEO
        
        return UnifiedMessage(
            source_id=str(msg["message_id"]),
            source_platform="bale",
            type=m_type,
            text=msg.get("text") or msg.get("caption"),
            file_url=file_url,
            raw_data=msg
        )
