# IP-HOP 🌐

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/Taoshan98/ip-hop)
[![Backend Coverage](https://img.shields.io/badge/backend%20coverage-100%25-brightgreen)](./backend)
[![Frontend Coverage](https://img.shields.io/badge/frontend%20coverage-45%25-yellow)](./frontend)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**IP-HOP** is a modern, self-hosted Dynamic DNS (DDNS) management system with multi-provider support, automatic IP monitoring, and a beautiful web dashboard.

## ✨ Features

- 🔄 **Automatic IP Updates**: Monitors your public IP and updates DNS records automatically
- 🌍 **Multi-Provider Support**: Cloudflare, Dynu, DuckDNS, and extensible for more
- ⏰ **Flexible Scheduling**: Cron-based scheduling for each domain
- 🔐 **Secure**: Encrypted credentials, JWT authentication, HttpOnly cookies
- 📊 **History Tracking**: Complete audit trail of all IP changes
- 🎨 **Modern UI**: Beautiful Next.js dashboard with real-time updates
- 🐳 **Docker Ready**: One-command deployment with Docker Compose
- ✅ **Fully Tested**: 73 backend + 56 frontend tests with 100% pass rate

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites
- Docker & Docker Compose
- Domain(s) to manage
- API credentials from your DNS provider

### 1. Clone the Repository
```bash
git clone https://github.com/Taoshan98/ip-hop.git
cd ip-hop
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

**Required variables:**
```env
SECRET_KEY=your-random-secret-key-here
ENCRYPTION_KEY=your-32-byte-base64-encryption-key
```

Generate keys:
```bash
# SECRET_KEY
openssl rand -hex 32

# ENCRYPTION_KEY (must be 32 bytes)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Start the Application
```bash
docker-compose up -d
```

### 4. Access the Dashboard
Open [http://localhost:3000](http://localhost:3000)

**First-time setup:**
1. Navigate to `/setup` 
2. Create admin account
3. Add DNS providers
4. Configure domains
5. Set update schedules

## 📦 Architecture

```
ip-hop/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   │   ├── api/     # REST API endpoints
│   │   ├── core/    # Security, config
│   │   ├── models/  # SQLAlchemy models
│   │   ├── providers/ # DNS provider implementations
│   │   └── services/  # Business logic
│   ├── database/    # SQLite database
│   └── tests/       # 73 comprehensive tests
│
├── frontend/        # Next.js frontend
│   ├── src/
│   │   ├── app/     # Next.js 14 app router
│   │   ├── components/ # React components
│   │   ├── context/ # Auth context
│   │   └── lib/     # Utilities, API client
│   └── __tests__/   # 56 comprehensive tests
│
└── docker-compose.yml  # Deployment config
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with HttpOnly cookies
- **Security**: Fernet encryption for credentials
- **Scheduling**: APScheduler with Cron expressions
- **HTTP Client**: httpx (async)
- **Testing**: pytest (73 tests, 100% pass rate)

### Frontend
- **Framework**: Next.js 14 (React 19)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: Radix UI primitives
- **State**: React Query for server state
- **HTTP Client**: Axios
- **Testing**: Jest + React Testing Library (56 tests)

### DevOps
- **Containerization**: Docker (multi-stage builds)
- **CI/CD**: GitHub Actions
- **Security Scanning**: Trivy
- **Image Registry**: GitHub Container Registry (GHCR)

## 📖 Documentation

- **[Backend Documentation](./backend/README.md)** - API endpoints, models, providers
- **[Frontend Documentation](./frontend/README.md)** - Components, pages, architecture
- **[Release Management](./RELEASE.md)** - Versioning and release process

## 🔌 Supported DNS Providers

| Provider | Status | Features |
|----------|--------|----------|
| **Cloudflare** | ✅ | API, Zone ID, proxied/DNS-only |
| **Dynu** | ✅ | API, domain management |
| **DuckDNS** | ✅ | Free, simple token-based auth |
| **Custom** | 🔧 | Extensible provider system |

### Adding New Providers
See [Backend Documentation](./backend/README.md#adding-providers) for implementation guide.

## 🛡️ Security Features

- **Encrypted Storage**: Credentials encrypted at rest with Fernet
- **JWT Authentication**: Secure token-based auth
- **HttpOnly Cookies**: XSS protection
- **Non-root Docker**: Runs as user `iphop:1000`
- **Security Scanning**: Automated Trivy scans in CI/CD
- **No Hardcoded Secrets**: Environment-based configuration

## 📊 API Overview

### Authentication
- `POST /api/v1/auth/setup` - Initial admin setup
- `POST /api/v1/auth/token` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Current user

### Providers
- `GET /api/v1/providers` - List providers
- `POST /api/v1/providers` - Add provider
- `PUT /api/v1/providers/{id}` - Update provider
- `DELETE /api/v1/providers/{id}` - Remove provider

### Domains
- `GET /api/v1/domains` - List domains
- `POST /api/v1/domains` - Add domain
- `PUT /api/v1/domains/{id}` - Update domain
- `POST /api/v1/domains/{id}/update_ip` - Force update
- `GET /api/v1/domains/{id}/history` - Update history

**Full API docs:** [Backend README](./backend/README.md)

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python -m pytest tests/ -v
# 73 tests, 100% pass rate
```

### Run Frontend Tests
```bash
cd frontend
npm test
# 56 tests, 100% pass rate
```

### Coverage Reports
```bash
# Backend
cd backend && pytest --cov=app tests/

# Frontend  
cd frontend && npm test -- --coverage
```

## 🚢 Deployment Options

### Option 1: Docker Compose (Recommended)

1. **Set environment variables:**
```bash
SECRET_KEY="your-secret-key-here" #openssl rand -hex 32
ENCRYPTION_KEY="your-encryption-key-here" #python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

2. **Start the application:**
```bash
docker-compose up -d
```

**Permissions:**
You may be asked to change ownership of the newly created directory if you are running docker as root and creating folders via docker compose
```bash
sudo chown -R $USER:$USER ip-hop/
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Option 2: Docker Run

```bash
docker pull ghcr.io/taoshan98/ip-hop:latest

docker run -d \
  --name iphop \
  -p 8001:8001 \
  -p 3000:3000 \
  -e SECRET_KEY="your-secret-key" \
  -e ENCRYPTION_KEY="your-encryption-key" \
  -v iphop-data:/app/backend/database \
  ghcr.io/taoshan98/ip-hop:latest
```

### Option 2: Manual Installation

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Frontend
cd frontend
npm install
npm run build
npm start
```

## 🐳 Docker Details

### Image Information
- **Base Image:** Alpine Linux (minimal size)
- **Size:** ~200MB (optimized multi-stage build)
- **Platforms:** linux/amd64, linux/arm64
- **User:** Non-root (iphop:1000)
- **Health Check:** Built-in monitoring

### Volumes
- `/app/backend/database` - Persistent database storage

### Ports
- `8001` - Backend API (FastAPI/Uvicorn)
- `3000` - Frontend (Next.js)

### Security Features
- ✅ Non-root user execution
- ✅ Minimal Alpine base image
- ✅ Multi-stage build (smaller attack surface)
- ✅ Security scanning with Trivy
- ✅ No hardcoded secrets
- ✅ Health checks enabled

### CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On Pull Request:**
   - Runs backend tests (pytest)
   - Builds frontend
   - Validates Docker build

2. **On Main Branch Push:**
   - Runs all tests
   - Builds multi-architecture images (amd64, arm64)
   - Pushes to GitHub Container Registry
   - Scans for vulnerabilities (Trivy)
   - Creates semantic version tags (1.0.0, 1.0, 1, latest)

### Docker Management

**View logs:**
```bash
docker compose logs -f
```

**Stop the application:**
```bash
docker-compose down
# or
docker stop iphop
```

### Troubleshooting

**Container won't start:**
```bash
docker compose logs iphop
```

**Health check failing:**
```bash
docker inspect iphop-app | grep Health -A 10
```

**Database issues:**
```bash
docker exec -it iphop-app ls -la /app/backend/database
```

### Production Recommendations

1. Use volume for database persistence
2. Set strong SECRET_KEY and ENCRYPTION_KEY
3. Use reverse proxy (nginx/traefik) for SSL
4. Enable Docker resource limits
5. Monitor container health
6. Regular backups of database volume

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT signing key | ✅ | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiration time in minutes | ❌ | `10080` (7 days) |
| `ENCRYPTION_KEY` | Fernet encryption key | ✅ | - |
| `DATABASE_PATH` | SQLite database path | ❌ | `backend/database/ip_hop.db` |
| `CORS_ORIGINS` | Allowed CORS origins | ❌ | `["http://localhost:3000"]` |

### Cron Schedule Examples
```
*/5 * * * *   # Every 5 minutes
0 */1 * * *   # Every hour
0 0 * * *     # Daily at midnight
0 */6 * * *   # Every 6 hours
```

## 📈 Version Management

IP-HOP follows [Semantic Versioning](https://semver.org/):
- **v1.0.0** - Initial stable release
- See [CHANGELOG.md](./CHANGELOG.md) for version history
- See [RELEASE.md](./RELEASE.md) for release process

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- **FastAPI** for the excellent backend framework
- **Next.js** for the modern React framework
- **Cloudflare** and **Dynu** for DNS services
- All open-source contributors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Taoshan98/ip-hop/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Taoshan98/ip-hop/discussions)

---

**Made with ❤️ for easier DDNS management**
