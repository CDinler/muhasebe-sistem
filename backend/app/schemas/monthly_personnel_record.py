"""Monthly Personnel Record Pydantic schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class MonthlyPersonnelRecordBase(BaseModel):
    """Base Monthly Personnel Record schema - Luca'dan gelen aylık sicil kayıtları"""
    personnel_id: int
    donem: date
    cost_center_id: Optional[int] = None
    contract_id: Optional[int] = None
    
    # Dönem bilgisi
    yil: Optional[int] = None
    ay: Optional[int] = None
    
    # Kimlik ve temel bilgiler
    adi: Optional[str] = Field(None, max_length=100)
    soyadi: Optional[str] = Field(None, max_length=100)
    tc_kimlik_no: Optional[str] = Field(None, max_length=11)
    cinsiyeti: Optional[str] = Field(None, max_length=10)
    
    # İş bilgileri
    unvan: Optional[str] = Field(None, max_length=200)
    isyeri: Optional[str] = Field(None, max_length=200)
    bolum: Optional[str] = Field(None, max_length=200)
    
    # SSK ve Meslek
    ssk_no: Optional[str] = Field(None, max_length=50)
    meslek_adi: Optional[str] = Field(None, max_length=200)
    meslek_kodu: Optional[str] = Field(None, max_length=20)
    
    # Aile bilgileri
    baba_adi: Optional[str] = Field(None, max_length=100)
    anne_adi: Optional[str] = Field(None, max_length=100)
    
    # Doğum bilgileri
    dogum_yeri: Optional[str] = Field(None, max_length=100)
    dogum_tarihi: Optional[date] = None
    
    # Nüfus bilgileri
    nufus_cuzdani_no: Optional[str] = Field(None, max_length=20)
    nufusa_kayitli_oldugu_il: Optional[str] = Field(None, max_length=100)
    nufusa_kayitli_oldugu_ilce: Optional[str] = Field(None, max_length=100)
    nufusa_kayitli_oldugu_mah: Optional[str] = Field(None, max_length=200)
    cilt_no: Optional[str] = Field(None, max_length=20)
    sira_no: Optional[str] = Field(None, max_length=20)
    kutuk_no: Optional[str] = Field(None, max_length=20)
    
    # Çalışma tarihleri
    ise_giris_tarihi: Optional[date] = None
    isten_cikis_tarihi: Optional[date] = None
    isten_ayrilis_kodu: Optional[str] = Field(None, max_length=20)
    isten_ayrilis_nedeni: Optional[str] = Field(None, max_length=200)
    
    # İletişim bilgileri
    adres: Optional[str] = None
    telefon: Optional[str] = Field(None, max_length=50)
    
    # Banka bilgileri
    banka_sube_adi: Optional[str] = Field(None, max_length=100)
    hesap_no: Optional[str] = Field(None, max_length=34)
    
    # Ücret bilgileri
    ucret: Optional[Decimal] = None
    net_brut: Optional[str] = Field(None, max_length=10)
    
    # Diğer
    kan_grubu: Optional[str] = Field(None, max_length=5)


class MonthlyPersonnelRecordCreate(MonthlyPersonnelRecordBase):
    """Monthly Personnel Record creation schema"""
    created_by: Optional[int] = None


class MonthlyPersonnelRecordUpdate(BaseModel):
    """Monthly Personnel Record update schema"""
    cost_center_id: Optional[int] = None
    contract_id: Optional[int] = None
    yil: Optional[int] = None
    ay: Optional[int] = None
    adi: Optional[str] = Field(None, max_length=100)
    soyadi: Optional[str] = Field(None, max_length=100)
    tc_kimlik_no: Optional[str] = Field(None, max_length=11)
    cinsiyeti: Optional[str] = Field(None, max_length=10)
    unvan: Optional[str] = Field(None, max_length=200)
    isyeri: Optional[str] = Field(None, max_length=200)
    bolum: Optional[str] = Field(None, max_length=200)
    ssk_no: Optional[str] = Field(None, max_length=50)
    meslek_adi: Optional[str] = Field(None, max_length=200)
    meslek_kodu: Optional[str] = Field(None, max_length=20)
    baba_adi: Optional[str] = Field(None, max_length=100)
    anne_adi: Optional[str] = Field(None, max_length=100)
    dogum_yeri: Optional[str] = Field(None, max_length=100)
    dogum_tarihi: Optional[date] = None
    nufus_cuzdani_no: Optional[str] = Field(None, max_length=20)
    nufusa_kayitli_oldugu_il: Optional[str] = Field(None, max_length=100)
    nufusa_kayitli_oldugu_ilce: Optional[str] = Field(None, max_length=100)
    nufusa_kayitli_oldugu_mah: Optional[str] = Field(None, max_length=200)
    cilt_no: Optional[str] = Field(None, max_length=20)
    sira_no: Optional[str] = Field(None, max_length=20)
    kutuk_no: Optional[str] = Field(None, max_length=20)
    ise_giris_tarihi: Optional[date] = None
    isten_cikis_tarihi: Optional[date] = None
    isten_ayrilis_kodu: Optional[str] = Field(None, max_length=20)
    isten_ayrilis_nedeni: Optional[str] = Field(None, max_length=200)
    adres: Optional[str] = None
    telefon: Optional[str] = Field(None, max_length=50)
    banka_sube_adi: Optional[str] = Field(None, max_length=100)
    hesap_no: Optional[str] = Field(None, max_length=34)
    ucret: Optional[Decimal] = None
    net_brut: Optional[str] = Field(None, max_length=10)
    kan_grubu: Optional[str] = Field(None, max_length=5)
    updated_by: Optional[int] = None


class MonthlyPersonnelRecordResponse(MonthlyPersonnelRecordBase):
    """Monthly Personnel Record response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class MonthlyPersonnelRecordList(BaseModel):
    """Monthly Personnel Record list response"""
    items: list[MonthlyPersonnelRecordResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)
