import pytest
from pytest_httpx import HTTPXMock
from src.adapters.telegram import TelegramAdapter
from src.adapters.soroush import SoroushAdapter
from src.models import UnifiedMessage, MessageType, PlatformConfig
from src.utils.media import MediaManager
from unittest.mock import MagicMock

@pytest.fixture
def media_manager():
    return MagicMock(spec=MediaManager)

@pytest.fixture
def platform_config():
    return PlatformConfig(token="fake_token", channel_id="123", name="TestPlatform")

@pytest.mark.asyncio
async def test_telegram_fetch_messages(httpx_mock: HTTPXMock, platform_config, media_manager):
    adapter = TelegramAdapter(platform_config, media_manager)
    
    # Mock Telegram API response
    httpx_mock.add_response(
        url=f"https://api.telegram.org/bot{platform_config.token}/getUpdates?offset=1&timeout=10",
        json={
            "ok": True,
            "result": [
                {
                    "update_id": 100,
                    "message": {
                        "message_id": 1,
                        "text": "hello telegram",
                        "chat": {"id": 123}
                    }
                }
            ]
        }
    )
    
    messages = await adapter.fetch_messages()
    assert len(messages) == 1
    assert messages[0].text == "hello telegram"
    assert messages[0].source_id == "1"

@pytest.mark.asyncio
async def test_soroush_fetch_messages(httpx_mock: HTTPXMock, platform_config, media_manager):
    adapter = SoroushAdapter(platform_config, media_manager)
    
    # Mock Soroush API response
    httpx_mock.add_response(
        url=f"https://bot.splus.ir/v2/{platform_config.token}/getMessage",
        json=[
            {
                "id": "s1",
                "type": "TEXT",
                "body": "hello soroush"
            }
        ]
    )
    
    messages = await adapter.fetch_messages()
    assert len(messages) == 1
    assert messages[0].text == "hello soroush"
    assert messages[0].source_id == "s1"

@pytest.mark.asyncio
async def test_telegram_send_message_text(httpx_mock: HTTPXMock, platform_config, media_manager):
    adapter = TelegramAdapter(platform_config, media_manager)
    msg = UnifiedMessage(source_id="1", source_platform="test", type=MessageType.TEXT, text="send me")
    
    httpx_mock.add_response(
        method="POST",
        url=f"https://api.telegram.org/bot{platform_config.token}/sendMessage",
        status_code=200
    )
    
    success = await adapter.send_message(msg)
    assert success is True
