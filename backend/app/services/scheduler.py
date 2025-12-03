import logging
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models import Domain
from app.services.ddns_service import DDNSService

logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Manages automatic IP update scheduling for domains with cron expressions.
    Uses AsyncIOScheduler for compatibility with FastAPI's async runtime.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        logger.info("AsyncIOScheduler started")
    
    def load_all_schedules(self):
        """
        Load all domains with cron schedules and create jobs.
        Called on application startup.
        """
        db = SessionLocal()
        try:
            domains = db.query(Domain).filter(Domain.cron_schedule.isnot(None)).all()
            for domain in domains:
                if domain.cron_schedule and self._validate_cron(domain.cron_schedule):
                    self.add_schedule(domain.id, domain.cron_schedule)
                    logger.info(f"Loaded schedule for domain {domain.id}: {domain.cron_schedule}")
        finally:
            db.close()
    
    def add_schedule(self, domain_id: int, cron_expression: str):
        """
        Add or update a scheduled job for a domain.
        """
        if not self._validate_cron(cron_expression):
            logger.error(f"Invalid cron expression for domain {domain_id}: {cron_expression}")
            return False
        
        job_id = f"domain_{domain_id}"
        
        # Remove existing job if it exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed old schedule for domain {domain_id}")
        
        # Add new job
        try:
            self.scheduler.add_job(
                func=self._check_and_update_domain,
                trigger=CronTrigger.from_crontab(cron_expression),
                id=job_id,
                args=[domain_id],
                replace_existing=True
            )
            logger.info(f"Added schedule for domain {domain_id}: {cron_expression}")
            return True
        except Exception as e:
            logger.error(f"Failed to add schedule for domain {domain_id}: {e}")
            return False
    
    def remove_schedule(self, domain_id: int):
        """
        Remove a scheduled job for a domain.
        """
        job_id = f"domain_{domain_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed schedule for domain {domain_id}")
            return True
        return False
    
    async def _check_and_update_domain(self, domain_id: int):
        """
        Background task to check and update IP for a domain.
        Only updates if IP has changed.
        """
        db = SessionLocal()
        try:
            domain = db.query(Domain).filter(Domain.id == domain_id).first()
            if not domain:
                logger.warning(f"Domain {domain_id} not found, removing schedule")
                self.remove_schedule(domain_id)
                return
            
            # Check if provider is enabled
            if not domain.provider.is_enabled:
                logger.info(f"Provider for domain {domain.domain_name} is disabled, skipping")
                return
            
            # Get current IP
            service = DDNSService(db)
            from app.core.ip_fetcher import IPFetcher
            fetcher = IPFetcher()
            
            try:
                current_ip = await fetcher.get_current_ip()
            except Exception as e:
                logger.error(f"Failed to fetch IP for domain {domain.domain_name}: {e}")
                return
            
            # Compare with last known IP
            if current_ip == domain.last_known_ip:
                logger.info(f"No IP change detected for {domain.domain_name} (still {current_ip})")
                return
            
            # IP changed, trigger update
            logger.info(f"IP changed for {domain.domain_name}: {domain.last_known_ip} -> {current_ip}")
            try:
                await service.update_domain_ip(domain_id)
                logger.info(f"Successfully updated {domain.domain_name} to {current_ip}")
            except Exception as e:
                logger.error(f"Failed to update {domain.domain_name}: {e}")
            
        finally:
            db.close()
    
    def _validate_cron(self, cron_expression: str) -> bool:
        """
        Validate a cron expression.
        """
        try:
            croniter(cron_expression)
            return True
        except Exception:
            return False
    
    def shutdown(self):
        """
        Gracefully shutdown the scheduler.
        """
        self.scheduler.shutdown()
        logger.info("AsyncIOScheduler shutdown")

# Global scheduler instance
scheduler_service: Optional[SchedulerService] = None

def get_scheduler() -> SchedulerService:
    """
    Get the global scheduler instance.
    """
    global scheduler_service
    if scheduler_service is None:
        scheduler_service = SchedulerService()
    return scheduler_service
