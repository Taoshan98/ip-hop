import httpx
import logging
from typing import TYPE_CHECKING
from app.core.exceptions import ProviderError
from app.providers.base import DDNSProvider

if TYPE_CHECKING:
    from app.schemas.providers import DomainConfig

logger = logging.getLogger(__name__)

class CloudflareProvider(DDNSProvider):
    """
    Implementation for Cloudflare DDNS Provider.
    """
    
    API_URL = "https://api.cloudflare.com/client/v4"

    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    @property
    def name(self) -> str:
        return "cloudflare"

    async def update_record(self, ip: str, domain_config: 'DomainConfig') -> bool:
        """
        Updates the Cloudflare DNS record.
        Requires zone_id and record_id in domain_config.
        """
        if not self.auth_token:
             logger.error("Cloudflare API Token is missing.")
             raise ProviderError("Cloudflare API Token missing")
             
        zone_id = domain_config.zone_id
        record_id = domain_config.record_id
        domain_name = domain_config.name
        proxied = domain_config.proxied
        
        if not zone_id or not record_id:
            logger.error(f"Cloudflare configuration incomplete for {domain_name}. zone_id and record_id are required.")
            return False

        url = f'{self.API_URL}/zones/{zone_id}/dns_records/{record_id}'
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "type": "A",
            "name": domain_name,
            "content": ip,
            "ttl": 1, # Automatic
            "proxied": proxied
        }

        try:
            logger.info(f"Updating Cloudflare record for {domain_name} to {ip}...")
            async with httpx.AsyncClient() as client:
                response = await client.put(url, json=payload, headers=headers, timeout=10)
                data = response.json()

                if response.status_code == 200 and data.get('success'):
                    logger.info(f"Cloudflare update successful: {ip}")
                    return True
                else:
                    errors = data.get('errors', [])
                    error_msg = "; ".join([f"{e.get('code')}: {e.get('message')}" for e in errors])
                    logger.error(f"Cloudflare update failed for {domain_name}: {error_msg}")
                    return False

        except httpx.HTTPError as e:
            logger.error(f"Network error updating Cloudflare: {e}")
            raise ProviderError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating Cloudflare: {e}")
            raise ProviderError(f"Unexpected error: {e}")
