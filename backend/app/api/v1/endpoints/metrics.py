from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from datetime import datetime, timedelta, UTC
from app.db.base import SessionLocal
from app.models import Domain, Provider, IPHistory
from app.api.v1.endpoints.auth import get_db, oauth2_scheme

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get dashboard metrics including domain stats, success rates, and provider statistics.
    """
    # Total domains
    total_domains = db.query(Domain).count()
    
    # Active domains (domains with enabled providers)
    active_domains = db.query(Domain).join(Provider).filter(Provider.is_enabled == True).count()
    
    # Calculate 24h timeframe
    now = datetime.now(UTC)
    yesterday = now - timedelta(hours=24)
    
    # Updates in last 24h
    updates_24h = db.query(IPHistory).filter(
        IPHistory.timestamp >= yesterday
    ).count()
    
    # Success/failure counts 24h
    success_count_24h = db.query(IPHistory).filter(
        IPHistory.timestamp >= yesterday,
        IPHistory.status == "SUCCESS"
    ).count()
    
    failed_updates_24h = db.query(IPHistory).filter(
        IPHistory.timestamp >= yesterday,
        IPHistory.status == "FAILED"
    ).count()
    
    # Success rate calculation
    if updates_24h > 0:
        success_rate_24h = round((success_count_24h / updates_24h) * 100, 1)
    else:
        success_rate_24h = 0.0
    
    # Unique IPs in last 24h
    unique_ips_24h = db.query(func.count(func.distinct(IPHistory.ip_address))).filter(
        IPHistory.timestamp >= yesterday
    ).scalar() or 0
    
    # Last update time (most recent across all domains)
    last_update = db.query(IPHistory).order_by(IPHistory.timestamp.desc()).first()
    last_update_time = last_update.timestamp.isoformat() if last_update else None
    
    # Provider statistics
    provider_stats = db.query(
        Provider.type,
        func.count(Domain.id).label('count'),
        func.sum(func.cast(Provider.is_enabled, Integer)).label('active')
    ).outerjoin(Domain).group_by(Provider.type).all()
    
    providers_stats = [
        {
            "type": stat.type,
            "count": stat.count or 0,
            "active": stat.active or 0
        }
        for stat in provider_stats
    ]
    
    return {
        "total_domains": total_domains,
        "active_domains": active_domains,
        "success_rate_24h": success_rate_24h,
        "total_updates_24h": updates_24h,
        "failed_updates_24h": failed_updates_24h,
        "unique_ips_24h": unique_ips_24h,
        "last_update_time": last_update_time,
        "providers_stats": providers_stats
    }

@router.get("/response-time")
def get_response_time_metrics(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get average IP update response time metrics over different time periods.
    """
    now = datetime.now(UTC)
    
    # Time periods
    periods = {
        "1h": now - timedelta(hours=1),
        "6h": now - timedelta(hours=6),
        "24h": now - timedelta(hours=24)
    }
    
    result = {}
    for period_name, start_time in periods.items():
        # Note: IPHistory doesn't have duration/response_time field
        # This is a placeholder - in real implementation you'd add this field
        updates = db.query(IPHistory).filter(
            IPHistory.timestamp >= start_time
        ).all()
        
        result[period_name] = {
            "count": len(updates),
            "avg_time": 0,  # Placeholder - would calculate from duration field
            "min_time": 0,  # Placeholder
            "max_time": 0   # Placeholder
        }
    
    return result

