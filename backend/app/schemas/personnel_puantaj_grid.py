"""Personnel Puantaj Grid Pydantic schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class PuantajGunBase(BaseModel):
    """Puantaj grid için tek gün verisi"""
    gun: int  # 1-31
    durum: Optional[str] = Field(None, max_length=10)  # C, T, R, I, vs


class PersonnelPuantajGridBase(BaseModel):
    """Base Personnel Puantaj Grid schema - 31 günlük çalışma grid'i"""
    personnel_id: int
    contract_id: Optional[int] = None
    donem: date  # YYYY-MM-DD format
    cost_center_id: Optional[int] = None
    
    # Ay bilgisi
    ayin_toplam_gun_sayisi: Optional[int] = None
    
    # 31 günlük grid (gun_1, gun_2, ..., gun_31)
    gun_1: Optional[str] = Field(None, max_length=10)
    gun_2: Optional[str] = Field(None, max_length=10)
    gun_3: Optional[str] = Field(None, max_length=10)
    gun_4: Optional[str] = Field(None, max_length=10)
    gun_5: Optional[str] = Field(None, max_length=10)
    gun_6: Optional[str] = Field(None, max_length=10)
    gun_7: Optional[str] = Field(None, max_length=10)
    gun_8: Optional[str] = Field(None, max_length=10)
    gun_9: Optional[str] = Field(None, max_length=10)
    gun_10: Optional[str] = Field(None, max_length=10)
    gun_11: Optional[str] = Field(None, max_length=10)
    gun_12: Optional[str] = Field(None, max_length=10)
    gun_13: Optional[str] = Field(None, max_length=10)
    gun_14: Optional[str] = Field(None, max_length=10)
    gun_15: Optional[str] = Field(None, max_length=10)
    gun_16: Optional[str] = Field(None, max_length=10)
    gun_17: Optional[str] = Field(None, max_length=10)
    gun_18: Optional[str] = Field(None, max_length=10)
    gun_19: Optional[str] = Field(None, max_length=10)
    gun_20: Optional[str] = Field(None, max_length=10)
    gun_21: Optional[str] = Field(None, max_length=10)
    gun_22: Optional[str] = Field(None, max_length=10)
    gun_23: Optional[str] = Field(None, max_length=10)
    gun_24: Optional[str] = Field(None, max_length=10)
    gun_25: Optional[str] = Field(None, max_length=10)
    gun_26: Optional[str] = Field(None, max_length=10)
    gun_27: Optional[str] = Field(None, max_length=10)
    gun_28: Optional[str] = Field(None, max_length=10)
    gun_29: Optional[str] = Field(None, max_length=10)
    gun_30: Optional[str] = Field(None, max_length=10)
    gun_31: Optional[str] = Field(None, max_length=10)
    
    # Hesaplama alanları
    normal_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    fazla_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    gece_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    tatil_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    sigorta_girmedigi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    
    # Ödeme kalemleri
    yol: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    prim: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    ikramiye: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    bayram: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    kira: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    
    # Notlar
    notlar: Optional[str] = None


class PersonnelPuantajGridCreate(PersonnelPuantajGridBase):
    """Personnel Puantaj Grid creation schema"""
    created_by: Optional[int] = None


class PersonnelPuantajGridUpdate(BaseModel):
    """Personnel Puantaj Grid update schema"""
    contract_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    ayin_toplam_gun_sayisi: Optional[int] = None
    gun_1: Optional[str] = Field(None, max_length=10)
    gun_2: Optional[str] = Field(None, max_length=10)
    gun_3: Optional[str] = Field(None, max_length=10)
    gun_4: Optional[str] = Field(None, max_length=10)
    gun_5: Optional[str] = Field(None, max_length=10)
    gun_6: Optional[str] = Field(None, max_length=10)
    gun_7: Optional[str] = Field(None, max_length=10)
    gun_8: Optional[str] = Field(None, max_length=10)
    gun_9: Optional[str] = Field(None, max_length=10)
    gun_10: Optional[str] = Field(None, max_length=10)
    gun_11: Optional[str] = Field(None, max_length=10)
    gun_12: Optional[str] = Field(None, max_length=10)
    gun_13: Optional[str] = Field(None, max_length=10)
    gun_14: Optional[str] = Field(None, max_length=10)
    gun_15: Optional[str] = Field(None, max_length=10)
    gun_16: Optional[str] = Field(None, max_length=10)
    gun_17: Optional[str] = Field(None, max_length=10)
    gun_18: Optional[str] = Field(None, max_length=10)
    gun_19: Optional[str] = Field(None, max_length=10)
    gun_20: Optional[str] = Field(None, max_length=10)
    gun_21: Optional[str] = Field(None, max_length=10)
    gun_22: Optional[str] = Field(None, max_length=10)
    gun_23: Optional[str] = Field(None, max_length=10)
    gun_24: Optional[str] = Field(None, max_length=10)
    gun_25: Optional[str] = Field(None, max_length=10)
    gun_26: Optional[str] = Field(None, max_length=10)
    gun_27: Optional[str] = Field(None, max_length=10)
    gun_28: Optional[str] = Field(None, max_length=10)
    gun_29: Optional[str] = Field(None, max_length=10)
    gun_30: Optional[str] = Field(None, max_length=10)
    gun_31: Optional[str] = Field(None, max_length=10)
    normal_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    fazla_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    gece_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    tatil_calismasi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    sigorta_girmedigi: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    yol: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    prim: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    ikramiye: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    bayram: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    kira: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    notlar: Optional[str] = None
    updated_by: Optional[int] = None


class PersonnelPuantajGridResponse(PersonnelPuantajGridBase):
    """Personnel Puantaj Grid response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class PersonnelPuantajGridList(BaseModel):
    """Personnel Puantaj Grid list response"""
    items: list[PersonnelPuantajGridResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)
