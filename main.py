import asyncio
import logging
from fastapi import FastAPI
import uvicorn
from src.config import load_app_config
from src.database import Database
from src.orchestrator import Orchestrator
from src.utils.media import MediaManager
from src.adapters.telegram import TelegramAdapter
from src.adapters.soroush import SoroushAdapter
from src.adapters.bale import BaleAdapter
from src.adapters.eitaa import EitaaAdapter
from src.adapters.rubika import RubikaAdapter
from src.models import PlatformConfig

app = FastAPI()
orchestrator = None

@app.get("/health")
def health():
    return {"status": "healthy", "orchestrator_running": orchestrator.is_running if orchestrator else False}

async def run_sync():
    global orchestrator
    config = load_app_config()
    
    # Configure logging level
    logging.getLogger().setLevel(config.log_level)
    
    db = Database(config.db_path)
    media_manager = MediaManager(config.cache_dir)
    
    adapters_map = {
        "telegram": TelegramAdapter,
        "soroush": SoroushAdapter,
        "bale": BaleAdapter,
        "eitaa": EitaaAdapter,
        "rubika": RubikaAdapter
    }
    
    # Initialize Source
    source_cls = adapters_map.get(config.source)
    source_creds = config.credentials.get(config.source, {})
    source_p_config = PlatformConfig(
        token=source_creds.get("token", ""),
        channel_id=config.source_channel_id,
        name=f"Source({config.source})"
    )
    source_adapter = source_cls(source_p_config, media_manager)
    
    # Initialize Targets
    targets = []
    for t_name, t_channel_id in config.targets.items():
        t_cls = adapters_map.get(t_name)
        t_creds = config.credentials.get(t_name, {})
        t_p_config = PlatformConfig(
            token=t_creds.get("token", ""),
            channel_id=t_channel_id,
            name=f"Target({t_name})"
        )
        targets.append(t_cls(t_p_config, media_manager))
    
    orchestrator = Orchestrator(source_adapter, targets, db)
    await orchestrator.start(interval=config.interval)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_sync())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
