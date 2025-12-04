# Network Setup

Configure networking for local and remote access to IP-HOP.

## Local Network Access

### Basic Setup

IP-HOP runs on:
- Frontend: Port `3000`
- API: Port `8001`

Access from local network:
```
http://<server-ip>:3000
```

### Find Server IP

```bash
# Linux/Mac
hostname -I

# Or using ip command
ip addr show
```

## Remote Access

### Option 1: Reverse Proxy (Recommended)

Use Nginx or Caddy as reverse proxy with SSL.

#### Nginx Example

```nginx
server {
    listen 80;
    server_name iphop.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name iphop.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Caddy Example

```caddyfile
iphop.yourdomain.com {
    reverse_proxy localhost:3000
    reverse_proxy /api/* localhost:8001
}
```

Auto HTTPS with Let's Encrypt!

### Option 2: Cloudflare Tunnel

Zero-config secure access using Cloudflare Tunnel.

1. Install cloudflared
2. Authenticate
3. Create tunnel:

```bash
cloudflared tunnel create iphop
cloudflared tunnel route dns iphop iphop.yourdomain.com
```

4. Configure tunnel:

```yaml
# config.yml
tunnel: <tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: iphop.yourdomain.com
    service: http://localhost:3000
  - service: http_status:404
```

5. Run tunnel:

```bash
cloudflared tunnel run iphop
```

### Option 3: Tailscale

Private VPN access using Tailscale.

1. Install Tailscale on server
2. Start Tailscale
3. Access from any device on Tailscale network

## Port Forwarding

For direct access without proxy:

1. **Router Configuration**:
   - Forward external port (e.g., 8443) to internal port 3000
   - Forward external port (e.g., 8444) to internal port 8001

2. **Security Considerations**:
   - Use non-standard ports
   - Enable firewall rules
   - Consider using VPN instead

!!! warning "Security"
    Direct port forwarding exposes services to the internet.
    Use reverse proxy with HTTPS instead!

## Firewall Configuration

### UFW (Ubuntu/Debian)

```bash
# Allow local network only
sudo ufw allow from 192.168.1.0/24 to any port 3000
sudo ufw allow from 192.168.1.0/24 to any port 8001

# Or allow from anywhere (if using reverse proxy)
sudo ufw allow 80
sudo ufw allow 443
```

### firewalld (RHEL/CentOS)

```bash
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --reload
```

## Docker Networking

### Custom Network

Create isolated network:

```yaml
# docker-compose.yml
networks:
  iphop-net:
    driver: bridge

services:
  ip-hop:
    networks:
      - iphop-net
```

### Host Network

For better performance (Linux only):

```yaml
services:
  ip-hop:
    network_mode: host
```

## HTTPS Setup

### Let's Encrypt with Nginx

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d iphop.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Self-Signed Certificate

For local testing only:

```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=iphop.local"
```

## Troubleshooting

### Cannot Access from Other Devices

1. Check firewall: `sudo ufw status`
2. Verify container is running: `docker ps`
3. Test port connectivity: `telnet <server-ip> 3000`

### Reverse Proxy Not Working

1. Check proxy configuration
2. Verify upstream services are accessible
3. Check proxy logs

### CORS Errors

Update API CORS settings:

```env
API_CORS_ORIGINS=https://iphop.yourdomain.com,https://www.iphop.yourdomain.com
```

## Next Steps

- [API Documentation](../api/overview.md)
- [Troubleshooting](../troubleshooting.md)
