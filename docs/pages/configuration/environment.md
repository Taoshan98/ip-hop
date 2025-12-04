# Environment Variables

IP-HOP can be configured using environment variables. This page documents all available options.

## Required Variables

### Security

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Secret key for JWT token signing | `a1b2c3d4...` (64 chars) |
| `ENCRYPTION_KEY` | Fernet key for encrypting sensitive data | `abc123xyz...==` |

!!! danger "Security Critical"
    **Never** commit these keys to version control!
    Generate unique keys for each installation.

Generate secure keys:

```bash
# SECRET_KEY
openssl rand -hex 32

# ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Optional Variables

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `/app/backend/database/iphop.db` | SQLite database file path |

### API Server

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API server bind address |
| `API_PORT` | `8001` | API server port |
| `API_CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8001` | API URL for frontend |
| `PORT` | `3000` | Frontend server port |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | None | Optional log file path |

## Example Configurations

### Development

```env
# .env
SECRET_KEY=dev-secret-key-only-for-local-testing
ENCRYPTION_KEY=dev-encryption-key-only-for-local
DATABASE_PATH=/app/backend/database/iphop_dev.db
API_HOST=127.0.0.1
API_PORT=8001
NEXT_PUBLIC_API_URL=http://localhost:8001
LOG_LEVEL=DEBUG
```

### Production

```env
# .env
SECRET_KEY=<generate-secure-key>
ENCRYPTION_KEY=<generate-secure-key>
DATABASE_PATH=/app/backend/database/iphop.db
API_HOST=0.0.0.0
API_PORT=8001
API_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
LOG_LEVEL=INFO
LOG_FILE=/app/logs/iphop.log
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  ip-hop:
    image: ghcr.io/taoshan98/ip-hop:latest
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - DATABASE_PATH=/data/iphop.db
      - API_HOST=0.0.0.0
      - LOG_LEVEL=INFO
    env_file:
      - .env
```

## Security Best Practices

1. **Generate Unique Keys**: Never reuse keys across installations
2. **Use Environment Files**: Keep secrets in `.env` file (add to `.gitignore`)
3. **Rotate Keys**: Periodically generate new keys
4. **Restrict CORS**: In production, specify exact allowed origins
5. **HTTPS**: Always use HTTPS in production

## Troubleshooting

### Missing SECRET_KEY Error

```
Error: SECRET_KEY environment variable is required
```

**Solution**: Add `SECRET_KEY` to your `.env` file or environment.

### Invalid ENCRYPTION_KEY

```
Error: Invalid ENCRYPTION_KEY format
```

**Solution**: Generate a new key using the command above. The key must be a valid Fernet key.

### Database Permission Error

```
Error: Unable to write to database file
```

**Solution**: Check database directory permissions:

```bash
# For Docker
docker exec ip-hop ls -la /app/backend/database/

# Fix permissions if needed
sudo chown -R 1000:1000 ./data
```

## Next Steps

- [Configure DDNS Providers](providers.md)
- [Network Setup](network.md)
