# 🌐 nginx — Reverse Proxy & TLS

## Overview

nginx acts as a reverse proxy in front of the FastAPI application.
It handles HTTPS termination and forwards requests to the backend.

---

## Architecture
Internet
↓
nginx :80  → redirect to HTTPS
nginx :443 → proxy to FastAPI :8000
↓
FastAPI (app container)

---

## File Structure
nginx/
└── default.conf    # Main nginx configuration
---

## Configuration Explained

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name mypaste.duckdns.org;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl;
    server_name mypaste.duckdns.org;

    # SSL certificates from Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/mypaste.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mypaste.duckdns.org/privkey.pem;

    # Forward all requests to FastAPI
    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## SSL Certificate

### Initial Setup

```bash
# Stop nginx to free port 80
docker compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d mypaste.duckdns.org

# Start nginx back
docker compose start nginx
```

### Certificate Location
/etc/letsencrypt/live/mypaste.duckdns.org/
├── fullchain.pem   ← SSL certificate
└── privkey.pem     ← Private key

### Auto-renewal

Certbot automatically sets up a cron job for renewal.
Verify with:
```bash
sudo certbot renew --dry-run
```

### Manual renewal
```bash
docker compose stop nginx
sudo certbot renew
docker compose start nginx
```

---

## Headers Explained

| Header | Purpose |
|--------|---------|
| `Host` | Original host from client request |
| `X-Real-IP` | Client's real IP address |
| `X-Forwarded-For` | Chain of IP addresses |
| `X-Forwarded-Proto` | Original protocol (http/https) |

---

## Testing

```bash
# Check HTTP redirect
curl -I http://mypaste.duckdns.org

# Check HTTPS
curl -I https://mypaste.duckdns.org/health

# Check SSL certificate
openssl s_client -connect mypaste.duckdns.org:443 -servername mypaste.duckdns.org
```
