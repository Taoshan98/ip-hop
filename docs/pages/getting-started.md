# Getting Started

This guide will help you get IP-HOP up and running in just a few minutes.

## Prerequisites

Before you begin, make sure you have:

- [x] Docker and Docker Compose installed
- [x] A supported DDNS provider account
- [x] Basic knowledge of terminal/command line

!!! info "System Requirements"
    - **CPU**: 1 core minimum (ARM64 or x86_64)
    - **RAM**: 512MB minimum, 1GB recommended
    - **Storage**: ~200MB for Docker image
    - **OS**: Any Linux distribution with Docker support

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Taoshan98/ip-hop.git
cd ip-hop
```

### 2. Create Environment File

Create a `.env` file with your configuration:

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred editor:

```bash
nano .env
```

### 3. Generate Secret Keys

Generate secure keys for your installation:

```bash
# For SECRET_KEY
openssl rand -hex 32

# For ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add these to your `.env` file.

### 4. Start the Application

Using Docker Compose (recommended):

```bash
docker compose up -d
```

Or using the pre-built image:

```bash
docker pull ghcr.io/taoshan98/ip-hop:latest
docker run -d \
  -p 3000:3000 \
  -p 8001:8001 \
  -v ./data:/app/backend/database \
  --env-file .env \
  --name ip-hop \
  ghcr.io/taoshan98/ip-hop:latest
```

### 5. Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

!!! success "First Login"
    On first run, you'll be prompted to create an admin account. Make sure to use a strong password!

## Next Steps

Now that IP-HOP is running, you can:

1. **Configure Providers**: Set up your DDNS provider credentials
2. **Add Domains**: Add the domains you want to manage
3. **Enable Auto-Update**: Configure automatic IP update intervals
4. **Customize Settings**: Adjust themes and preferences

## Need Help?

- 📖 **Installation Guides**: Detailed setup for different platforms
- ⚙️ **Configuration**: Environment variables and advanced settings
- 🔍 **Troubleshooting**: Common issues and solutions

[:octicons-arrow-right-24: Installation Guides](installation/docker-compose.md){.md-button}
[:octicons-arrow-right-24: Configuration](configuration/environment.md){.md-button}
