import surfari_logger
import config
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager

logger = surfari_logger.getLogger(__name__)

@contextmanager
def get_db_connection_sync():
    path = os.path.join(config.PROJECT_ROOT, "credentials.db")
    logger.debug(f"Opening DB at {path} (sync)")
    conn = sqlite3.connect(path)
    try:
        yield conn
    finally:
        conn.close()

@asynccontextmanager
async def get_db_connection():
    path = os.path.join(config.PROJECT_ROOT, "credentials.db")
    logger.debug(f"Opening DB at {path} (async)")
    conn = sqlite3.connect(path)
    try:
        yield conn
    finally:
        conn.close()
