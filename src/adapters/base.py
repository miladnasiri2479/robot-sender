from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAdapter(ABC):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    @abstractmethod
    def send_text(self, text: str) -> bool:
        pass

    @abstractmethod
    def send_image(self, image_url: str, caption: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    def send_video(self, video_url: str, caption: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    def send_file(self, file_url: str, caption: Optional[str] = None) -> bool:
        pass
