import httpx
import logging
from typing import Optional
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class EitaaAdapter(BaseAdapter):
    def __init__(self, token: str, chat_id: str):
        super().__init__(token, chat_id)
        self.base_url = f"https://eitaayar.ir/api/{self.token}"

    def send_text(self, text: str) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text
        }
        return self._make_request(url, payload)

    def send_image(self, image_url: str, caption: Optional[str] = None) -> bool:
        return self.send_file(image_url, caption)

    def send_video(self, video_url: str, caption: Optional[str] = None) -> bool:
        return self.send_file(video_url, caption)

    def send_file(self, file_url: str, caption: Optional[str] = None) -> bool:
        url = f"{self.base_url}/sendFile"
        return self._make_file_request(url, file_url, caption)

    def _make_request(self, url: str, payload: dict) -> bool:
        try:
            with httpx.Client() as client:
                response = client.post(url, data=payload, timeout=30.0)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Eitaa request failed: {e}")
            return False

    def _make_file_request(self, url: str, file_url: str, caption: Optional[str]) -> bool:
        try:
            with httpx.Client() as client:
                file_response = client.get(file_url)
                file_response.raise_for_status()
                
                files = {'file': ('file', file_response.content)}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption
                
                response = client.post(url, data=data, files=files, timeout=60.0)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Eitaa file request failed: {e}")
            return False
