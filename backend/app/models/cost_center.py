"""
CostCenter model - Maliyet merkezleri (Şantiyeler)
Luca-compatible: cost_centers table
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CostCenter(Base):
    """Maliyet Merkezi (Şantiye)"""
    __tablename__ = "cost_centers"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    bolum_adi = Column(String(200), nullable=True)
    
    # Sistem
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="cost_center")
    
    def __repr__(self):
        return f"<CostCenter {self.code} - {self.name}>"
