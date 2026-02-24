"""
PersonnelDraftContract Model
Personel taslak sözleşme modeli
"""
from sqlalchemy import Column, Integer, String, Numeric, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PersonnelDraftContract(Base):
    """Personel taslak sözleşme modeli - Net ücret ve çalışma koşulları"""
    
    __tablename__ = 'personnel_draft_contracts'
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    personnel_id = Column(Integer, ForeignKey('personnel.id'), nullable=False, index=True)
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id'), nullable=True, index=True)
    
    # Personel bilgileri
    tc_kimlik_no = Column(String(11), nullable=True, index=True)
    
    # Ücret bilgileri
    ucret_nevi = Column(
        SQLEnum('aylik', 'sabit aylik', 'gunluk', name='ucret_nevi_enum'),
        nullable=False
    )
    net_ucret = Column(Numeric(18, 2), nullable=True)
    
    # Oranlar
    fm_orani = Column(Numeric(5, 2), default=1.00)
    tatil_orani = Column(Numeric(5, 2), default=1.00)
    
    # Çalışma takvimi
    calisma_takvimi = Column(
        SQLEnum('atipi', 'btipi', 'ctipi', name='calisma_takvimi_enum'),
        nullable=True
    )
    
    # Status
    is_active = Column(Integer, default=1)
    
    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    personnel = relationship("Personnel", back_populates="draft_contracts")
    cost_center = relationship("CostCenter", foreign_keys=[cost_center_id])
    
    def __repr__(self):
        return f"<PersonnelDraftContract(id={self.id}, personnel_id={self.personnel_id}, ucret_nevi={self.ucret_nevi}, net_ucret={self.net_ucret})>"
