import httpx
import logging
import base64
from typing import TYPE_CHECKING
from app.core.exceptions import ProviderError
from app.providers.base import DDNSProvider

if TYPE_CHECKING:
    from app.schemas.providers import DomainConfig

logger = logging.getLogger(__name__)


class NoIPProvider(DDNSProvider):
    """
    Implementation for No-IP DDNS Provider.
    Uses DDNS Key authentication (username + password).
    """
    
    API_URL = "https://dynupdate.no-ip.com/nic/update"
    USER_AGENT = "IP-HOP/1.0.1 github.com/Taoshan98/ip-hop"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    @property
    def name(self) -> str:
        return "noip"

    async def update_record(self, ip: str, domain_config: 'DomainConfig') -> bool:
        """
        Updates the No-IP hostname.
        Uses HTTP Basic Authentication with DDNS Key credentials.
        """
        if not self.username or not self.password:
            logger.error("No-IP credentials are missing.")
            raise ProviderError("No-IP credentials missing")
            
        hostname = domain_config.name
        
        if not hostname:
            logger.error("No-IP hostname is empty")
            return False

        # Build Basic Auth header
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "User-Agent": self.USER_AGENT
        }
        
        params = {
            "hostname": hostname,
            "myip": ip
        }

        try:
            logger.info(f"Updating No-IP hostname {hostname} to {ip}...")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.API_URL, 
                    params=params, 
                    headers=headers, 
                    timeout=10
                )
                response_text = response.text.strip()

                # Parse No-IP response codes
                if response.status_code == 200:
                    if response_text.startswith('good'):
                        logger.info(f"No-IP update successful: {ip}")
                        return True
                    elif response_text.startswith('nochg'):
                        logger.info(f"No-IP: IP unchanged ({ip})")
                        return True
                    elif response_text == 'badauth':
                        logger.error(f"No-IP authentication failed for {hostname}")
                        raise ProviderError("No-IP authentication failed (badauth)")
                    elif response_text == 'nohost':
                        logger.error(f"No-IP hostname not found: {hostname}")
                        return False
                    elif response_text == 'badagent':
                        logger.error("No-IP: Client has been banned (badagent)")
                        raise ProviderError("No-IP client banned (badagent)")
                    elif response_text == 'abuse':
                        logger.error(f"No-IP: Account blocked for abuse: {hostname}")
                        raise ProviderError("No-IP account blocked (abuse)")
                    elif response_text == '!donator':
                        logger.error(f"No-IP: Feature not available for account")
                        return False
                    else:
                        logger.error(f"No-IP unexpected response: {response_text}")
                        return False
                else:
                    logger.error(f"No-IP HTTP error {response.status_code}")
                    return False

        except httpx.HTTPError as e:
            logger.error(f"Network error updating No-IP: {e}")
            raise ProviderError(f"Network error: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating No-IP: {e}")
            raise ProviderError(f"Unexpected error: {e}")
