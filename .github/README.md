bashcat > ~/pastebin/.github/README.md << 'EOF'
# ⚙️ CI/CD — GitHub Actions

## Overview

Two workflows automate the entire build and deployment process.
Every push to `main` triggers a build and deploy automatically.

---

## Workflows
git push to main
↓
build.yml (Build & Push)
↓
deploy.yml (Deploy to EC2)
↓
✅ Live at https://mypaste.duckdns.org

---

## File Structure
.github/
└── workflows/
├── build.yml    # Build Docker image + push to ghcr.io
└── deploy.yml   # SSH to EC2 + pull + restart

---

## build.yml

**Triggers:** push to `main`, `dev`, pull requests to `main`

**Steps:**
1. Checkout code
2. Set up Docker Buildx
3. Login to GitHub Container Registry
4. Build Docker image
5. Push to `ghcr.io/ice1one/pastebin`

**Image tags:**
| Branch | Tag |
|--------|-----|
| `main` | `latest` + `sha-<commit>` |
| `dev` | `dev-<run_number>` |
| PR | `pr-<pr_number>` |

---

## deploy.yml

**Triggers:** after successful `Build` workflow on `main`

**Steps:**
1. SSH into EC2
2. `git pull origin main`
3. Login to ghcr.io
4. `docker compose pull app`
5. `docker compose up -d --no-deps app`
6. `docker image prune -f`

---

## Required Secrets

Go to: `Settings → Secrets → Actions → New repository secret`

| Secret | Value | Description |
|--------|-------|-------------|
| `EC2_SSH_KEY` | Private SSH key content | For SSH access to EC2 |
| `EC2_HOST` | `18.184.216.234` | EC2 Elastic IP |
| `EC2_USER` | `ubuntu` | EC2 username |

---

## Required Permissions

Go to: `Settings → Actions → General → Workflow permissions`

- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

---

## Monitoring Pipelines

View all runs:
https://github.com/Ice1One/pastebin/actions

### Pipeline Status Badges

```markdown
![Build](https://github.com/Ice1One/pastebin/actions/workflows/build.yml/badge.svg)
![Deploy](https://github.com/Ice1One/pastebin/actions/workflows/deploy.yml/badge.svg)
```

---

## Troubleshooting

### Build fails — permission denied to ghcr.io
Settings → Actions → General → Workflow permissions
→ Read and write permissions ✅

### Deploy fails — SSH authentication
Check EC2_SSH_KEY secret contains full private key
including -----BEGIN and -----END lines

### Deploy fails — port already in use
```bash
# On EC2
docker rm -f $(docker ps -aq)
docker compose up -d
```

---

## Adding a New Workflow

1. Create file in `.github/workflows/`
2. Define trigger with `on:`
3. Define jobs and steps
4. Push to GitHub

Example:
```yaml
name: Test

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: echo "Running tests..."
```
