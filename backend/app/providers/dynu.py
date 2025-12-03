import httpx
import logging
from typing import TYPE_CHECKING
from app.core.exceptions import ProviderError
from app.providers.base import DDNSProvider

if TYPE_CHECKING:
    from app.schemas.providers import DomainConfig

logger = logging.getLogger(__name__)

class DynuProvider(DDNSProvider):
    """
    Implementation for Dynu DDNS Provider.
    """
    
    API_URL = "https://api.dynu.com/v2/dns"

    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    @property
    def name(self) -> str:
        return "dynu"

    async def update_record(self, ip: str, domain_config: 'DomainConfig') -> bool:
        """
        Updates the Dynu DNS record.
        """
        if not self.auth_token:
             logger.error("Dynu API Token is missing.")
             raise ProviderError("Dynu API Token missing")
             
        domain_id = domain_config.id
        domain_name = domain_config.name
        
        if not domain_id or not domain_name:
            logger.error(f"Dynu configuration incomplete for domain {domain_name}. ID is required.")
            return False

        url = f'{self.API_URL}/{domain_id}'
        
        headers = {
            "accept": "application/json",
            "API-Key": self.auth_token
        }

        payload = {
            "name": domain_name,
            "group": "",
            "ipv4Address": ip,
            "ipv6Address": None,
            "ttl": 90,
            "ipv4": True,
            "ipv6": False,
            "ipv4WildcardAlias": True,
            "ipv6WildcardAlias": False,
            "allowZoneTransfer": False,
            "dnssec": True
        }

        try:
            logger.info(f"Updating Dynu record for {domain_name} to {ip}...")
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10)
                data = response.json()

                if response.status_code == 200 and data.get('statusCode') == 200:
                    logger.info(f"Dynu update successful: {ip}")
                    return True
                else:
                    logger.error(
                        f"Dynu update failed for {domain_name}:\n"
                        f"Status: {data.get('statusCode')}\n"
                        f"Type: {data.get('type')}\n"
                        f"Message: {data.get('message')}"
                    )
                    return False

        except httpx.HTTPError as e:
            logger.error(f"Network error updating Dynu: {e}")
            raise ProviderError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating Dynu: {e}")
            raise ProviderError(f"Unexpected error: {e}")
