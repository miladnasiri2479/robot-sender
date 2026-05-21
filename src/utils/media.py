import httpx
import os
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MediaManager:
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / url_hash

    async def get_media(self, url: str) -> Optional[Path]:
        """Download media using streaming and return local path."""
        if not url: return None
        
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            logger.info(f"Using cached media for {url}")
            return cache_path

        logger.info(f"Downloading media: {url}")
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", url, timeout=60.0) as response:
                    response.raise_for_status()
                    with open(cache_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
            return cache_path
        except Exception as e:
            logger.error(f"Failed to download media {url}: {e}")
            if cache_path.exists(): cache_path.unlink()
            return None

    def cleanup(self):
        """Optionally cleanup old cache files."""
        pass
