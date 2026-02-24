from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from app.core.database import Base


class MonthlyPersonnelRecord(Base):
    """
    Aylık personel sicil kayıtları.
    Luca Personel Sicil Excel dosyasından yüklenir ve personnel_contracts tablosunu günceller.
    """
    __tablename__ = "monthly_personnel_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=False, index=True)
    donem = Column(String(10), nullable=False, index=True)  # yyyy-mm format
    yil = Column(Integer, nullable=False, index=True)
    ay = Column(Integer, nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("personnel_contracts.id"), nullable=True)
    
    # Personel Bilgileri
    adi = Column(String(100))
    soyadi = Column(String(100))
    cinsiyeti = Column(String(10))
    unvan = Column(String(100))
    isyeri = Column(String(100))
    bolum = Column(String(100))
    ssk_no = Column(String(50))
    tc_kimlik_no = Column(String(11), index=True)
    
    # Aile Bilgileri
    baba_adi = Column(String(100))
    anne_adi = Column(String(100))
    
    # Nüfus Bilgileri
    dogum_yeri = Column(String(100))
    dogum_tarihi = Column(Date)
    nufus_cuzdani_no = Column(String(50))
    nufusa_kayitli_oldugu_il = Column(String(100))
    nufusa_kayitli_oldugu_ilce = Column(String(100))
    nufusa_kayitli_oldugu_mah = Column(String(100))
    cilt_no = Column(String(50))
    sira_no = Column(String(50))
    kutuk_no = Column(String(50))
    
    # İş Bilgileri
    ise_giris_tarihi = Column(Date, nullable=False)
    isten_cikis_tarihi = Column(Date, nullable=True)
    isten_ayrilis_kodu = Column(String(50))
    isten_ayrilis_nedeni = Column(Text)
    
    # İletişim Bilgileri
    adres = Column(Text)
    telefon = Column(String(50))
    
    # Banka Bilgileri
    banka_sube_adi = Column(String(100))
    hesap_no = Column(String(50))
    
    # Ücret Bilgileri
    ucret = Column(DECIMAL(15, 2))
    net_brut = Column(String(10))  # 'net' veya 'brut'
    
    # Diğer
    kan_grubu = Column(String(10))
    meslek_kodu = Column(String(50))
    meslek_adi = Column(String(100))
    
    # Relationships
    personnel = relationship("Personnel", back_populates="monthly_records")
    contract = relationship("PersonnelContract", foreign_keys=[contract_id])
