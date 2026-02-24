"""Personnel domain models"""
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLEnum, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class Personnel(Base):
    """Personnel model - Personel kartları (sadece temel bilgiler)"""
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
    draft_contracts = relationship("PersonnelDraftContract", back_populates="personnel")
    monthly_records = relationship("MonthlyPersonnelRecord", back_populates="personnel")
    payroll_calculations = relationship("PayrollCalculation", back_populates="personnel", foreign_keys="[PayrollCalculation.personnel_id]")
    transactions = relationship("Transaction", back_populates="personnel")

    def __repr__(self):
        return f"<Personnel {self.tc_kimlik_no} - {self.ad} {self.soyad}>"


# Enums for PersonnelContract
class UcretNevi(str, enum.Enum):
    """Ücret ödeme şekli"""
    AYLIK = "aylik"
    SABIT_AYLIK = "sabit aylik"
    GUNLUK = "gunluk"


class CalismaTakvimi(str, enum.Enum):
    """Çalışma takvimi tipi"""
    ATIPI = "atipi"
    BTIPI = "btipi"
    CTIPI = "ctipi"


class MaasHesabi(str, enum.Enum):
    """Maaş hesap tipi"""
    TIPA = "tipa"
    TIPB = "tipb"
    TIPC = "tipc"


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
    """Personnel contract model"""
    __tablename__ = "personnel_contracts"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey('personnel.id'), nullable=False, index=True)
    personnel_draft_contracts_id = Column(Integer, ForeignKey('personnel_draft_contracts.id'), nullable=True, index=True)
    tc_kimlik_no = Column(String(11), nullable=False, index=True)
    bolum = Column(String(200), nullable=True)
    monthly_personnel_records_id = Column(Integer, ForeignKey('monthly_personnel_records.id'), nullable=True)
    
    # Tarih aralığı
    ise_giris_tarihi = Column(Date, nullable=False, index=True)
    isten_cikis_tarihi = Column(Date, nullable=True)
    is_active = Column(Integer, default=1)
    
    # Ücret bilgileri (taşındı: ucret_nevi, calisma_takvimi, maas2_tutar, maas_hesabi, fm_orani, tatil_orani → personnel_draft_contracts)
    kanun_tipi = Column(String(50), nullable=True)
    net_brut = Column(String(10), nullable=True)
    ucret = Column(Numeric(18, 2), nullable=True)
    iban = Column(String(34), nullable=True)
    
    # Taşeron
    taseron = Column(Integer, default=0)
    taseron_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    
    # Departman
    departman = Column(String(100), nullable=True)
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id'), nullable=True)
    
    # Sistem
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    personnel = relationship("Personnel", back_populates="contracts")
    draft_contract = relationship("PersonnelDraftContract", foreign_keys=[personnel_draft_contracts_id])
    cost_center = relationship("CostCenter", foreign_keys=[cost_center_id])
    taseron_contact = relationship("Contact", foreign_keys=[taseron_id])

    def __repr__(self):
        return f"<PersonnelContract {self.personnel_id} - {self.ise_giris_tarihi}>"
