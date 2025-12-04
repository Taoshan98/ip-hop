# Backend Documentation

FastAPI-based REST API for IP-HOP Dynamic DNS management system.

## 📋 Table of Contents

- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Provider System](#provider-system)
- [Authentication](#authentication)
- [Testing](#testing)
- [Development](#development)

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/v1/           # API routes
│   │   └── endpoints/    # Endpoint implementations
│   ├── core/            # Core functionality
│   │   ├── config.py    # Configuration
│   │   ├── security.py  # Auth & encryption
│   │   └── scheduler.py # IP update scheduler
│   ├── db/              # Database
│   │   └── base.py      # SQLAlchemy setup
│   ├── models/          # SQLAlchemy models
│   ├── providers/       # DNS provider implementations
│   │   ├── base.py      # Abstract base
│   │   ├── cloudflare.py
│   │   └── dynu.py
│   ├── services/        # Business logic
│   │   └── ip_service.py
│   └── main.py          # FastAPI application
├── database/            # SQLite database storage
├── scripts/             # Utility scripts
└── tests/               # 73 comprehensive tests
```

## 🔌 API Endpoints

### Base URL
```
http://localhost:8001/api/v1
```

### Authentication Endpoints

#### POST `/auth/setup`
**Initial admin account creation** (only works once)

**Request:**
```json
{
  "username": "admin",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "username": "admin",
  "message": "Admin user created successfully"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

---

#### POST `/auth/token`
**Login and obtain JWT token**

**Request** (form data):
```
username=admin
password=SecurePass123!
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Notes:**
- Sets HttpOnly cookie with JWT
- Cookie name: `access_token`
- Secure, SameSite=Lax

---

#### POST `/auth/logout`
**Logout and clear session**

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

#### GET `/auth/me`
**Get current authenticated user**

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "admin"
}
```

---

### Provider Endpoints

#### GET `/providers`
**List all DNS providers**

**Response:**
```json
[
  {
    "id": 1,
    "name": "Cloudflare",
    "type": "cloudflare",
    "is_enabled": true,
    "config": {
      "zone_id": "abc123..."
    },
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

---

#### POST `/providers`
**Add new DNS provider**

**Request (Cloudflare):**
```json
{
  "name": "My Cloudflare",
  "type": "cloudflare",
  "credentials": {
    "api_token": "your-cloudflare-api-token"
  },
  "config": {
    "zone_id": "your-zone-id"
  }
}
```

**Request (Dynu):**
```json
{
  "name": "My Dynu",
  "type": "dynu",
  "credentials": {
    "api_key": "your-dynu-api-key"
  }
}
```

**Request (DuckDNS):**
```json
{
  "name": "My DuckDNS",
  "type": "duckdns",
  "credentials": {
    "token": "your-duckdns-token"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Cloudflare",
  "type": "cloudflare",
  "is_enabled": true,
  "config": {...},
  "created_at": "2024-01-01T00:00:00"
}
```

---

#### PUT `/providers/{provider_id}`
**Update existing provider**

**Request:**
```json
{
  "name": "Updated Name",
  "is_enabled": false,
  "credentials": {
    "api_token": "new-token"
  }
}
```

---

#### DELETE `/providers/{provider_id}`
**Delete provider and all associated domains**

**Response:**
```json
{
  "message": "Provider deleted successfully"
}
```

---

### Domain Endpoints

#### GET `/domains`
**List all domains**

**Response:**
```json
[
  {
    "id": 1,
    "provider_id": 1,
    "domain_name": "example.com",
    "external_id": "cloudflare-record-id",
    "last_known_ip": "1.2.3.4",
    "last_update": "2024-01-01T12:00:00",
    "cron_schedule": "*/5 * * * *",
    "is_enabled": true,
    "config": {
      "proxied": false,
      "ttl": 1
    },
    "provider": {
      "name": "Cloudflare",
      "type": "cloudflare"
    }
  }
]
```

---

#### POST `/domains`
**Add new domain**

**Request:**
```json
{
  "provider_id": 1,
  "domain_name": "subdomain.example.com",
  "cron_schedule": "*/10 * * * *",
  "config": {
    "proxied": false,
    "ttl": 1
  }
}
```

**Cron Schedule Examples:**
- `*/5 * * * *` - Every 5 minutes
- `0 */1 * * *` - Every hour
- `0 0 * * *` - Daily at midnight
- `0 */6 * * *` - Every 6 hours

**Response:**
```json
{
  "id": 1,
  "domain_name": "subdomain.example.com",
  "last_known_ip": "1.2.3.4",
  "cron_schedule": "*/10 * * * *",
  "is_enabled": true
}
```

---

#### PUT `/domains/{domain_id}`
**Update domain configuration**

**Request:**
```json
{
  "cron_schedule": "*/15 * * * *",
  "is_enabled": false,
  "config": {
    "proxied": true
  }
}
```

---

#### DELETE `/domains/{domain_id}`
**Delete domain**

**Response:**
```json
{
  "message": "Domain deleted successfully"
}
```

---

#### POST `/domains/{domain_id}/update_ip`
**Force immediate IP update**

**Response:**
```json
{
  "success": true,
  "old_ip": "1.2.3.4",
  "new_ip": "5.6.7.8",
  "message": "IP updated successfully"
}
```

---

#### GET `/domains/{domain_id}/history`
**Get domain update history**

**Query Parameters:**
- `days` (optional): Number of days to retrieve (default: 30)

**Response:**
```json
[
  {
    "id": 1,
    "domain_id": 1,
    "old_ip": "1.2.3.4",
    "new_ip": "5.6.7.8",
    "update_time": "2024-01-01T12:00:00",
    "success": true
  }
]
```

---

#### DELETE `/domains/{domain_id}/history`
**Clear domain history**

**Response:**
```json
{
  "message": "History cleared successfully",
  "deleted_count": 42
}
```

---

### System Endpoints

#### GET `/system/status`
**Check if system is initialized**

**Response:**
```json
{
  "initialized": true,
  "version": "1.0.0"
}
```

---

## 🗄️ Database Models

### User
```python
class User(Base):
    id: int
    username: str (unique, max 100)
    password_hash: str
    created_at: datetime
```

### Provider
```python
class Provider(Base):
    id: int
    name: str (max 100)
    type: str (cloudflare, dynu, etc.)
    credentials_encrypted: str  # Fernet encrypted JSON
    config: JSON  # Provider-specific config
    is_enabled: bool (default: True)
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    domains: List[Domain]
```

### Domain
```python
class Domain(Base):
    id: int
    provider_id: int (foreign key)
    domain_name: str (max 255)
    external_id: str  # Provider's record ID
    last_known_ip: str (max 45, nullable)
    last_update_status: datetime (nullable)
    cron_schedule: str  # Cron expression
    is_enabled: bool (default: True)
    config: JSON  # Domain-specific config
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    provider: Provider
    history: List[UpdateHistory]
```

### UpdateHistory
```python
class UpdateHistory(Base):
    id: int
    domain_id: int (foreign key)
    old_ip: str (max 45, nullable)
    new_ip: str (max 45)
    update_time: datetime
    success: bool
    error_message: str (nullable)
    
    # Relationships
    domain: Domain
```

---

## 🔌 Provider System

### Architecture

All providers implement the `DNSProvider` abstract base class:

```python
class DNSProvider(ABC):
    @abstractmethod
    async def create_record(self, domain: str, ip: str, config: dict) -> str:
        """Create DNS record, return external_id"""
        pass
    
    @abstractmethod
    async def update_record(self, external_id: str, ip: str, config: dict) -> bool:
        """Update existing record"""
        pass
    
    @abstractmethod
    async def delete_record(self, external_id: str) -> bool:
        """Delete DNS record"""
        pass
    
    @abstractmethod
    async def get_last_known_ip(self, external_id: str) -> str:
        """Get current IP from provider"""
        pass
```

### Supported Providers

#### Cloudflare

**Credentials:**
```json
{
  "api_token": "your-api-token"
}
```

**Config:**
```json
{
  "zone_id": "your-zone-id",
  "proxied": false,  // Optional, default: false
  "ttl": 1          // Optional, 1 = auto
}
```

**Features:**
- Automatic record creation
- Proxied/DNS-only modes
- Custom TTL support
- Zone management

---

#### Dynu

**Credentials:**
```json
{
  "api_key": "your-api-key"
}
```

**Config:**
```json
{
  "ttl": 300  // Optional
}
```

**Features:**
- Domain-level management
- IPv4 support
- TTL configuration

---

#### DuckDNS

**Credentials:**
```json
{
  "token": "your-duckdns-token"
}
```

**Config:**
No additional config needed!

**Features:**
- Simple token-based authentication
- Automatic subdomain handling
- Free service with no limits
- Perfect for home lab
- Accepts both `subdomain` and `subdomain.duckdns.org`

---

### Adding a New Provider

1. **Create provider class** in `app/providers/your_provider.py`:

```python
from app.providers.base import DNSProvider

class YourProvider(DNSProvider):
    def __init__(self, credentials: dict):
        self.api_key = credentials['api_key']
    
    async def create_record(self, domain: str, ip: str, config: dict) -> str:
        # Implementation
        return "external_record_id"
    
    async def update_record(self, external_id: str, ip: str, config: dict) -> bool:
        # Implementation
        return True
    
    # ... implement other methods
```

2. **Register in factory** (`app/providers/base.py`):

```python
PROVIDERS = {
    'cloudflare': CloudflareProvider,
    'dynu': DynuProvider,
    'duckdns': DuckDNSProvider,
    'your_provider': YourProvider,  # Add here
}
```

3. **Add tests** in `tests/test_providers.py`

---

## 🔐 Authentication & Security

### JWT Tokens
- **Algorithm**: HS256
- **Expiry**: 7 days (configurable)
- **Storage**: HttpOnly cookies
- **Key**: `SECRET_KEY` environment variable

### Credential Encryption
- **Algorithm**: Fernet (symmetric encryption)
- **Key**: `ENCRYPTION_KEY` environment variable (32 bytes)
- **Usage**: Provider credentials encrypted at rest

### Password Requirements
Enforced via `security.validate_password()`:
- Minimum 8 characters
- Uppercase letter
- Lowercase letter
- Number
- Special character

---

## 🧪 Testing

### Test Suite
```bash
cd backend
pytest tests/ -v
```

**Coverage:**
- 73 tests
- 100% pass rate
- ~85% code coverage

### Test Categories

**Authentication** (12 tests):
- Setup flow
- Login/logout
- Token validation
- Password validation

**Providers** (18 tests):
- CRUD operations
- Credential encryption
- Provider-specific logic

**Domains** (28 tests):
- CRUD operations
- IP updates
- History tracking
- Scheduling

**Services** (11 tests):
- IP detection
- Update logic
- Error handling

**System** (15 tests):
- System status
- Security utilities
- Edge cases

---

## 🛠️ Development

### Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**API Docs:**
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Initialize Database

```bash
python scripts/init_db.py
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_auth.py -v

# With coverage
pytest --cov=app tests/

# Watch mode (with pytest-watch)
ptw tests/
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

---

## 📊 Dependencies

### Core
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM
- **httpx** - Async HTTP client

### Security
- **python-jose** - JWT tokens
- **passlib[bcrypt]** - Password hashing
- **cryptography** - Credential encryption

### Scheduling
- **APScheduler** - Cron scheduling

### Testing
- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **requests-mock** - HTTP mocking

---

## 🔧 Configuration

### Environment Variables

```env
# Required
SECRET_KEY=your-secret-key-for-jwt
ENCRYPTION_KEY=your-32-byte-fernet-key

# Optional
DATABASE_PATH=backend/database/ip_hop.db
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=["http://localhost:3000"]
```

### Generate Keys

```bash
# SECRET_KEY (any random string)
openssl rand -hex 32

# ENCRYPTION_KEY (must be Fernet-compatible)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 📝 API Response Formats

### Success Response
```json
{
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

**For frontend integration, see:** [Frontend Documentation](../frontend/README.md)
