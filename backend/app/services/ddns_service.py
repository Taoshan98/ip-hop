import logging
from sqlalchemy.orm import Session
from app.models import Domain, Provider, IPHistory
from app.core import security
from app.core.ip_fetcher import IPFetcher
from app.schemas.providers import DomainConfig
from app.providers.dynu import DynuProvider
from app.providers.cloudflare import CloudflareProvider
from app.providers.duckdns import DuckDNSProvider
from app.providers.noip import NoIPProvider

logger = logging.getLogger(__name__)

class DDNSService:
    
    def __init__(self, db: Session):
        self.db = db

    async def update_domain_ip(self, domain_id: int) -> bool:
        """
        Triggers an immediate IP update for a specific domain.
        """
        domain = self.db.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            raise ValueError("Domain not found")
            
        provider = domain.provider
        if not provider.is_enabled:
             raise ValueError("Provider is disabled")

        # 1. Fetch Current IP
        fetcher = IPFetcher()
        try:
            current_ip = await fetcher.get_current_ip()
        except Exception as e:
            self._log_history(domain.id, "0.0.0.0", "FAILED", f"IP Fetch Error: {e}")
            raise e

        # 2. Decrypt Credentials
        try:
            creds = security.decrypt_credentials(provider.credentials_encrypted)
            
            provider_instance = None
            if provider.type == "dynu":
                provider_instance = DynuProvider(auth_token=creds.get("token"))
            elif provider.type == "cloudflare":
                provider_instance = CloudflareProvider(auth_token=creds.get("token"))
            elif provider.type == "duckdns":
                provider_instance = DuckDNSProvider(token=creds.get("token"))
            elif provider.type == "noip":
                provider_instance = NoIPProvider(
                    username=creds.get("username"),
                    password=creds.get("password")
                )
            else:
                raise ValueError(f"Unknown provider type: {provider.type}")

            # 3. Prepare Domain Config
            d_config = DomainConfig(
                name=domain.domain_name,
                id=domain.external_id, # For Dynu
                zone_id=domain.external_id, # For Cloudflare (mapping needed?)
                record_id=domain.config.get("record_id"),
                proxied=domain.config.get("proxied", False)
            )
            
            # 4. Update
            success = await provider_instance.update_record(current_ip, d_config)
            
            if success:
                self._log_history(domain.id, current_ip, "SUCCESS", "Updated successfully")
                domain.last_known_ip = current_ip
                domain.last_update_status = "SUCCESS"
                self.db.commit()
                self._cleanup_old_history(domain.id)  # Retention policy
                return True
            else:
                self._log_history(domain.id, current_ip, "FAILED", "Provider rejected update")
                domain.last_update_status = "FAILED"
                self.db.commit()
                return False

        except Exception as e:
            logger.error(f"Update failed: {e}")
            self._log_history(domain.id, current_ip, "FAILED", str(e))
            domain.last_update_status = "FAILED"
            self.db.commit()
            raise e

    def _log_history(self, domain_id: int, ip: str, status: str, message: str):
        history = IPHistory(
            domain_id=domain_id,
            ip_address=ip,
            status=status,
            message=message
        )
        self.db.add(history)
    
    def _cleanup_old_history(self, domain_id: int):
        """
        Keep only the last 20 IP history records for a domain.
        """
        # Get all history for domain, ordered by timestamp DESC
        all_history = self.db.query(IPHistory).filter(
            IPHistory.domain_id == domain_id
        ).order_by(IPHistory.timestamp.desc()).all()
        
        # If more than 20, delete the oldest ones
        if len(all_history) > 20:
            records_to_delete = all_history[20:]
            for record in records_to_delete:
                self.db.delete(record)
            self.db.commit()
            logger.info(f"Cleaned up {len(records_to_delete)} old history records for domain {domain_id}")

