import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "pastebin.db")

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pastes (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                syntax TEXT DEFAULT 'text',
                ttl_seconds INTEGER DEFAULT 86400,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_expiry
            ON pastes (created_at, ttl_seconds)
        """)
        await db.commit()
