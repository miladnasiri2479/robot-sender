import httpx
import logging
from typing import Optional
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class BaleAdapter(BaseAdapter):
    def __init__(self, token: str, chat_id: str):
        super().__init__(token, chat_id)
        self.base_url = f"https://tapi.bale.ai/bot{self.token}"

    def send_text(self, text: str) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text
        }
        return self._make_request(url, payload)

    def send_image(self, image_url: str, caption: Optional[str] = None) -> bool:
        url = f"{self.base_url}/sendPhoto"
        payload = {
            "chat_id": self.chat_id,
            "photo": image_url,
            "caption": caption
        }
        return self._make_request(url, payload)

    def send_video(self, video_url: str, caption: Optional[str] = None) -> bool:
        url = f"{self.base_url}/sendVideo"
        payload = {
            "chat_id": self.chat_id,
            "video": video_url,
            "caption": caption
        }
        return self._make_request(url, payload)

    def send_file(self, file_url: str, caption: Optional[str] = None) -> bool:
        url = f"{self.base_url}/sendDocument"
        payload = {
            "chat_id": self.chat_id,
            "document": file_url,
            "caption": caption
        }
        return self._make_request(url, payload)

    def _make_request(self, url: str, payload: dict) -> bool:
        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Bale request failed: {e}")
            return False
