import asyncio
import json
import logging
import os
from src.database import Database
from src.orchestrator import Orchestrator
from src.adapters.telegram import TelegramAdapter
from src.adapters.soroush import SoroushAdapter
from src.adapters.bale import BaleAdapter
from src.adapters.eitaa import EitaaAdapter
from src.adapters.rubika import RubikaAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ADAPTERS = {
    "telegram": TelegramAdapter,
    "soroush": SoroushAdapter,
    "bale": BaleAdapter,
    "eitaa": EitaaAdapter,
    "rubika": RubikaAdapter
}

def load_config(path: str = "config.json"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def main():
    try:
        config = load_config()
        
        # Ensure data directory exists for SQLite
        os.makedirs("data", exist_ok=True)
        db = Database("data/sync.db")

        # Initialize Source
        source_name = config["source"]
        source_config = config["credentials"].get(source_name, {})
        source_config["channel_id"] = config["source_channel_id"]
        source_config["name"] = f"Source({source_name})"
        
        if source_name not in ADAPTERS:
            raise ValueError(f"Unsupported source platform: {source_name}")
        
        source_adapter = ADAPTERS[source_name](source_config)

        # Initialize Targets
        target_adapters = []
        for t_name, t_channel_id in config["targets"].items():
            if t_name not in ADAPTERS:
                logger.warning(f"Unsupported target platform: {t_name}")
                continue
            
            t_config = config["credentials"].get(t_name, {})
            t_config["channel_id"] = t_channel_id
            t_config["name"] = f"Target({t_name})"
            target_adapters.append(ADAPTERS[t_name](t_config))

        if not target_adapters:
            raise ValueError("No valid targets configured")

        orchestrator = Orchestrator(source_adapter, target_adapters, db)
        await orchestrator.start(interval=config.get("interval", 60))

    except Exception as e:
        logger.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
