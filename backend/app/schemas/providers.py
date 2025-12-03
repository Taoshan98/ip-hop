from pydantic import BaseModel
from typing import Optional

class DomainConfig(BaseModel):
    name: str
    id: Optional[str] = None
    zone_id: Optional[str] = None
    record_id: Optional[str] = None
    proxied: bool = False
