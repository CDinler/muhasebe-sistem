"""
PersonnelContract model - Personel sözleşme kayıtları
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLEnum, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UcretNevi(str, enum.Enum):
    """Ücret ödeme şekli"""
    AYLIK = "aylik"
    SABIT_AYLIK = "sabit aylik"
    GUNLUK = "gunluk"


class CalismaTakvimi(str, enum.Enum):
    """Çalışma takvimi tipi"""
    ATIPI = "atipi"  # PAZAR TATİL 08:00-17:00
    BTIPI = "btipi"  # HER GÜN 08:00-17:00
    CTIPI = "ctipi"  # TAKVİM YOK


class MaasHesabi(str, enum.Enum):
    """Maaş hesap tipi"""
    TIPA = "tipa"  # aylık ve maaş2 yok
    TIPB = "tipb"  # sabit aylık ve maaş2 var
    TIPC = "tipc"  # aylık/günlük ve maaş2 var


class Departman(str, enum.Enum):
    """Departman tipleri"""
    ANKRAJ = "Ankraj Ekibi"
    ASFALTLAMA = "Asfaltlama Ekibi"
    BEKCI = "Bekçi Ekibi"
    BETON_KESIM = "Beton Kesim Ekibi"
    DEMIRCI = "Demirci Ekibi"
    DOSEME = "Döşeme Ekibi"
    ELEKTRIKCI = "Elektrikçi Ekibi"
    FORE_KAZIK = "Fore Kazık Ekibi"
    IDARE = "İdare Ekibi"
    KALIPCI = "Kalıpçı Ekibi"
    KALIPCI_KOLON = "Kalıpçı Kolon Ekibi"
    KAYNAKCI = "Kaynakçı Ekibi"
    MERKEZ = "Merkez Ekibi"
    OPERATOR = "Operatör Ekibi"
    SAHA_BETON = "Saha Beton Ekibi"
    STAJYER = "Stajyer Ekibi"
    SOFOR = "Şöför Ekibi"
    YIKIM = "Yıkım Ekibi"


class KanunTipi(str, enum.Enum):
    """SSK kanun tipi"""
    K05510_TABI = "K05510_TABI"
    K05510_DEGIL = "K05510_DEGIL"
    EMEKLI = "EMEKLI"


class PersonnelContract(Base):
    """Personel sözleşme bilgileri (zamana göre değişebilir)"""
    __tablename__ = "personnel_contracts"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey('personnel.id'), nullable=False, index=True)
    tc_kimlik_no = Column(String(11), nullable=False, index=True)
    bolum = Column(String(200), nullable=True)
    monthly_personnel_records_id = Column(Integer, ForeignKey('monthly_personnel_records.id'), nullable=True)
    
    # Tarih aralığı
    ise_giris_tarihi = Column(Date, nullable=False, index=True)
    isten_cikis_tarihi = Column(Date, nullable=True)
    is_active = Column(Integer, default=1)
    
    # Ücret bilgileri
    ucret_nevi = Column(SQLEnum(UcretNevi), nullable=False)
    kanun_tipi = Column(SQLEnum(KanunTipi), default=KanunTipi.K05510_TABI)
    calisma_takvimi = Column(SQLEnum(CalismaTakvimi), nullable=True)
    maas1_tip = Column(String(10), nullable=True)  # NET veya BRÜT
    maas1_tutar = Column(Numeric(18, 2), nullable=True)
    maas2_tutar = Column(Numeric(18, 2), nullable=True)
    maas_hesabi = Column(SQLEnum(MaasHesabi), nullable=True)
    iban = Column(String(34), nullable=True)
    
    # Oranlar
    fm_orani = Column(Numeric(5, 2), default=1)
    tatil_orani = Column(Numeric(5, 2), default=1)
    
    # Taşeron bilgileri
    taseron = Column(Integer, default=0)  # 0: Hayır, 1: Evet
    taseron_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    
    # Departman ve Şantiye
    departman = Column(SQLEnum(Departman), nullable=True)
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id'), nullable=True)
    
    # Sistem
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # İlişkiler
    personnel = relationship("Personnel", back_populates="contracts")
    cost_center = relationship("CostCenter")
    taseron_contact = relationship("Contact", foreign_keys=[taseron_id])

    def __repr__(self):
        return f"<PersonnelContract {self.personnel_id} - {self.ise_giris_tarihi}>"
