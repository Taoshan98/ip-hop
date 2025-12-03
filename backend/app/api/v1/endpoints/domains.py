from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import SessionLocal
from app.models import Domain, Provider, IPHistory
from app.schemas import resources as schemas
from app.api.v1.endpoints.auth import get_db, oauth2_scheme
from app.services.ddns_service import DDNSService
from app.services.scheduler import get_scheduler

router = APIRouter()

@router.get("", response_model=List[schemas.Domain])
async def read_domains(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    domains = db.query(Domain).offset(skip).limit(limit).all()
    return domains

@router.post("", response_model=schemas.Domain)
async def create_domain(domain: schemas.DomainCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    provider = db.query(Provider).filter(Provider.id == domain.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    new_domain = Domain(
        provider_id=domain.provider_id,
        domain_name=domain.domain_name,
        external_id=domain.external_id,
        config=domain.config,
        cron_schedule=getattr(domain, 'cron_schedule', None)
    )
    db.add(new_domain)
    db.commit()
    db.refresh(new_domain)
    
    # Add scheduler if cron_schedule is provided
    if new_domain.cron_schedule:
        scheduler = get_scheduler()
        scheduler.add_schedule(new_domain.id, new_domain.cron_schedule)
    
    return new_domain

@router.put("/{domain_id}", response_model=schemas.Domain)
async def update_domain(domain_id: int, domain_update: schemas.DomainUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not db_domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    if domain_update.domain_name is not None:
        db_domain.domain_name = domain_update.domain_name
    if domain_update.external_id is not None:
        db_domain.external_id = domain_update.external_id
    if domain_update.config is not None:
        db_domain.config = domain_update.config
    
    # Update cron schedule
    if domain_update.cron_schedule is not None:
        db_domain.cron_schedule = domain_update.cron_schedule
        scheduler = get_scheduler()
        if domain_update.cron_schedule:
            scheduler.add_schedule(db_domain.id, domain_update.cron_schedule)
        else:
            scheduler.remove_schedule(db_domain.id)
        
    db.commit()
    db.refresh(db_domain)
    return db_domain

@router.get("/{domain_id}/history", response_model=List[schemas.IPHistory])
async def read_domain_history(domain_id: int, limit: int = 20, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    history = db.query(IPHistory).filter(IPHistory.domain_id == domain_id).order_by(IPHistory.timestamp.desc()).limit(limit).all()
    return history

@router.delete("/{domain_id}")
async def delete_domain(domain_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # Remove scheduler if exists
    scheduler = get_scheduler()
    scheduler.remove_schedule(domain_id)
    
    db.delete(domain)
    db.commit()
    return {"message": "Domain deleted successfully"}

@router.post("/{domain_id}/update_ip")
async def update_domain_ip(domain_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    service = DDNSService(db)
    try:
        success = await service.update_domain_ip(domain_id)
        if success:
            return {"message": "IP updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Update failed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
