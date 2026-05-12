# 📋 Pastebin — Self-Hosted

> A self-hosted, ephemeral pastebin with auto-expiring pastes, deployed on AWS EC2 via GitHub Actions.

![Build](https://github.com/Ice1One/pastebin/actions/workflows/build.yml/badge.svg)
![Deploy](https://github.com/Ice1One/pastebin/actions/workflows/deploy.yml/badge.svg)

**🌐 Live: [https://mypaste.duckdns.org/ui](https://mypaste.duckdns.org/ui)**

---

## 🏗️ Stack

| Layer | Technology |
|-------|-----------|
| 🐍 Backend | Python / FastAPI |
| 🗄️ Database | SQLite |
| 🌐 Reverse Proxy | nginx |
| 🐳 Container | Docker + Docker Compose |
| ⚙️ CI/CD | GitHub Actions |
| ☁️ Infrastructure | AWS EC2 (t3.micro) + Elastic IP |
| 🌍 DNS | DuckDNS |
| 🔒 TLS | Let's Encrypt (certbot) |
| 📦 Registry | GitHub Container Registry (ghcr.io) |
| 🏗️ IaC | Terraform |

---

## 🏛️ Architecture
internet → DuckDNS → EC2 (Elastic IP)
↓
nginx (TLS :443)
↓
FastAPI (gunicorn)
↓
SQLite (Docker Volume)
---

## 📁 Structure
pastebin/
├── app/
│   ├── main.py          # FastAPI entrypoint
│   ├── models.py        # Pydantic schemas
│   ├── database.py      # SQLite connection
│   └── cleanup.py       # Background expiry task
├── frontend/
│   └── index.html       # Single-page UI
├── nginx/
│   └── default.conf     # Reverse proxy + TLS
├── terraform/
│   ├── main.tf          # EC2 + EIP + SG
│   ├── variables.tf
│   └── outputs.tf
├── .github/workflows/
│   ├── build.yml        # Build + push to ghcr.io
│   └── deploy.yml       # Deploy to EC2
├── Dockerfile
└── docker-compose.yml

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/paste` | Create new paste |
| GET | `/p/{id}` | Get paste by ID |
| GET | `/api/paste/{id}/raw` | Get raw content |
| DELETE | `/api/paste/{id}` | Delete paste |
| GET | `/health` | Health check |

---

## ⚙️ CI/CD Pipeline
git push → GitHub Actions (Build)
↓
docker build
↓
push to ghcr.io
↓
GitHub Actions (Deploy)
↓
SSH to EC2
↓
docker compose pull + up
↓
✅ Live

---

## 🏃 Quick Start (Local)

```bash
git clone https://github.com/Ice1One/pastebin.git
cd pastebin
docker compose up -d
open http://localhost/ui
```

---

**Marko Zvarych** · [github.com/Ice1One](https://github.com/Ice1One) · [mypaste.duckdns.org](https://mypaste.duckdns.org/ui)
