from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Що приймаємо від користувача
class PasteCreate(BaseModel):
    content: str
    syntax: str = "text"
    ttl_seconds: int = 86400  # 24 години за замовчуванням

# Що повертаємо користувачу
class PasteResponse(BaseModel):
    id: str
    url: str
    syntax: str
    ttl_seconds: int
    expires_at: str
