"""Personnel Contract Pydantic schemas - Sadece resmi sözleşme bilgileri
NOT: Taslak sözleşme bilgileri (ucret_nevi, fm_orani, tatil_orani, vb.) 
     personnel_draft_contracts tablosundadır.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class Departman(str, Enum):
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


class KanunTipi(str, Enum):
    """SSK kanun tipi"""
    K05510_TABI = "K05510_TABI"
    K05510_DEGIL = "K05510_DEGIL"
    EMEKLI = "EMEKLI"


class PersonnelContractBase(BaseModel):
    """Base Personnel Contract schema - Resmi sözleşme bilgileri"""
    personnel_id: int
    tc_kimlik_no: Optional[str] = None  # personnel tablosundan otomatik
    
    # Resmi sözleşme bilgileri
    bolum: Optional[str] = None
    ise_giris_tarihi: Optional[date] = None
    isten_cikis_tarihi: Optional[date] = None
    kanun_tipi: Optional[str] = None
    net_brut: Optional[str] = None
    ucret: Optional[Decimal] = None
    iban: Optional[str] = None  # personnel tablosundan otomatik
    
    # İlişkili kayıtlar
    taseron: Optional[int] = 0
    taseron_id: Optional[int] = None
    departman: Optional[str] = None
    cost_center_id: Optional[int] = None
    monthly_personnel_records_id: Optional[int] = None
    is_active: Optional[int] = 1
    
    # NOT: Taslak sözleşme bilgileri personnel_draft_contracts tablosunda
    # ucret_nevi, maas2_tutar, fm_orani, tatil_orani, calisma_takvimi, maas_hesabi


class PersonnelContractCreate(PersonnelContractBase):
    """Personnel Contract creation schema"""
    created_by: Optional[int] = None


class PersonnelContractUpdate(BaseModel):
    """Personnel Contract update schema - Sadece resmi sözleşme bilgileri"""
    personnel_id: Optional[int] = None
    tc_kimlik_no: Optional[str] = None
    bolum: Optional[str] = None
    monthly_personnel_records_id: Optional[int] = None
    ise_giris_tarihi: Optional[date] = None
    isten_cikis_tarihi: Optional[date] = None
    is_active: Optional[int] = None
    kanun_tipi: Optional[str] = None
    net_brut: Optional[str] = None
    ucret: Optional[Decimal] = None
    iban: Optional[str] = None
    taseron: Optional[int] = None
    taseron_id: Optional[int] = None
    departman: Optional[str] = None
    cost_center_id: Optional[int] = None
    updated_by: Optional[int] = None
    # NOT: Taslak sözleşme bilgileri personnel_draft_contracts'tan güncellenir


class PersonnelContractResponse(PersonnelContractBase):
    """Personnel Contract response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    # İlişkili veriler
    personnel_ad: Optional[str] = None
    personnel_soyad: Optional[str] = None
    cost_center_name: Optional[str] = None
    taseron_name: Optional[str] = None
    meslek_adi: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class PersonnelContractList(BaseModel):
    """Personnel Contract list response"""
    items: list[PersonnelContractResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)
