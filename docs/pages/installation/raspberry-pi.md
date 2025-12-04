# Raspberry Pi Installation

IP-HOP has first-class support for Raspberry Pi and ARM64 devices!

## Supported Devices

- ✅ Raspberry Pi 4 (4GB+ recommended)
- ✅ Raspberry Pi 5
- ✅ Raspberry Pi 400
- ⚠️ Raspberry Pi 3 (ARM64 mode, 1GB model not recommended)

## Prerequisites

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes.

### 2. Install Docker Compose

```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

Verify:

```bash
docker compose version
```

## Installation

### Method 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/Taoshan98/ip-hop.git
cd ip-hop

# Create environment file
cp .env.example .env

# Generate keys
nano .env  # Add your secret keys

# Start services
docker compose up -d
```

### Method 2: Standalone Docker

```bash
# Pull ARM64 image
docker pull ghcr.io/taoshan98/ip-hop:latest

# Create data directory
mkdir -p ~/ip-hop/data

# Run container
docker run -d \
  --name ip-hop \
  --restart unless-stopped \
  -p 3000:3000 \
  -p 8001:8001 \
  -v ~/ip-hop/data:/app/backend/database \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
  ghcr.io/taoshan98/ip-hop:latest
```

## Pi-Specific Optimizations

### Memory Management

For Pi models with limited RAM:

```yaml
# docker-compose.yml
services:
  ip-hop:
    # ... other config ...
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Performance Tips

1. **Use Fast Storage**: Use a USB 3.0 SSD for best performance
2. **Enable Swap**: Ensure swap is enabled for stability
3. **Network**: Use wired ethernet when possible

### Enable Swap (if needed)

```bash
# Check current swap
free -h

# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Accessing from Network

### Find Pi IP Address

```bash
hostname -I
```

### Access from Other Devices

Replace `localhost` with your Pi's IP:

```
http://192.168.1.100:3000
```

### Setup Static IP (Recommended)

Edit `/etc/dhcpcd.conf`:

```bash
sudo nano /etc/dhcpcd.conf
```

Add:

```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Restart networking:

```bash
sudo systemctl restart dhcpcd
```

## Auto-Start on Boot

Docker containers with `--restart unless-stopped` will auto-start on boot.

Verify:

```bash
# Reboot Pi
sudo reboot

# After reboot, check container
docker ps
```

## Monitoring

### View Resource Usage

```bash
# Container stats
docker stats ip-hop

# System resources
htop
```

### Check Logs

```bash
docker logs -f ip-hop
```

## Troubleshooting

### Out of Memory

Reduce memory usage:

```yaml
deploy:
  resources:
    limits:
      memory: 384M
```

### Slow Performance

1. Check SD card speed: Use Class 10 or better
2. Use external storage for database
3. Reduce update frequency in settings

### Network Issues

```bash
# Check firewall
sudo ufw status

# Allow ports if needed
sudo ufw allow 3000
sudo ufw allow 8001
```

## Next Steps

- [Configure Environment Variables](../configuration/environment.md)
- [Set Up DDNS Providers](../configuration/providers.md)
- [Network Setup for Remote Access](../configuration/network.md)
