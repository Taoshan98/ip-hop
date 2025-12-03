from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

# Provider Schemas
class ProviderBase(BaseModel):
    name: str
    type: str
    is_enabled: bool = True

class ProviderCreate(ProviderBase):
    credentials: Dict[str, Any] # Will be encrypted

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    credentials: Optional[Dict[str, Any]] = None

class Provider(ProviderBase):
    id: int
    # We don't return credentials for security
    
    model_config = ConfigDict(from_attributes=True)

# Domain Schemas
class DomainBase(BaseModel):
    domain_name: str
    external_id: Optional[str] = None
    config: Dict[str, Any] = {}

class DomainCreate(DomainBase):
    provider_id: int
    cron_schedule: Optional[str] = None

class DomainUpdate(BaseModel):
    domain_name: Optional[str] = None
    external_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    cron_schedule: Optional[str] = None

class Domain(DomainBase):
    id: int
    provider_id: int
    last_known_ip: Optional[str] = None
    last_update_status: Optional[str] = None
    cron_schedule: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# History Schema
class IPHistory(BaseModel):
    id: int
    domain_id: int
    ip_address: str
    timestamp: datetime
    status: str
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
