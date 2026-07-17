# 📋 Pastebin — Self-Hosted

> A self-hosted, ephemeral pastebin with auto-expiring pastes, deployed via GitHub Actions.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-29.1-2496ED?style=flat&logo=docker&logoColor=white)
![nginx](https://img.shields.io/badge/nginx-1.29-009639?style=flat&logo=nginx&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-1.15-7B42BC?style=flat&logo=terraform&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.45-003B57?style=flat&logo=sqlite&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=flat&logo=githubactions&logoColor=white)
![Build](https://github.com/Ice1One/pastebin/actions/workflows/build.yml/badge.svg)
![Deploy](https://github.com/Ice1One/pastebin/actions/workflows/deploy.yml/badge.svg)

[![Live](https://img.shields.io/badge/🟢_Live-pastebin--73vo.onrender.com-00C853?style=for-the-badge)](https://pastebin-73vo.onrender.com/ui)

---
## 🎬 Demo
![Demo](demo-pastebin%20(1).gif)
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
| ☸️ Orchestration | Kubernetes (minikube) |
| 📊 Monitoring | Prometheus + Grafana |
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
## ☸️ Kubernetes
Local Kubernetes cluster via minikube with 2 replicas for high availability.
```bash
# Deploy
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
# Scale
kubectl scale deployment pastebin-app --replicas=3
# Status
kubectl get pods
kubectl get services
```
**Self-healing demo:**
```bash
# Delete a pod — Kubernetes automatically creates a new one
kubectl delete pod <pod-name>
kubectl get pods  # new pod appears in seconds
```
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
**Marko Zvarych** · [github.com/Ice1One](https://github.com/Ice1One) · https://pastebin-73vo.onrender.com/ui
