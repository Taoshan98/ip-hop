# Authentication

API authentication using JWT tokens.

## Login

**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Example**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

## Using Tokens

Include token in all API requests:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1/providers
```

## Token Expiration

Tokens expire after 7 days by default.

When expired, you'll receive:
```json
{
  "detail": "Token has expired"
}
```

Re-authenticate to get a new token.

## Security

- Tokens are signed with `SECRET_KEY`
- Use HTTPS in production
- Store tokens securely
- Never commit tokens to version control
