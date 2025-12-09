# DDNS Providers

IP-HOP currently supports the following DDNS providers.

## Supported Providers

- ✅ **Cloudflare**
- ✅ **Dynu**
- ✅ **DuckDNS**
- ✅ **No-IP**

## Adding a Provider

### Through Web UI

1. Navigate to **Providers** page
2. Click **Add Provider**
3. Select provider type
4. Enter credentials
5. Click **Save**

## Cloudflare

### Prerequisites

- Cloudflare account
- Domain added to Cloudflare
- API Token with DNS edit permissions

### Configuration

1. **Create API Token**:
   - Go to Cloudflare Dashboard → Profile → API Tokens
   - Click "Create Token"
   - Use "Edit zone DNS" template
   - Select your zone
   - Create token and copy it

2. **Add Provider in IP-HOP**:
   - Type: `cloudflare`
   - Credentials: `{"api_token": "your-token-here"}`
   - Zone ID: Found in domain overview
   - Record ID: Auto-configured on first update

### Required Fields

- `api_token`: Your Cloudflare API token
- `zone_id` (in domain config): Cloudflare zone identifier
- `record_id` (in domain config): DNS record identifier

## Dynu

### Prerequisites

- Dynu account (free tier available)
- Dynu API token

### Configuration

1. **Get Token**:
   - Login to https://dynu.com
   - Go to API Credentials section
   - Generate or copy your API token

2. **Add Provider in IP-HOP**:
   - Type: `dynu`
   - Credentials: `{"token": "your-token-here"}`
   - Domain ID: Your Dynu domain ID

### Required Fields

- `token`: Your Dynu API token
- `id` (in domain config): Dynu domain ID

## DuckDNS

### Prerequisites

- DuckDNS account (free)
- DuckDNS token

### Configuration

1. **Get Token**:
   - Login to https://www.duckdns.org
   - Copy your token from the top of the page

2. **Add Provider in IP-HOP**:
   - Type: `duckdns`
   - Credentials: `{"token": "your-token-here"}`
   - Domain: `yoursubdomain` (or `yoursubdomain.duckdns.org`)

### Required Fields

- `token`: Your DuckDNS account token

### Notes

- Domain can be entered as just subdomain (`mysubdomain`) or full domain (`mysubdomain.duckdns.org`)
- DuckDNS automatically detects your IP if not specified
- Free service with no limits
- Perfect for home lab and personal use

## No-IP

### Prerequisites

- No-IP account (free tier available)
- DDNS Key credentials (recommended) or account credentials

### Configuration

1. **Create DDNS Key** (Recommended):
   - Login to https://www.noip.com
   - Go to "Dynamic DNS" → "DDNS Keys"
   - Click "Create New DDNS Key"
   - Select your hostname(s)
   - Copy the generated Username and Password

2. **Add Provider in IP-HOP**:
   - Type: `noip`
   - Credentials: `{"username": "ddns_key_username", "password": "ddns_key_password"}`
   - Domain: `yourhost.ddns.net`

### Required Fields

- `username`: DDNS Key username (or account email)
- `password`: DDNS Key password (or account password)

### Notes

- **DDNS Key is recommended** over account credentials for security
- DDNS Keys are **free** for all No-IP accounts
- If a DDNS Key is compromised, only DNS updates are affected (not your full account)
- Supports all No-IP hostname formats (e.g., `.ddns.net`, `.zapto.org`, etc.)

## Testing Configuration

After adding a provider:

1. Click **Test Connection**
2. Verify current IP is detected
3. Click **Update Now** to force an update
4. Check provider dashboard to confirm

## Auto-Update Settings

Configure automatic updates:

- **Update Interval**: How often to check for IP changes
- **Cron Schedule**: Custom schedule using cron syntax
- **Retry on Failure**: Retry failed updates (recommended)

## Troubleshooting

### Authentication Failed

**Cloudflare**:
- Verify API token has correct permissions ("Zone.DNS Edit")
- Check Zone ID is correct
- Ensure record exists in Cloudflare dashboard

**Dynu**:
- Ensure token is copied correctly
- Verify domain exists under your Dynu account
- Check domain ID is correct

### Update Failed

Check:
- Internet connection
- Provider API status
- IP-HOP logs: `docker logs iphop`

### IP Not Updating

1. Check current detected IP: Dashboard or API `/api/v1/system/status`
2. Verify domain configuration (IDs, credentials)
3. Check provider dashboard for last update time

## Next Steps

- [Network Setup](network.md)
- [API Documentation](../api/overview.md)
