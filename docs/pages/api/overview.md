# API Overview

IP-HOP provides a RESTful API for programmatic access to all features.

## Base URL

```
http://localhost:8001/api/v1
```

## Authentication

All API endpoints (except `/auth/login`) require JWT authentication.

### Login

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Using Token

Include token in Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1/providers
```

## Interactive Documentation

Visit the auto-generated API docs:

```
http://localhost:8001/docs
```

Features:
- Try endpoints directly
- View request/response schemas
- Download OpenAPI spec

## API Endpoints

See detailed documentation:

- [Authentication](authentication.md)
- [Endpoints Reference](endpoints.md)

## Rate Limiting

Currently no rate limiting. May be added in future versions.

## Versioning

API version is included in URL: `/api/v1/`

Breaking changes will increment version number.

## Error Responses

Standard error format:

```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- `200` - Success
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error
