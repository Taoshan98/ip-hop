# API Endpoints

Complete reference of all API endpoints.

## Authentication

### Login
`POST /api/v1/auth/login`

Authenticate and get JWT token.

## Providers

### List Providers
`GET /api/v1/providers`

Returns all configured DDNS providers.

### Create Provider
`POST /api/v1/providers`

Create new DDNS provider.

**Request Body**:
```json
{
  "name": "string",
  "type": "cloudflare" | "dynu",
  "credentials": {},
  "is_enabled": true
}
```

### Update Provider
`PUT /api/v1/providers/{provider_id}`

Update provider configuration.

### Delete Provider
`DELETE /api/v1/providers/{provider_id}`

Remove provider.

## Domains

### List Domains
`GET /api/v1/domains`

Get all domains.

### Create Domain
`POST /api/v1/domains`

Create new domain.

### Update Domain
`PUT /api/v1/domains/{domain_id}`

Update domain configuration.

### Delete Domain
`DELETE /api/v1/domains/{domain_id}`

Remove domain.

### Get Domain History
`GET /api/v1/domains/{domain_id}/history`

Get IP update history for domain.

**Query Parameters**:
- `limit`: Number of records (default: 20)

### Force Domain Update
`POST /api/v1/domains/{domain_id}/update_ip`

Trigger immediate IP update for domain.

## System

### System Status
`GET /api/v1/system/status`

Get system health and initialization status.

**Response**:
```json
{
  "initialized": true,
  "version": "1.0.0"
}
```

## Metrics

### Dashboard Metrics
`GET /api/v1/metrics/dashboard`

Get dashboard statistics.

### Provider Statistics
`GET /api/v1/metrics/provider-stats`

Get detailed success rate statistics per provider.

## Full Documentation

For complete API documentation with interactive testing, visit:

```
http://localhost:8001/docs
```
