# ── Етап 1: builder ──────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Встановлюємо залежності окремо для кешування
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Етап 2: final ────────────────────────────────
FROM python:3.12-slim

# Створюємо non-root user для безпеки
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Копіюємо залежності з builder
COPY --from=builder /root/.local /home/appuser/.local

# Копіюємо код
COPY app/ ./app/
COPY frontend/ ./frontend/

# Створюємо папку для бази даних
RUN mkdir -p /data && chown appuser:appuser /data

# Переключаємось на non-root user
USER appuser

# Змінні середовища
ENV PATH=/home/appuser/.local/bin:$PATH
ENV DB_PATH=/data/pastebin.db
ENV PYTHONPATH=/app

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
