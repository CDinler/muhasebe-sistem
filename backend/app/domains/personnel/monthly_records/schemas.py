"""Monthly Personnel Records schemas"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from decimal import Decimal


class MonthlyPersonnelRecordBase(BaseModel):
    """Base schema for Monthly Personnel Records"""
    personnel_id: int
    donem: str = Field(..., description="Period in yyyy-mm format")
    yil: int = Field(..., description="Year from donem")
    ay: int = Field(..., description="Month from donem")
    contract_id: Optional[int] = None
    
    # Personel Bilgileri
    adi: Optional[str] = None
    soyadi: Optional[str] = None
    cinsiyeti: Optional[str] = None
    unvan: Optional[str] = None
    isyeri: Optional[str] = None
    bolum: Optional[str] = None
    ssk_no: Optional[str] = None
    tc_kimlik_no: str
    
    # Aile Bilgileri
    baba_adi: Optional[str] = None
    anne_adi: Optional[str] = None
    
    # Nüfus Bilgileri
    dogum_yeri: Optional[str] = None
    dogum_tarihi: Optional[date] = None
    nufus_cuzdani_no: Optional[str] = None
    nufusa_kayitli_oldugu_il: Optional[str] = None
    nufusa_kayitli_oldugu_ilce: Optional[str] = None
    nufusa_kayitli_oldugu_mah: Optional[str] = None
    cilt_no: Optional[str] = None
    sira_no: Optional[str] = None
    kutuk_no: Optional[str] = None
    
    # İş Bilgileri
    ise_giris_tarihi: date
    isten_cikis_tarihi: Optional[date] = None
    isten_ayrilis_kodu: Optional[str] = None
    isten_ayrilis_nedeni: Optional[str] = None
    
    # İletişim Bilgileri
    adres: Optional[str] = None
    telefon: Optional[str] = None
    
    # Banka Bilgileri
    banka_sube_adi: Optional[str] = None
    hesap_no: Optional[str] = None
    
    # Ücret Bilgileri
    ucret: Optional[Decimal] = None
    net_brut: Optional[str] = None  # 'net' veya 'brut'
    
    # Diğer
    kan_grubu: Optional[str] = None
    meslek_kodu: Optional[str] = None
    meslek_adi: Optional[str] = None


class MonthlyPersonnelRecordCreate(MonthlyPersonnelRecordBase):
    """Schema for creating Monthly Personnel Record"""
    pass


class MonthlyPersonnelRecordUpdate(BaseModel):
    """Schema for updating Monthly Personnel Record"""
    personnel_id: Optional[int] = None
    donem: Optional[str] = None
    contract_id: Optional[int] = None
    
    # Personel Bilgileri
    adi: Optional[str] = None
    soyadi: Optional[str] = None
    cinsiyeti: Optional[str] = None
    unvan: Optional[str] = None
    isyeri: Optional[str] = None
    bolum: Optional[str] = None
    ssk_no: Optional[str] = None
    tc_kimlik_no: Optional[str] = None
    
    # Aile Bilgileri
    baba_adi: Optional[str] = None
    anne_adi: Optional[str] = None
    
    # Nüfus Bilgileri
    dogum_yeri: Optional[str] = None
    dogum_tarihi: Optional[date] = None
    nufus_cuzdani_no: Optional[str] = None
    nufusa_kayitli_oldugu_il: Optional[str] = None
    nufusa_kayitli_oldugu_ilce: Optional[str] = None
    nufusa_kayitli_oldugu_mah: Optional[str] = None
    cilt_no: Optional[str] = None
    sira_no: Optional[str] = None
    kutuk_no: Optional[str] = None
    
    # İş Bilgileri
    ise_giris_tarihi: Optional[date] = None
    isten_cikis_tarihi: Optional[date] = None
    isten_ayrilis_kodu: Optional[str] = None
    isten_ayrilis_nedeni: Optional[str] = None
    
    # İletişim Bilgileri
    adres: Optional[str] = None
    telefon: Optional[str] = None
    
    # Banka Bilgileri
    banka_sube_adi: Optional[str] = None
    hesap_no: Optional[str] = None
    
    # Ücret Bilgileri
    ucret: Optional[Decimal] = None
    net_brut: Optional[str] = None
    
    # Diğer
    kan_grubu: Optional[str] = None
    meslek_kodu: Optional[str] = None
    meslek_adi: Optional[str] = None


class MonthlyPersonnelRecord(MonthlyPersonnelRecordBase):
    """Schema for Monthly Personnel Record response"""
    id: int
    
    class Config:
        from_attributes = True


class MonthlyPersonnelRecordList(BaseModel):
    """List of Monthly Personnel Records with pagination"""
    items: list[MonthlyPersonnelRecord]
    total: int
    page: int
    page_size: int
