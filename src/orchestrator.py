import asyncio
import logging
from typing import List, Type
from src.adapters.base import BaseAdapter
from src.database import Database
from src.models import UnifiedMessage

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, source: BaseAdapter, targets: List[BaseAdapter], db: Database):
        self.source = source
        self.targets = targets
        self.db = db
        self.is_running = False

    async def start(self, interval: int = 60):
        self.is_running = True
        logger.info(f"Starting orchestrator: {self.source.name} -> {[t.name for t in self.targets]}")
        
        while self.is_running:
            try:
                messages = await self.source.fetch_messages()
                for msg in messages:
                    if not self.db.is_processed(msg.source_platform, msg.source_id):
                        logger.info(f"New message from {msg.source_platform}: {msg.source_id}")
                        
                        # Forward to all targets concurrently
                        tasks = [self._safe_send(target, msg) for target in self.targets]
                        results = await asyncio.gather(*tasks)
                        
                        if any(results):
                            self.db.mark_as_processed(msg.source_platform, msg.source_id)
                
            except Exception as e:
                logger.error(f"Orchestrator loop error: {e}")
            
            await asyncio.sleep(interval)

    async def _safe_send(self, target: BaseAdapter, message: UnifiedMessage) -> bool:
        try:
            success = await target.send_message(message)
            if success:
                logger.info(f"Successfully forwarded to {target.name}")
            else:
                logger.warning(f"Failed to forward to {target.name}")
            return success
        except Exception as e:
            logger.error(f"Error sending to {target.name}: {e}")
            return False

    def stop(self):
        self.is_running = False
