import asyncio
import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                logger.warning("Circuit breaker is OPEN. Skipping call.")
                return None

        try:
            result = await func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
                logger.info("Circuit breaker CLOSED after successful call")
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            logger.error(f"Call failed (Failure {self.failures}/{self.failure_threshold}): {e}")
            
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error("Circuit breaker state changed to OPEN")
            raise e

class TokenBucket:
    def __init__(self, rate_per_sec, capacity):
        self.rate = rate_per_sec
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def consume(self):
        async with self.lock:
            now = time.time()
            passed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + passed * self.rate)
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    async def wait_for_token(self):
        while not await self.consume():
            await asyncio.sleep(0.1)
