"""Luca Bordro Pydantic schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class LucaBordroBase(BaseModel):
    """Base Luca Bordro schema - Luca'dan gelen bordro verileri"""
    
    # Dönem bilgisi
    yil: Optional[int] = None
    ay: Optional[int] = None
    donem: Optional[str] = None  # "2025-11" formatında
    
    # Personel bilgileri
    sira_no: Optional[int] = None
    adi_soyadi: Optional[str] = None
    tckn: Optional[str] = Field(None, max_length=11)
    ssk_sicil_no: Optional[str] = Field(None, max_length=20)
    
    # Tarih bilgileri
    giris_t: Optional[date] = None
    cikis_t: Optional[date] = None
    
    # Çalışma günü
    t_gun: Optional[int] = None
    
    # Kazançlar
    nor_kazanc: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    dig_kazanc: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    top_kazanc: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    ssk_m: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)  # SSK Matrahı
    g_v_m: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)  # Gelir Vergisi Matrahı
    
    # Kesintiler (İşçi payları)
    ssk_isci: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    iss_p_isci: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    gel_ver: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    damga_v: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    
    # Özel kesintiler
    ozel_kesinti: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    oto_kat_bes: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    icra: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    avans: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    
    # Net ödenen
    n_odenen: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    
    # İşveren payları
    isveren_maliyeti: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    ssk_isveren: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    iss_p_isveren: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    
    # Kanun ve teşvik
    kanun: Optional[str] = Field(None, max_length=10)
    ssk_tesviki: Optional[Decimal] = Field(None, max_digits=18, decimal_places=2)
    
    # Upload bilgisi
    upload_date: Optional[datetime] = None
    file_name: Optional[str] = Field(None, max_length=500)
    
    # İşlem durumu
    is_processed: Optional[int] = None
    contract_id: Optional[int] = None


class LucaBordroCreate(LucaBordroBase):
    """Luca Bordro creation schema"""
    created_by: Optional[int] = None


class LucaBordroUpdate(BaseModel):
    """Luca Bordro update schema"""
    yil: Optional[int] = None
    ay: Optional[int] = None
    donem: Optional[str] = None
    sira_no: Optional[int] = None
    adi_soyadi: Optional[str] = None
    tckn: Optional[str] = None
    ssk_sicil_no: Optional[str] = None
    giris_t: Optional[date] = None
    cikis_t: Optional[date] = None
    t_gun: Optional[int] = None
    nor_kazanc: Optional[Decimal] = None
    dig_kazanc: Optional[Decimal] = None
    top_kazanc: Optional[Decimal] = None
    ssk_m: Optional[Decimal] = None
    g_v_m: Optional[Decimal] = None
    ssk_isci: Optional[Decimal] = None
    iss_p_isci: Optional[Decimal] = None
    gel_ver: Optional[Decimal] = None
    damga_v: Optional[Decimal] = None
    ozel_kesinti: Optional[Decimal] = None
    oto_kat_bes: Optional[Decimal] = None
    icra: Optional[Decimal] = None
    avans: Optional[Decimal] = None
    n_odenen: Optional[Decimal] = None
    isveren_maliyeti: Optional[Decimal] = None
    ssk_isveren: Optional[Decimal] = None
    iss_p_isveren: Optional[Decimal] = None
    kanun: Optional[str] = None
    ssk_tesviki: Optional[Decimal] = None
    file_name: Optional[str] = None
    is_processed: Optional[int] = None
    contract_id: Optional[int] = None
    updated_by: Optional[int] = None


class LucaBordroResponse(LucaBordroBase):
    """Luca Bordro response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class LucaBordroList(BaseModel):
    """Luca Bordro list response"""
    items: list[LucaBordroResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)
