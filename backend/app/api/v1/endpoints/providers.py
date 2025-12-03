from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.base import SessionLocal
from app.models import Provider, Domain
from app.schemas import resources as schemas
from app.core import security
from app.api.v1.endpoints.auth import get_db, oauth2_scheme

router = APIRouter()

@router.get("", response_model=List[schemas.Provider])
def read_providers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    providers = db.query(Provider).offset(skip).limit(limit).all()
    return providers

@router.post("", response_model=schemas.Provider)
def create_provider(provider: schemas.ProviderCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_provider = db.query(Provider).filter(Provider.name == provider.name).first()
    if db_provider:
        raise HTTPException(status_code=400, detail="Provider with this name already exists")
    
    encrypted_creds = security.encrypt_credentials(provider.credentials)
    
    new_provider = Provider(
        name=provider.name,
        type=provider.type,
        is_enabled=provider.is_enabled,
        credentials_encrypted=encrypted_creds
    )
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return new_provider

@router.put("/{provider_id}", response_model=schemas.Provider)
def update_provider(provider_id: int, provider_update: schemas.ProviderUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    if provider_update.name is not None:
        db_provider.name = provider_update.name
    if provider_update.is_enabled is not None:
        db_provider.is_enabled = provider_update.is_enabled
    if provider_update.credentials is not None:
        db_provider.credentials_encrypted = security.encrypt_credentials(provider_update.credentials)
        
    db.commit()
    db.refresh(db_provider)
    return db_provider

@router.delete("/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db.delete(provider)
    db.commit()
    return {"message": "Provider deleted successfully"}
