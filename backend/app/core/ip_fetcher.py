import httpx
import logging
import re
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.core.exceptions import IPFetchError

logger = logging.getLogger(__name__)

class IPFetcher:
    """
    Responsible for fetching the current WAN IP address from multiple external services.
    Uses async httpx for non-blocking I/O.
    """
    
    IP_SERVICES = [
        "https://checkip.amazonaws.com/",
        "https://icanhazip.com/",
        "https://ifconfig.me/ip",
        "https://api.ipify.org",
        "https://ipecho.net/plain",
    ]

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def _validate_ip(self, ip: str) -> bool:
        """Validates if the string is a valid IPv4 address."""
        # Simple regex for IPv4
        pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if re.match(pattern, ip):
            return True
        return False

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.HTTPError))
    async def _fetch_from_url(self, client: httpx.AsyncClient, url: str) -> str:
        """
        Fetches IP from a single URL with retries.
        Raises httpx.HTTPError on failure.
        """
        response = await client.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text.strip()

    async def get_current_ip(self) -> str:
        """
        Iterates through available IP services to find the current WAN IP.
        Returns the first valid IP found.
        Raises IPFetchError if all services fail.
        """
        errors = []
        
        async with httpx.AsyncClient() as client:
            for url in self.IP_SERVICES:
                try:
                    logger.debug(f"Attempting to fetch IP from {url}")
                    ip = await self._fetch_from_url(client, url)
                    
                    if self._validate_ip(ip):
                        logger.info(f"Successfully fetched IP: {ip} from {url}")
                        return ip
                    else:
                        logger.warning(f"Invalid IP response from {url}: {ip}")
                        errors.append(f"{url}: Invalid IP")
                except Exception as e:
                    logger.warning(f"Failed to fetch IP from {url}: {e}")
                    errors.append(f"{url}: {str(e)}")

        error_msg = "All IP fetch attempts failed. Details: " + "; ".join(errors)
        logger.error(error_msg)
        raise IPFetchError(error_msg)
