"""Luca Bordro Pydantic schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class LucaBordroBase(BaseModel):
    """Base Luca Bordro schema - Luca'dan gelen bordro verileri"""
    donem: date
    personnel_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    
    # Kimlik bilgileri
    tc: Optional[str] = Field(None, max_length=11)
    adi: Optional[str] = Field(None, max_length=100)
    soyadi: Optional[str] = Field(None, max_length=100)
    
    # Tarih bilgileri (kısa isimlerle)
    giris_t: Optional[date] = None  # ise_giris_tarihi
    cikis_t: Optional[date] = None  # isten_cikis_tarihi
    
    # Gün sayıları
    t_gun: Optional[int] = None  # toplam_gun
    ucretli_izin_gun: Optional[int] = None
    ucretsiz_izin_gun: Optional[int] = None
    
    # Kazançlar (kısa isimlerle)
    nor_kazanc: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # normal_kazanc
    dig_kazanc: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # diger_kazanc
    fazla_mes: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # fazla_mesai
    t_kazanc: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # toplam_kazanc
    
    # Kesintiler (kısa isimlerle)
    sgk_iscisi: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # sgk_isci_payi
    issiz_iscisi: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # issizlik_isci_payi
    gel_ver: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # gelir_vergisi
    damga_v: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # damga_vergisi
    t_kesinti: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # toplam_kesinti
    
    # Net ödeme
    net_ucret: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    
    # İşveren yükümlülükleri (kısa isimlerle)
    sgk_isveren: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # sgk_isveren_payi
    issiz_isveren: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # issizlik_isveren_payi
    
    # Toplam maliyet
    t_isveren_maliyet: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)  # toplam_isveren_maliyet
    
    # Ham veri
    luca_data: Optional[str] = None  # JSON text


class LucaBordroCreate(LucaBordroBase):
    """Luca Bordro creation schema"""
    created_by: Optional[int] = None


class LucaBordroUpdate(BaseModel):
    """Luca Bordro update schema"""
    personnel_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    tc: Optional[str] = Field(None, max_length=11)
    adi: Optional[str] = Field(None, max_length=100)
    soyadi: Optional[str] = Field(None, max_length=100)
    giris_t: Optional[date] = None
    cikis_t: Optional[date] = None
    t_gun: Optional[int] = None
    ucretli_izin_gun: Optional[int] = None
    ucretsiz_izin_gun: Optional[int] = None
    nor_kazanc: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    dig_kazanc: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    fazla_mes: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    t_kazanc: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    sgk_iscisi: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    issiz_iscisi: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    gel_ver: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    damga_v: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    t_kesinti: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    net_ucret: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    sgk_isveren: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    issiz_isveren: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    t_isveren_maliyet: Optional[Decimal] = Field(None, max_digits=15, decimal_places=2)
    luca_data: Optional[str] = None
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
