"""
MonthlyPuantaj model - Aylık puantaj kayıtları
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, Index, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MonthlyPuantaj(Base):
    """Aylık puantaj kayıtları (şantiyelerden gelen)"""
    __tablename__ = "monthly_puantaj"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dönem
    yil = Column(Integer, nullable=False, index=True)
    ay = Column(Integer, nullable=False, index=True)
    donem = Column(String(7), nullable=False, index=True)  # "2025-12"
    
    # Personel ve şantiye
    personnel_id = Column(Integer, ForeignKey('personnel.id'), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey('personnel_contracts.id'), nullable=True)
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id'), nullable=True)
    
    tckn = Column(String(11), nullable=False, index=True)
    adi_soyadi = Column(String(200), nullable=False)
    santiye_adi = Column(String(200), nullable=True)
    
    # Puantaj (Ham veriler)
    normal_gun = Column(Numeric(5, 2), default=0)         # Normal çalışma günü
    fazla_mesai_saat = Column(Numeric(7, 2), default=0)   # Fazla mesai (saat)
    tatil_mesai_gun = Column(Numeric(5, 2), default=0)    # Tatil çalışması (gün)
    yillik_izin_gun = Column(Numeric(5, 2), default=0)    # Yıllık ücretli izin (gün)
    rapor_gun = Column(Numeric(5, 2), default=0)          # Rapor (gün)
    
    # Hesaplanan (otomatik)
    hafta_tatili_gun = Column(Numeric(5, 2), default=0)   # Haftalık 45 saat kontrolü
    toplam_gun = Column(Numeric(5, 2), default=0)         # Normal + Tatil + İzin
    
    # Upload bilgisi
    upload_date = Column(TIMESTAMP, server_default=func.now())
    file_name = Column(String(500), nullable=True)
    
    # İşlem durumu
    is_processed = Column(Integer, default=0)  # Bordroya aktarıldı mı?
    
    # Notlar
    notes = Column(String(500), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # İlişkiler
    personnel = relationship("Personnel")
    contract = relationship("PersonnelContract")
    cost_center = relationship("CostCenter")

    def __repr__(self):
        return f"<MonthlyPuantaj {self.donem} - {self.tckn}>"

    __table_args__ = (
        Index('ix_puantaj_donem_tckn', 'donem', 'tckn'),
        Index('ix_puantaj_donem_santiye', 'donem', 'cost_center_id'),
    )
