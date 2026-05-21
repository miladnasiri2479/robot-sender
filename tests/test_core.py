import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.orchestrator import Orchestrator
from src.models import UnifiedMessage, MessageType, PlatformConfig
from src.utils.resilience import CircuitBreaker, TokenBucket, CircuitState

@pytest.mark.asyncio
async def test_orchestrator_deduplication():
    # Mock dependencies
    source = AsyncMock()
    target = AsyncMock()
    db = MagicMock()
    
    msg = UnifiedMessage(source_id="1", source_platform="test", type=MessageType.TEXT, text="hello")
    source.fetch_messages.return_value = [msg]
    source.name = "Source"
    target.name = "Target"
    
    # Message already processed
    db.is_processed.return_value = True
    
    orchestrator = Orchestrator(source, [target], db)
    # Run one loop iteration
    task = asyncio.create_task(orchestrator.start(interval=0.1))
    await asyncio.sleep(0.2)
    orchestrator.stop()
    await task
    
    target.send_message.assert_not_called()

@pytest.mark.asyncio
async def test_circuit_breaker_opening():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    
    async def failing_func():
        raise Exception("API Down")
    
    # 1st failure
    with pytest.raises(Exception):
        await cb.call(failing_func)
    assert cb.state == CircuitState.CLOSED
    
    # 2nd failure -> OPEN
    with pytest.raises(Exception):
        await cb.call(failing_func)
    assert cb.state == CircuitState.OPEN
    
    # Subsequent call while OPEN
    result = await cb.call(failing_func)
    assert result is None

@pytest.mark.asyncio
async def test_token_bucket():
    bucket = TokenBucket(rate_per_sec=10, capacity=1)
    
    # 1st consume
    assert await bucket.consume() is True
    # 2nd consume immediately -> False
    assert await bucket.consume() is False
    
    # Wait for refill
    await asyncio.sleep(0.15)
    assert await bucket.consume() is True
