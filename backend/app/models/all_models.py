from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user") # admin, user
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False) # dynu, cloudflare
    credentials_encrypted = Column(Text, nullable=False) # Encrypted JSON blob
    is_enabled = Column(Boolean, default=True)
    
    domains = relationship("Domain", back_populates="provider", cascade="all, delete-orphan")

class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    domain_name = Column(String, index=True, nullable=False)
    external_id = Column(String, nullable=True) # Zone ID or Record ID
    config = Column(JSON, default={}) # Extra config like proxied: true
    last_known_ip = Column(String, nullable=True)
    last_update_status = Column(String, nullable=True) # SUCCESS, FAILED
    cron_schedule = Column(String, nullable=True) # Cron expression for auto-updates
    
    provider = relationship("Provider", back_populates="domains")
    history = relationship("IPHistory", back_populates="domain", cascade="all, delete-orphan")

class IPHistory(Base):
    __tablename__ = "ip_history"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    ip_address = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False) # SUCCESS, FAILED
    message = Column(Text, nullable=True)

    domain = relationship("Domain", back_populates="history")
