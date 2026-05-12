# 🐍 Backend — FastAPI Application

## Overview

The backend is built with **FastAPI** — a modern, fast Python web framework.
SQLite is used as the database for simplicity and portability.

---

## File Structure
app/
├── main.py       # Application entrypoint, all API routes
├── models.py     # Pydantic request/response schemas
├── database.py   # SQLite connection and initialization
└── cleanup.py    # Background task for expired paste deletion

---

## How It Works
HTTP Request
↓
FastAPI router (main.py)
↓
Pydantic validation (models.py)
↓
SQLite query (database.py)
↓
JSON Response
---

## API Endpoints

### Create Paste
```http
POST /api/paste
Content-Type: application/json

{
  "content": "print('hello world')",
  "syntax": "python",
  "ttl_seconds": 86400
}
```
Response:
```json
{
  "id": "abc12345",
  "url": "/p/abc12345",
  "syntax": "python",
  "ttl_seconds": 86400,
  "expires_at": "2026-05-13T10:00:00"
}
```

### Get Paste
```http
GET /p/{id}
```
Response:
```json
{
  "id": "abc12345",
  "content": "print('hello world')",
  "syntax": "python",
  "views": 1
}
```

### Get Raw Content
```http
GET /api/paste/{id}/raw
```
Returns plain text content.

### Delete Paste
```http
DELETE /api/paste/{id}
```
Returns `{"message": "Paste deleted"}`

### Health Check
```http
GET /health
```
```json
{
  "status": "ok",
  "pastes_count": 42
}
```

---

## Database Schema

```sql
CREATE TABLE pastes (
    id          TEXT PRIMARY KEY,
    content     TEXT NOT NULL,
    syntax      TEXT DEFAULT 'text',
    ttl_seconds INTEGER DEFAULT 86400,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    views       INTEGER DEFAULT 0
);
```

---

## Auto-Expiry

A background task runs every **5 minutes** and deletes expired pastes:

```sql
DELETE FROM pastes
WHERE datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime('now')
```

---

## Adding a New Endpoint

1. Add route in `main.py`:
```python
@app.get("/api/example")
async def example(db: aiosqlite.Connection = Depends(get_db)):
    return {"example": "response"}
```

2. Add Pydantic model in `models.py` if needed:
```python
class ExampleResponse(BaseModel):
    example: str
```

---

## Running Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`
