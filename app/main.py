from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import PlainTextResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from nanoid import generate
from datetime import datetime, timedelta
from app.models import PasteCreate, PasteResponse
from app.database import get_db, init_db
from app.cleanup import cleanup_loop
from prometheus_fastapi_instrumentator import Instrumentator
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
Instrumentator().instrument(app).expose(app)
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
    request: Request,
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

    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Paste {row['id']}</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--bg:#0a0e17;--bg2:#0f1623;--bg3:#151d2e;--blue:#3b82f6;--cyan:#22d3ee;--green:#22c55e;--text:#e2e8f0;--muted:#64748b;--border:rgba(59,130,246,0.15);--mono:'JetBrains Mono',monospace}}
    body{{background:var(--bg);color:var(--text);font-family:var(--mono);min-height:100vh}}
    body::before{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(59,130,246,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,0.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0}}
    nav{{position:sticky;top:0;z-index:100;display:flex;justify-content:space-between;align-items:center;padding:16px 40px;background:rgba(10,14,23,0.9);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}}
    .logo{{font-size:18px;font-weight:700;color:var(--blue);text-decoration:none}}
    .logo span{{color:var(--cyan)}}
    .new-btn{{background:var(--blue);color:#fff;border:none;padding:8px 16px;border-radius:6px;font-family:var(--mono);font-size:12px;cursor:pointer;text-decoration:none;transition:all 0.2s}}
    .new-btn:hover{{background:#1d4ed8;transform:translateY(-1px)}}
    main{{position:relative;z-index:1;max-width:900px;margin:0 auto;padding:40px 24px}}
    .meta{{display:flex;gap:16px;font-size:11px;color:var(--muted);margin-bottom:20px;flex-wrap:wrap;align-items:center}}
    .tag{{background:rgba(59,130,246,0.1);border:1px solid var(--border);color:var(--blue);font-size:11px;padding:3px 8px;border-radius:4px}}
    .code-box{{background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden}}
    .code-header{{display:flex;align-items:center;gap:8px;padding:10px 16px;background:var(--bg3);border-bottom:1px solid var(--border)}}
    .dot{{width:10px;height:10px;border-radius:50%}}
    .dot-r{{background:#ef4444}}.dot-y{{background:#f59e0b}}.dot-g{{background:#22c55e}}
    .filename{{font-size:11px;color:var(--muted);margin-left:8px}}
    .copy-btn{{margin-left:auto;background:var(--bg2);border:1px solid var(--border);color:var(--muted);font-family:var(--mono);font-size:11px;padding:5px 12px;border-radius:5px;cursor:pointer;transition:all 0.2s}}
    .copy-btn:hover{{color:var(--blue);border-color:var(--blue)}}
    pre{{padding:0;overflow-x:auto;font-size:14px;line-height:1.7;}} pre code.hljs{{padding:24px;display:block;white-space:pre-wrap;word-break:break-word;}}
    footer{{position:relative;z-index:1;text-align:center;padding:20px;font-size:11px;color:var(--muted);border-top:1px solid var(--border);margin-top:40px}}
    @media(max-width:600px){{nav{{padding:12px 20px}}main{{padding:24px 16px}}}}
  </style>
</head>
<body>
  <nav>
    <a class="logo" href="/ui">paste<span>bin</span></a>
    <a class="new-btn" href="/ui">+ New Paste</a>
  </nav>
  <main>
    <div class="meta">
      <span>🆔 {row['id']}</span>
      <span>🔤 <span class="tag">{row['syntax']}</span></span>
      <span>👁 {row['views'] + 1} views</span>
    </div>
    <div class="code-box">
      <div class="code-header">
        <div class="dot dot-r"></div>
        <div class="dot dot-y"></div>
        <div class="dot dot-g"></div>
        <span class="filename">paste.{row['syntax']}</span>
        <button class="copy-btn" onclick="navigator.clipboard.writeText(document.querySelector('pre').textContent).then(()=>{{this.textContent='Copied!';setTimeout(()=>this.textContent='Copy',2000)}})">Copy</button>
      </div>
      <pre><code class="language-{row['syntax']}">{row['content']}</code></pre>
    </div>
  </main>
  <footer>pastebin · self-hosted · powered by FastAPI + SQLite</footer>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script>hljs.highlightAll();</script>
</body>
</html>"""
        return HTMLResponse(html)

    return {{
        "id": row["id"],
        "content": row["content"],
        "syntax": row["syntax"],
        "views": row["views"] + 1,
    }}

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
