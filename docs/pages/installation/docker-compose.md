# Docker Compose Installation

The recommended way to install IP-HOP is using Docker Compose. This provides the easiest setup and maintenance experience.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+

!!! tip "Check Versions"
    ```bash
    docker --version
    docker compose version
    ```

## Installation Steps

### 1. Download Docker Compose File

```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/Taoshan98/ip-hop/main/docker-compose.yml
```

Or clone the repository:

```bash
git clone https://github.com/Taoshan98/ip-hop.git
cd ip-hop
```

### 2. Create Environment File

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Database
DATABASE_PATH=/app/backend/database/iphop.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001
```

!!! warning "Generate Secure Keys"
    Never use default keys in production! Generate secure values:
    ```bash
    # SECRET_KEY
    openssl rand -hex 32
    
    # ENCRYPTION_KEY
    python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```

### 3. Start Services

```bash
docker compose up -d
```

### 4. Verify Installation

Check container status:

```bash
docker compose ps
```

Expected output:

```
NAME                IMAGE                              STATUS
iphop           ghcr.io/taoshan98/ip-hop:latest   Up 2 minutes
```

Check logs:

```bash
docker compose logs -f
```

### 5. Access Application

Open browser to:

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8001/docs

## Configuration

### Custom Ports

Edit `docker-compose.yml` to change ports:

```yaml
ports:
  - "8080:3000"   # Frontend on port 8080
  - "8081:8001"   # API on port 8081
```

### Persistent Data

Data is stored in `./data` directory by default:

```yaml
volumes:
  - ./data:/app/backend/database
```

### Resource Limits

Add resource limits if needed:

```yaml
services:
  ip-hop:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

## Updating

### Update to Latest Version

```bash
# Pull latest image
docker compose pull

# Restart services
docker compose up -d
```

### Update to Specific Version

Edit `docker-compose.yml`:

```yaml
image: ghcr.io/taoshan98/ip-hop:v1
```

Then:

```bash
docker compose up -d
```

## Troubleshooting

### Container Won't Start

Check logs:

```bash
docker compose logs
```

### Permission Issues

Fix data directory permissions:

```bash
sudo chown -R 1000:1000 ./data
```

### Port Already in Use

Change ports in `docker-compose.yml` or stop conflicting services:

```bash
# Find process using port 3000
sudo lsof -i :3000

# Stop Docker Compose
docker compose down
```

## Next Steps

- [Configure Environment Variables](../configuration/environment.md)
- [Set Up DDNS Providers](../configuration/providers.md)
- [API Documentation](../api/overview.md)
