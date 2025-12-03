from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.providers import DomainConfig

logger = logging.getLogger(__name__)

class DDNSProvider(ABC):
    """
    Abstract Base Class for Dynamic DNS Providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the provider."""
        pass

    @abstractmethod
    async def update_record(self, ip: str, domain_config: 'DomainConfig') -> bool:
        """
        Updates the DNS record with the new IP address.
        Returns True if successful, False otherwise.
        Raises ProviderError on critical failures.
        """
        pass
