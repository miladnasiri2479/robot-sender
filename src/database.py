import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "data/sync.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_platform TEXT,
                    source_msg_id TEXT,
                    processed_at DATETIME,
                    UNIQUE(source_platform, source_msg_id)
                )
            """)
            conn.commit()

    def is_processed(self, platform: str, msg_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM processed_messages WHERE source_platform = ? AND source_msg_id = ?",
                (platform, msg_id)
            )
            return cursor.fetchone() is not None

    def mark_as_processed(self, platform: str, msg_id: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO processed_messages (source_platform, source_msg_id, processed_at) VALUES (?, ?, ?)",
                    (platform, msg_id, datetime.utcnow())
                )
                conn.commit()
        except sqlite3.IntegrityError:
            pass
