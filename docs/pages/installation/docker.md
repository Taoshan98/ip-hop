# Standalone Docker Installation

Install IP-HOP using a single Docker container without Docker Compose.

## Quick Start

```bash
docker run -d \
  --name ip-hop \
  -p 3000:3000 \
  -p 8001:8001 \
  -v $(pwd)/data:/app/backend/database \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
  ghcr.io/taoshan98/ip-hop:latest
```

## Detailed Setup

### 1. Pull Image

```bash
docker pull ghcr.io/taoshan98/ip-hop:latest
```

### 2. Create Data Directory

```bash
mkdir -p ./data
chmod 755 ./data
```

### 3. Generate Keys

```bash
export SECRET_KEY=$(openssl rand -hex 32)
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### 4. Run Container

```bash
docker run -d \
  --name ip-hop \
  --restart unless-stopped \
  -p 3000:3000 \
  -p 8001:8001 \
  -v $(pwd)/data:/app/backend/database \
  -e SECRET_KEY="${SECRET_KEY}" \
  -e ENCRYPTION_KEY="${ENCRYPTION_KEY}" \
  -e DATABASE_PATH="/app/backend/database/iphop.db" \
  -e API_HOST="0.0.0.0" \
  -e API_PORT="8001" \
  -e NEXT_PUBLIC_API_URL="http://localhost:8001" \
  ghcr.io/taoshan98/ip-hop:latest
```

## Management

### View Logs

```bash
docker logs -f ip-hop
```

### Stop Container

```bash
docker stop ip-hop
```

### Start Container

```bash
docker start ip-hop
```

### Remove Container

```bash
docker stop ip-hop
docker rm ip-hop
```

### Update

```bash
# Pull latest image
docker pull ghcr.io/taoshan98/ip-hop:latest

# Stop and remove old container
docker stop ip-hop
docker rm ip-hop

# Start new container (using same command as before)
docker run -d ...
```

## Advanced Configuration

### Using Environment File

Create `.env` file:

```env
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
DATABASE_PATH=/app/backend/database/iphop.db
API_HOST=0.0.0.0
API_PORT=8001
NEXT_PUBLIC_API_URL=http://localhost:8001
```

Run with env file:

```bash
docker run -d \
  --name ip-hop \
  -p 3000:3000 \
  -p 8001:8001 \
  -v $(pwd)/data:/app/backend/database \
  --env-file .env \
  ghcr.io/taoshan98/ip-hop:latest
```

### Custom Network

```bash
# Create network
docker network create ip-hop-net

# Run container on network
docker run -d \
  --name ip-hop \
  --network ip-hop-net \
  -p 3000:3000 \
  -p 8001:8001 \
  # ... other options ...
  ghcr.io/taoshan98/ip-hop:latest
```

### Health Check

```bash
# Check health
docker inspect --format='{{json .State.Health}}' ip-hop | jq

# Container should be healthy after ~40 seconds
```

## Next Steps

- [Configure Environment Variables](../configuration/environment.md)
- [Set Up DDNS Providers](../configuration/providers.md)
