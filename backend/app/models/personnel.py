"""
Personnel model - Personel kartları (Luca-compatible)
Dokümana göre sadece 6 temel alan
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(Integer, primary_key=True, index=True)
    tc_kimlik_no = Column(String(11), unique=True, nullable=False, index=True)
    ad = Column(String(100), nullable=False)
    soyad = Column(String(100), nullable=False)
    accounts_id = Column(Integer, ForeignKey('accounts.id'), nullable=True, index=True)
    iban = Column(String(34), nullable=True)
    
    # Sistem
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    account = relationship("Account", foreign_keys=[accounts_id])
    contracts = relationship("PersonnelContract", back_populates="personnel")

    def __repr__(self):
        return f"<Personnel {self.tc_kimlik_no} - {self.ad} {self.soyad}>"
