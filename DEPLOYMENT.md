# 🚀 Deployment Guide

Complete step-by-step guide to deploy Pastebin from scratch.

---

## Prerequisites

- AWS account with IAM user
- GitHub account
- Domain on DuckDNS
- Local machine with Ubuntu/Linux

---

## Step 1 — Clone Repository

```bash
git clone https://github.com/Ice1One/pastebin.git
cd pastebin
```

---

## Step 2 — Configure AWS

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: eu-central-1
# Default output format: json

# Verify
aws sts get-caller-identity
```

---

## Step 3 — Generate SSH Key

```bash
ssh-keygen -t ed25519 -f ~/.ssh/pastebin -N ""
```

---

## Step 4 — Deploy Infrastructure with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Note the outputs:
public_ip   = "YOUR_IP"
ssh_command = "ssh -i ~/.ssh/pastebin ubuntu@YOUR_IP"

---

## Step 5 — Configure DuckDNS

1. Go to [duckdns.org](https://www.duckdns.org)
2. Create subdomain (e.g. `mypaste`)
3. Set IP to your EC2 Elastic IP
4. Copy your token

---

## Step 6 — Setup EC2

```bash
# Connect to EC2
ssh -i ~/.ssh/pastebin ubuntu@YOUR_IP

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
newgrp docker

# Setup DuckDNS cron
cat > ~/duckdns-update.sh << 'SCRIPT'
#!/bin/bash
curl -s "https://www.duckdns.org/update?domains=mypaste&token=YOUR_TOKEN&ip="
SCRIPT
chmod +x ~/duckdns-update.sh
crontab -e
# Add: */5 * * * * /home/ubuntu/duckdns-update.sh
```

---

## Step 7 — Get SSL Certificate

```bash
# On EC2
sudo apt install certbot -y
sudo certbot certonly --standalone -d mypaste.duckdns.org
```

---

## Step 8 — Deploy Application

```bash
# On EC2
cd /opt
sudo git clone https://github.com/Ice1One/pastebin.git
sudo chown -R ubuntu:ubuntu /opt/pastebin
cd /opt/pastebin
docker compose up -d
```

---

## Step 9 — Configure GitHub Secrets

Go to: `Settings → Secrets → Actions`

| Secret | Value |
|--------|-------|
| `EC2_SSH_KEY` | `cat ~/.ssh/pastebin` |
| `EC2_HOST` | Your Elastic IP |
| `EC2_USER` | `ubuntu` |

---

## Step 10 — Verify

```bash
# Health check
curl https://mypaste.duckdns.org/health

# Open in browser
https://mypaste.duckdns.org/ui
```

---

## Updating the Application

Simply push to `main` — GitHub Actions handles everything:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Pipeline:
push → build → push image → deploy to EC2 → live

---

## Destroying Infrastructure

```bash
cd terraform
terraform destroy
```

⚠️ This permanently deletes EC2, EIP, and all data.

---

## Troubleshooting

### Site not accessible
```bash
# Check containers
docker compose ps
docker compose logs

# Check nginx
curl http://localhost/health
```

### SSL certificate expired
```bash
docker compose stop nginx
sudo certbot renew
docker compose start nginx
```

### Database issues
```bash
# Check volume
docker volume ls
docker volume inspect pastebin_pastebin-data
```
