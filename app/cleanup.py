import asyncio
import aiosqlite
import logging
from app.database import DB_PATH

logger = logging.getLogger(__name__)

async def delete_expired_pastes():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            DELETE FROM pastes
            WHERE datetime(created_at, '+' || ttl_seconds || ' seconds')
            < datetime('now')
        """)
        await db.commit()
        deleted = cursor.rowcount
        if deleted > 0:
            logger.info(f"Cleanup: deleted {deleted} expired pastes")
        return deleted

async def cleanup_loop():
    while True:
        try:
            await delete_expired_pastes()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        await asyncio.sleep(300)  # 5 хвилин
