"""Personnel Contract Pydantic schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class CalismaTakvimi(str, Enum):
    """Çalışma takvimi tipleri"""
    ATIPI = "atipi"
    BTIPI = "btipi"
    CTIPI = "ctipi"


class Departman(str, Enum):
    """Departman tipleri"""
    MUHASEBE = "muhasebe"
    SAHA = "saha"
    INSAN_KAYNAKLARI = "insan_kaynaklari"
    YONETIM = "yonetim"
    TEKNIK = "teknik"
    DEPO = "depo"
    SATIN_ALMA = "satin_alma"
    FINANSMAN = "finansman"
    BT = "bt"
    HUKUK = "hukuk"
    PAZARLAMA = "pazarlama"
    SATIS = "satis"
    KALITE = "kalite"
    AR_GE = "ar_ge"
    PROJE_YONETIMI = "proje_yonetimi"
    MUTEAHHIT = "muteahhit"
    DESTEK_HIZMETLERI = "destek_hizmetleri"
    DIGER = "diger"


class SigortaDurumu(str, Enum):
    """Sigorta durumu"""
    VARDIR = "vardir"
    YOKTUR = "yoktur"
    ASKIDA = "askida"


class MaasHesabi(str, Enum):
    """Maaş hesabı tipleri"""
    TIPA = "tipa"
    TIPB = "tipb"
    TIPC = "tipc"


class PersonnelContractBase(BaseModel):
    """Base Personnel Contract schema"""
    personnel_id: int
    cost_center_id: Optional[int] = None
    contact_id: Optional[int] = None
    tc_kimlik_no: Optional[str] = Field(None, max_length=11)
    bolum: Optional[str] = Field(None, max_length=200)
    monthly_personnel_records_id: Optional[int] = None
    maas_hesabi: Optional[MaasHesabi] = None
    taseron: Optional[bool] = None
    taseron_id: Optional[int] = None
    departman: Optional[Departman] = None
    pozisyon: Optional[str] = Field(None, max_length=200)
    unvan: Optional[str] = Field(None, max_length=200)
    baslangic_tarihi: Optional[date] = None
    bitis_tarihi: Optional[date] = None
    aktif: bool = True
    calisma_takvimi: Optional[CalismaTakvimi] = None
    sigorta_durumu: Optional[SigortaDurumu] = None


class PersonnelContractCreate(PersonnelContractBase):
    """Personnel Contract creation schema"""
    created_by: Optional[int] = None


class PersonnelContractUpdate(BaseModel):
    """Personnel Contract update schema"""
    cost_center_id: Optional[int] = None
    contact_id: Optional[int] = None
    tc_kimlik_no: Optional[str] = Field(None, max_length=11)
    bolum: Optional[str] = Field(None, max_length=200)
    monthly_personnel_records_id: Optional[int] = None
    maas_hesabi: Optional[MaasHesabi] = None
    taseron: Optional[bool] = None
    taseron_id: Optional[int] = None
    departman: Optional[Departman] = None
    pozisyon: Optional[str] = Field(None, max_length=200)
    unvan: Optional[str] = Field(None, max_length=200)
    baslangic_tarihi: Optional[date] = None
    bitis_tarihi: Optional[date] = None
    aktif: Optional[bool] = None
    calisma_takvimi: Optional[CalismaTakvimi] = None
    sigorta_durumu: Optional[SigortaDurumu] = None
    updated_by: Optional[int] = None


class PersonnelContractResponse(PersonnelContractBase):
    """Personnel Contract response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class PersonnelContractList(BaseModel):
    """Personnel Contract list response"""
    items: list[PersonnelContractResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)
