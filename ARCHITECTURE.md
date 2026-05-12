bashcat > ~/pastebin/ARCHITECTURE.md << 'EOF'
# 🏛️ Architecture

## Overview

Pastebin is a self-hosted service built with a simple but production-ready architecture.
Every component runs in a Docker container on a single AWS EC2 instance.

---

## High-Level Architecture
┌─────────────────────────────────────────────────┐
│                    Internet                      │
└─────────────────────┬───────────────────────────┘
│
▼
┌─────────────────────────────────────────────────┐
│              DuckDNS (DNS)                       │
│         mypaste.duckdns.org → EC2 IP            │
└─────────────────────┬───────────────────────────┘
│
▼
┌─────────────────────────────────────────────────┐
│           AWS EC2 (t3.micro)                     │
│           Elastic IP: 18.184.216.234             │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         nginx (Docker container)          │   │
│  │   :80  → redirect to HTTPS               │   │
│  │   :443 → proxy to FastAPI :8000          │   │
│  └───────────────────┬──────────────────────┘   │
│                      │                           │
│  ┌───────────────────▼──────────────────────┐   │
│  │       FastAPI app (Docker container)      │   │
│  │         uvicorn on :8000                  │   │
│  │         Background cleanup task           │   │
│  └───────────────────┬──────────────────────┘   │
│                      │                           │
│  ┌───────────────────▼──────────────────────┐   │
│  │       SQLite (Docker Volume)              │   │
│  │         /data/pastebin.db                 │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
└─────────────────────────────────────────────────┘

---

## CI/CD Pipeline
Developer
│
│  git push
▼
GitHub
│
│  trigger
▼
GitHub Actions (Build)
│
├── checkout code
├── docker build
└── push to ghcr.io
│
│  trigger on success
▼
GitHub Actions (Deploy)
│
├── SSH to EC2
├── git pull
├── docker pull
└── docker compose up
│
▼
✅ Live Site

---

## Component Details

### nginx
- Listens on ports 80 and 443
- Redirects HTTP to HTTPS
- Terminates TLS using Let's Encrypt certificates
- Proxies all requests to FastAPI container
- Runs as `nginx:alpine` Docker image

### FastAPI Application
- Python 3.12 with FastAPI framework
- Runs with uvicorn ASGI server
- Handles all API requests
- Runs background task every 5 minutes to delete expired pastes
- Connects to SQLite database via aiosqlite

### SQLite Database
- Stored on Docker Volume (`pastebin-data`)
- Persists data across container restarts
- Single table: `pastes`
- Auto-indexed for expiry queries

### Docker Compose
- Orchestrates all containers
- Manages networking between containers
- Handles volume mounting
- Ensures restart on failure

---

## Data Flow

### Creating a Paste
POST /api/paste
↓
nginx receives request
↓
proxy_pass to FastAPI
↓
Pydantic validates request body
↓
generate nanoid (8 chars)
↓
INSERT INTO pastes
↓
return {id, url, expires_at}

### Reading a Paste
GET /p/{id}
↓
nginx receives request
↓
proxy_pass to FastAPI
↓
SELECT FROM pastes WHERE id = ?
AND not expired
↓
UPDATE views = views + 1
↓
return {content, syntax, views}

### Auto-Expiry
every 5 minutes
↓
background task wakes up
↓
DELETE FROM pastes
WHERE expired
↓
log deleted count
↓
sleep 5 minutes

---

## Security

| Layer | Measure |
|-------|---------|
| Network | AWS Security Groups (ports 22, 80, 443 only) |
| TLS | Let's Encrypt SSL certificate |
| Container | Non-root user inside Docker |
| HTTP | Automatic redirect to HTTPS |
| Data | SQLite stored on private Docker volume |

---

## Scalability Considerations

Current setup is optimized for simplicity and cost.
For higher load, consider:

| Bottleneck | Solution |
|------------|---------|
| Single EC2 | Add load balancer + multiple instances |
| SQLite | Migrate to PostgreSQL or MongoDB |
| Single container | Kubernetes orchestration |
| Manual SSL | Automate with certbot cron |

---

## Infrastructure as Code

All AWS resources are managed by Terraform:

```hcl
EC2 Instance (t3.micro)
    + Elastic IP
    + Security Group
    + SSH Key Pair
    + userdata.sh (bootstrap)
```

Recreate entire infrastructure:
```bash
terraform destroy
terraform apply
```
