from abc import ABC, abstractmethod
from typing import List, Optional
from src.models import UnifiedMessage

class BaseAdapter(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.name = config.get("name", "unknown")

    @abstractmethod
    async def fetch_messages(self) -> List[UnifiedMessage]:
        """Fetch new messages from the platform."""
        pass

    @abstractmethod
    async def send_message(self, message: UnifiedMessage) -> bool:
        """Send a normalized message to the platform."""
        pass
