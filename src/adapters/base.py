from abc import ABC, abstractmethod
from typing import List, Optional
import logging
from src.models import UnifiedMessage, PlatformConfig
from src.utils.resilience import CircuitBreaker, TokenBucket
from src.utils.media import MediaManager

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    def __init__(self, config: PlatformConfig, media_manager: MediaManager):
        self.config = config
        self.name = config.name
        self.media_manager = media_manager
        
        # Resilience components
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=300)
        # Default rate limit: 1 request per second, capacity 5
        self.rate_limiter = TokenBucket(rate_per_sec=1.0, capacity=5.0)

    @abstractmethod
    async def fetch_messages(self) -> List[UnifiedMessage]:
        pass

    @abstractmethod
    async def _do_send(self, message: UnifiedMessage) -> bool:
        pass

    async def send_message(self, message: UnifiedMessage) -> bool:
        """Wrapped send method with rate limiting and circuit breaker."""
        await self.rate_limiter.wait_for_token()
        try:
            return await self.circuit_breaker.call(self._do_send, message)
        except Exception as e:
            logger.error(f"Platform {self.name} is failing persistently: {e}")
            return False