@router.get("/ip-changes")
def get_ip_change_frequency(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Track IP address change frequency over time.
    """
    now = datetime.now(UTC)
    week_ago = now - timedelta(days=7)
    
    # Get all domains
    domains = db.query(Domain).all()
    
    changes_per_domain = []
    for domain in domains:
        # Get IP changes for this domain in the last week
        history = db.query(IPHistory).filter(
            IPHistory.domain_id == domain.id,
            IPHistory.timestamp >= week_ago
        ).order_by(IPHistory.timestamp.asc()).all()
        
        # Count actual IP changes (when IP differs from previous)
        changes = 0
        prev_ip = None
        for entry in history:
            if prev_ip and prev_ip != entry.ip_address:
                changes += 1
            prev_ip = entry.ip_address
        
        changes_per_domain.append({
            "domain_id": domain.id,
            "domain_name": domain.domain_name,
            "changes_last_week": changes,
            "changes_per_day": round(changes / 7, 2) if changes > 0 else 0
        })
    
    # Calculate totals
    total_changes = sum(d["changes_last_week"] for d in changes_per_domain)
    
    return {
        "total_changes_last_week": total_changes,
        "average_changes_per_day": round(total_changes / 7, 2) if total_changes > 0 else 0,
        "domains": changes_per_domain
    }

@router.get("/provider-stats")
def get_provider_success_rates(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get detailed success rate statistics per provider.
    """
    now = datetime.now(UTC)
    yesterday = now - timedelta(hours=24)
    
    providers = db.query(Provider).all()
    
    provider_details = []
    for provider in providers:
        # Get domains for this provider
        domains = db.query(Domain).filter(Domain.provider_id == provider.id).all()
        domain_ids = [d.id for d in domains]
        
        if not domain_ids:
            continue
        
        # Get update history for these domains in last 24h
        total_updates = db.query(IPHistory).filter(
            IPHistory.domain_id.in_(domain_ids),
            IPHistory.timestamp >= yesterday
        ).count()
        
        successful_updates = db.query(IPHistory).filter(
            IPHistory.domain_id.in_(domain_ids),
            IPHistory.timestamp >= yesterday,
            IPHistory.status == "SUCCESS"
        ).count()
        
        # Get last update time
        last_update = db.query(IPHistory).filter(
            IPHistory.domain_id.in_(domain_ids)
        ).order_by(IPHistory.timestamp.desc()).first()
        
        success_rate = round((successful_updates / total_updates) * 100, 1) if total_updates > 0 else 0
        
        provider_details.append({
            "provider_id": provider.id,
            "provider_name": provider.name,
            "provider_type": provider.type,
            "is_enabled": provider.is_enabled,
            "total_domains": len(domains),
            "updates_24h": total_updates,
            "successful_updates_24h": successful_updates,
            "success_rate_24h": success_rate,
            "last_update_time": last_update.timestamp.isoformat() if last_update else None
        })
    
    return {
        "providers": provider_details,
        "total_providers": len(provider_details)
    }

@router.get("/uptime")
def get_system_uptime(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Calculate system uptime and reliability metrics.
    """
    now = datetime.now(UTC)
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)
    
    # Calculate uptime based on successful updates vs total expected updates
    # For 24h
    total_24h = db.query(IPHistory).filter(
        IPHistory.timestamp >= day_ago
    ).count()
    
    success_24h = db.query(IPHistory).filter(
        IPHistory.timestamp >= day_ago,
        IPHistory.status == "SUCCESS"
    ).count()
    
    # For 7 days
    total_7d = db.query(IPHistory).filter(
        IPHistory.timestamp >= week_ago
    ).count()
    
    success_7d = db.query(IPHistory).filter(
        IPHistory.timestamp >= week_ago,
        IPHistory.status == "SUCCESS"
    ).count()
    
    uptime_24h = round((success_24h / total_24h) * 100, 2) if total_24h > 0 else 100
    uptime_7d = round((success_7d / total_7d) * 100, 2) if total_7d > 0 else 100
    
    # Check scheduler health (simple check - could be enhanced)
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()
    scheduler_running = scheduler.scheduler.running if hasattr(scheduler, 'scheduler') else False
    
    return {
        "uptime_24h": uptime_24h,
        "uptime_7d": uptime_7d,
        "total_requests_24h": total_24h,
        "successful_requests_24h": success_24h,
        "total_requests_7d": total_7d,
        "successful_requests_7d": success_7d,
        "scheduler_status": "running" if scheduler_running else "stopped"
    }

@router.get("/activity")
def get_recent_activity(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    limit: int = 20
):
    """
    Get recent activity timeline with detailed update information.
    """
    # Get recent updates with domain information
    recent_updates = db.query(
        IPHistory,
        Domain.domain_name
    ).join(
        Domain, IPHistory.domain_id == Domain.id
    ).order_by(
        IPHistory.timestamp.desc()
    ).limit(limit).all()
    
    activity = []
    for update, domain_name in recent_updates:
        activity.append({
            "id": update.id,
            "domain_id": update.domain_id,
            "domain_name": domain_name,
            "ip_address": update.ip_address,
            "status": update.status,
            "timestamp": update.timestamp.isoformat(),
            "message": update.message
        })
    
    return {
        "activity": activity,
        "count": len(activity)
    }

