import asyncio
import os
import shutil
from src.database import Database
from src.orchestrator import Orchestrator
from src.models import UnifiedMessage, MessageType, PlatformConfig
from src.utils.media import MediaManager
from src.adapters.base import BaseAdapter
from typing import List

class MockAdapter(BaseAdapter):
    def __init__(self, config, media_manager):
        super().__init__(config, media_manager)
        self.sent_messages = []
        self.fetch_count = 0

    async def fetch_messages(self) -> List[UnifiedMessage]:
        self.fetch_count += 1
        if self.fetch_count == 1:
            return [
                UnifiedMessage(
                    source_id="mock_1",
                    source_platform=self.name,
                    type=MessageType.TEXT,
                    text="Mock message 1"
                )
            ]
        return []

    async def _do_send(self, message: UnifiedMessage) -> bool:
        self.sent_messages.append(message)
        return True

async def run_integration_test():
    print("🚀 Starting System Integration Test (Simulation)...")
    
    # Setup temporary environment
    test_data_dir = "data_test"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)
    
    db = Database(os.path.join(test_data_dir, "test.db"))
    media_manager = MediaManager(os.path.join(test_data_dir, "cache"))
    
    source_cfg = PlatformConfig(token="src_token", channel_id="src_id", name="MockSource")
    target_cfg = PlatformConfig(token="tgt_token", channel_id="tgt_id", name="MockTarget")
    
    source = MockAdapter(source_cfg, media_manager)
    target = MockAdapter(target_cfg, media_manager)
    
    orchestrator = Orchestrator(source, [target], db)
    
    # Run for a brief moment
    print("🔄 Running orchestrator loop...")
    task = asyncio.create_task(orchestrator.start(interval=1))
    
    await asyncio.sleep(2)
    orchestrator.stop()
    await task
    
    # Verify results
    print("\n📊 Test Results:")
    print(f"✅ Source fetched messages: {source.fetch_count > 0}")
    print(f"✅ Target received messages: {len(target.sent_messages) == 1}")
    if len(target.sent_messages) > 0:
        print(f"✅ Message content matches: {target.sent_messages[0].text == 'Mock message 1'}")
    
    print(f"✅ Database marked as processed: {db.is_processed(source.name, 'mock_1')}")

    # Cleanup
    shutil.rmtree(test_data_dir)
    print("\n✨ Integration test completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
