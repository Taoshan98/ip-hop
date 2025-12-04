# Troubleshooting

Common issues and solutions.

## Installation Issues

### Docker Image Won't Pull

**Error**: `manifest unknown` or `unauthorized`

**Solution**:
```bash
# Verify image name
docker pull ghcr.io/taoshan98/ip-hop:latest

# Login if private
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Container Exits Immediately

**Check logs**:
```bash
docker logs ip-hop
```

Common causes:
- Missing environment variables
- Database permission issues
- Port conflicts

## Runtime Issues

### Cannot Access Frontend

1. **Check container is running**:
   ```bash
   docker ps | grep ip-hop
   ```

2. **Verify ports**:
   ```bash
   docker port ip-hop
   ```

3. **Check firewall**:
   ```bash
   sudo ufw status
   ```

### API Returns 500 Error

1. **Check backend logs**:
   ```bash
   docker logs ip-hop 2>&1 | grep ERROR
   ```

2. **Verify environment variables**:
   ```bash
   docker exec ip-hop env | grep SECRET_KEY
   ```

### Database Locked

**Error**: `database is locked`

**Solution**:
```bash
# Stop container
docker stop ip-hop

# Check for multiple instances
docker ps -a | grep ip-hop

# Remove old instances
docker rm old-container-id

# Start fresh
docker start ip-hop
```

## Provider Issues

### Updates Failing

1. **Test API credentials** in provider dashboard
2. **Check IP-HOP logs** for specific errors
3. **Verify provider API status** (check provider status page)

### IP Not Updating

1. **Check update interval settings**
2. **Force manual update** via UI
3. **Verify current IP detection**:
   ```bash
   curl http://localhost:8001/api/v1/system/status
   ```

## Performance Issues

### High Memory Usage

**Solution**: Limit container resources:

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
```

### Slow Response

1. **Check container stats**:
   ```bash
   docker stats ip-hop
   ```

2. **Verify database size**:
   ```bash
   docker exec ip-hop ls -lh /app/backend/database/
   ```

3. **Restart container**:
   ```bash
   docker restart ip-hop
   ```

## Network Issues

### Cannot Access Remotely

1. **Verify local access works first**
2. **Check router port forwarding**
3. **Verify firewall rules**
4. **Test with**: `telnet your-ip 3000`

### CORS Errors

Update API CORS settings:

```env
API_CORS_ORIGINS=https://yourdomain.com
```

## Still Having Issues?

1. **Enable debug logging**:
   ```env
   LOG_LEVEL=DEBUG
   ```

2. **Collect logs**:
   ```bash
   docker logs ip-hop > iphop-logs.txt
   ```

3. **Open GitHub Issue** with:
   - IP-HOP version
   - Platform (Docker, Pi, etc.)
   - Error messages
   - Steps to reproduce

[:fontawesome-brands-github: Report Issue](https://github.com/Taoshan98/ip-hop/issues){.md-button}
