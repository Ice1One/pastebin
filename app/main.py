from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from nanoid import generate
from datetime import datetime, timedelta
from app.models import PasteCreate, PasteResponse
from app.database import get_db, init_db
from app.cleanup import cleanup_loop
import aiosqlite
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(cleanup_loop())
    logging.info("Cleanup task started")
    yield
    task.cancel()
    logging.info("Cleanup task stopped")

app = FastAPI(title="Pastebin API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/ui")
def ui():
    return FileResponse("frontend/index.html")

@app.get("/")
def root():
    return {"message": "Pastebin API працює!"}

@app.get("/health")
async def health(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT COUNT(*) FROM pastes") as cursor:
        row = await cursor.fetchone()
        count = row[0]
    return {"status": "ok", "pastes_count": count}

@app.post("/api/paste", response_model=PasteResponse)
async def create_paste(
    paste: PasteCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    paste_id = generate(size=8)
    expires_at = datetime.now() + timedelta(seconds=paste.ttl_seconds)
    await db.execute(
        """INSERT INTO pastes (id, content, syntax, ttl_seconds)
           VALUES (?, ?, ?, ?)""",
        (paste_id, paste.content, paste.syntax, paste.ttl_seconds)
    )
    await db.commit()
    return PasteResponse(
        id=paste_id,
        url=f"/p/{paste_id}",
        syntax=paste.syntax,
        ttl_seconds=paste.ttl_seconds,
        expires_at=expires_at.isoformat(),
    )

@app.get("/p/{paste_id}")
async def get_paste(
    paste_id: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    async with db.execute(
        """SELECT * FROM pastes WHERE id = ?
           AND datetime(created_at, '+' || ttl_seconds || ' seconds')
           > datetime('now')""",
        (paste_id,)
    ) as cursor:
        row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Paste not found or expired")
    await db.execute(
        "UPDATE pastes SET views = views + 1 WHERE id = ?",
        (paste_id,)
    )
    await db.commit()
    return {
        "id": row["id"],
        "content": row["content"],
        "syntax": row["syntax"],
        "views": row["views"] + 1,
    }

@app.get("/api/paste/{paste_id}/raw")
async def get_paste_raw(
    paste_id: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    async with db.execute(
        "SELECT content FROM pastes WHERE id = ?",
        (paste_id,)
    ) as cursor:
        row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Paste not found")
    return PlainTextResponse(row["content"])

@app.delete("/api/paste/{paste_id}")
async def delete_paste(
    paste_id: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    async with db.execute(
        "SELECT id FROM pastes WHERE id = ?",
        (paste_id,)
    ) as cursor:
        row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Paste not found")
    await db.execute("DELETE FROM pastes WHERE id = ?", (paste_id,))
    await db.commit()
    return {"message": "Paste deleted"}
