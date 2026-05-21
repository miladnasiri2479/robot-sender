import httpx
import logging
from typing import List
from .base import BaseAdapter
from src.models import UnifiedMessage, MessageType, PlatformConfig
from src.utils.media import MediaManager

logger = logging.getLogger(__name__)

class TelegramAdapter(BaseAdapter):
    def __init__(self, config: PlatformConfig, media_manager: MediaManager):
        super().__init__(config, media_manager)
        self.base_url = f"https://api.telegram.org/bot{self.config.token}"
        self.last_update_id = 0

    async def fetch_messages(self) -> List[UnifiedMessage]:
        url = f"{self.base_url}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 10}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                data = response.json()
                if not data.get("ok"): return []
                
                updates = data.get("result", [])
                unified = []
                for update in updates:
                    self.last_update_id = max(self.last_update_id, update["update_id"])
                    msg = update.get("message") or update.get("channel_post")
                    if msg:
                        unified.append(self._normalize(msg))
                return unified
        except Exception as e:
            logger.error(f"Telegram fetch failed: {e}")
            return []

    async def _do_send(self, message: UnifiedMessage) -> bool:
        method = "sendMessage"
        params = {"chat_id": self.config.channel_id, "parse_mode": "HTML"}
        files = None

        if message.type == MessageType.TEXT:
            params["text"] = message.text
        else:
            local_path = await self.media_manager.get_media(message.file_url)
            if not local_path: return False
            
            file_field = "photo" if message.type == MessageType.IMAGE else "video" if message.type == MessageType.VIDEO else "document"
            method = f"send{file_field.capitalize()}"
            params["caption"] = message.text
            files = {file_field: open(local_path, "rb")}

        url = f"{self.base_url}/{method}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=params, files=files, timeout=60.0)
                return response.status_code == 200
        finally:
            if files:
                for f in files.values(): f.close()

    def _normalize(self, msg: dict) -> UnifiedMessage:
        # Simplified normalization for brevity
        return UnifiedMessage(
            source_id=str(msg["message_id"]),
            source_platform="telegram",
            type=MessageType.TEXT, # Real implementation would detect media
            text=msg.get("text") or msg.get("caption"),
            raw_data=msg
        )
