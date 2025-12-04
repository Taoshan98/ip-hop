import httpx
import logging
from typing import TYPE_CHECKING
from app.core.exceptions import ProviderError
from app.providers.base import DDNSProvider

if TYPE_CHECKING:
    from app.schemas.providers import DomainConfig

logger = logging.getLogger(__name__)

class DuckDNSProvider(DDNSProvider):
    """
    Implementation for DuckDNS DDNS Provider.
    """
    
    API_URL = "https://www.duckdns.org/update"

    def __init__(self, token: str):
        self.token = token

    @property
    def name(self) -> str:
        return "duckdns"

    async def update_record(self, ip: str, domain_config: 'DomainConfig') -> bool:
        """
        Updates the DuckDNS domain.
        Requires domain name (subdomain only, without .duckdns.org).
        """
        if not self.token:
            logger.error("DuckDNS token is missing.")
            raise ProviderError("DuckDNS token missing")
            
        # Extract subdomain (remove .duckdns.org if present)
        domain_name = domain_config.name
        if domain_name.endswith('.duckdns.org'):
            subdomain = domain_name.replace('.duckdns.org', '')
        else:
            subdomain = domain_name
        
        if not subdomain:
            logger.error(f"DuckDNS subdomain is empty for {domain_name}")
            return False

        # DuckDNS API uses query parameters
        params = {
            "domains": subdomain,
            "token": self.token,
            "ip": ip,
            "verbose": "true"  # Get detailed response
        }

        try:
            logger.info(f"Updating DuckDNS subdomain {subdomain} to {ip}...")
            async with httpx.AsyncClient() as client:
                response = await client.get(self.API_URL, params=params, timeout=10)
                response_text = response.text.strip()

                # Parse response
                if response.status_code == 200:
                    if response_text.startswith('OK'):
                        logger.info(f"DuckDNS update successful: {ip}")
                        return True
                    elif response_text == 'KO':
                        logger.error(f"DuckDNS update failed for {subdomain}: Invalid token or domain")
                        return False
                    else:
                        logger.error(f"DuckDNS unexpected response: {response_text}")
                        return False
                else:
                    logger.error(f"DuckDNS HTTP error {response.status_code}")
                    return False

        except httpx.HTTPError as e:
            logger.error(f"Network error updating DuckDNS: {e}")
            raise ProviderError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating DuckDNS: {e}")
            raise ProviderError(f"Unexpected error: {e}")
