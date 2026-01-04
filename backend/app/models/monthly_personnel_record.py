"""
MonthlyPersonnelRecord model - Aylık personel sicil kayıtları
Luca'dan import edilen aylık personel çalışma kayıtları
Bir personel aynı ayda birden fazla şantiyede çalışabilir
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, TIMESTAMP, Text, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MonthlyPersonnelRecord(Base):
    """Aylık personel sicil kayıtları (Luca import)"""
    __tablename__ = "monthly_personnel_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Personel ve Dönem
    personnel_id = Column(Integer, ForeignKey('personnel.id', ondelete='CASCADE'), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey('personnel_contracts.id', ondelete='SET NULL'), nullable=True, index=True)
    donem = Column(String(7), nullable=False, index=True, comment='YYYY-MM format (örn: 2026-01)')
    yil = Column(Integer, nullable=False, index=True)
    ay = Column(Integer, nullable=False, index=True)
    
    # Personel Bilgileri
    adi = Column(String(100), nullable=True)
    soyadi = Column(String(100), nullable=True)
    tc_kimlik_no = Column(String(11), nullable=False, index=True)
    cinsiyeti = Column(String(10), nullable=True)
    unvan = Column(String(200), nullable=True)
    
    # İşyeri ve Bölüm
    isyeri = Column(String(200), nullable=True)
    bolum = Column(String(200), nullable=True)
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # SSK ve Meslek
    ssk_no = Column(String(50), nullable=True)
    meslek_adi = Column(String(200), nullable=True)
    meslek_kodu = Column(String(20), nullable=True, index=True)
    
    # Aile Bilgileri
    baba_adi = Column(String(100), nullable=True)
    anne_adi = Column(String(100), nullable=True)
    
    # Doğum Bilgileri
    dogum_yeri = Column(String(100), nullable=True)
    dogum_tarihi = Column(Date, nullable=True)
    
    # Nüfus Bilgileri
    nufus_cuzdani_no = Column(String(20), nullable=True)
    nufusa_kayitli_oldugu_il = Column(String(100), nullable=True)
    nufusa_kayitli_oldugu_ilce = Column(String(100), nullable=True)
    nufusa_kayitli_oldugu_mah = Column(String(200), nullable=True)
    cilt_no = Column(String(20), nullable=True)
    sira_no = Column(String(20), nullable=True)
    kutuk_no = Column(String(20), nullable=True)
    
    # Çalışma Tarihleri
    ise_giris_tarihi = Column(Date, nullable=True)
    isten_cikis_tarihi = Column(Date, nullable=True)
    isten_ayrilis_kodu = Column(String(20), nullable=True)
    isten_ayrilis_nedeni = Column(String(200), nullable=True)
    calisilan_gun = Column(Integer, nullable=True, default=0)
    
    # İletişim ve Adres
    adres = Column(Text, nullable=True)
    telefon = Column(String(50), nullable=True)
    
    # Banka Bilgileri
    banka_sube_adi = Column(String(100), nullable=True)
    hesap_no = Column(String(34), nullable=True)
    
    # Ücret Bilgileri
    ucret = Column(Numeric(18, 2), nullable=True)
    net_brut = Column(String(10), nullable=True)  # 'N' veya 'B'
    
    # Diğer
    kan_grubu = Column(String(5), nullable=True)
    
    # Sistem
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    personnel = relationship("Personnel", foreign_keys=[personnel_id])
    contract = relationship("PersonnelContract", foreign_keys=[contract_id])
    cost_center = relationship("CostCenter", foreign_keys=[cost_center_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('personnel_id', 'donem', 'bolum', name='uq_personnel_donem_bolum'),
        Index('idx_monthly_personnel_donem', 'donem'),
        Index('idx_monthly_personnel_personnel_id', 'personnel_id'),
        Index('idx_monthly_personnel_cost_center', 'cost_center_id'),
        Index('idx_monthly_personnel_tc', 'tc_kimlik_no'),
    )
    
    def __repr__(self):
        return f"<MonthlyPersonnelRecord {self.donem} - Personnel {self.personnel_id} - {self.bolum}>"
    
    @property
    def is_active_in_period(self) -> bool:
        """Dönem içinde aktif mi?"""
        return self.isten_cikis_tarihi is None
