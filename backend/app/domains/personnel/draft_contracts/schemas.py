"""
PersonnelDraftContract Schema
Personel taslak sözleşme şemaları
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


class UcretNeviEnum(str, Enum):
    """Ücret ödeme şekli"""
    AYLIK = "aylik"
    SABIT_AYLIK = "sabit aylik"
    GUNLUK = "gunluk"


class CalismaTakvimiEnum(str, Enum):
    """Çalışma takvimi tipi"""
    ATIPI = "atipi"
    BTIPI = "btipi"
    CTIPI = "ctipi"


class PersonnelMinimal(BaseModel):
    """Minimal personnel info for nested responses"""
    id: int
    ad: Optional[str] = None
    soyad: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class CostCenterMinimal(BaseModel):
    """Minimal cost center info for nested responses"""
    id: int
    cost_center_code: Optional[str] = None
    cost_center_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class PersonnelDraftContractBase(BaseModel):
    """Base schema for PersonnelDraftContract"""
    personnel_id: int
    tc_kimlik_no: Optional[str] = None
    ucret_nevi: UcretNeviEnum
    net_ucret: Optional[Decimal] = None
    fm_orani: Decimal = Field(default=Decimal("1.00"))
    tatil_orani: Decimal = Field(default=Decimal("1.00"))
    cost_center_id: Optional[int] = None
    calisma_takvimi: Optional[CalismaTakvimiEnum] = None
    is_active: int = 1


class PersonnelDraftContractCreate(PersonnelDraftContractBase):
    """Schema for creating PersonnelDraftContract"""
    created_by: Optional[int] = None


class PersonnelDraftContractUpdate(BaseModel):
    """Schema for updating PersonnelDraftContract"""
    personnel_id: Optional[int] = None
    tc_kimlik_no: Optional[str] = None
    ucret_nevi: Optional[UcretNeviEnum] = None
    net_ucret: Optional[Decimal] = None
    fm_orani: Optional[Decimal] = None
    tatil_orani: Optional[Decimal] = None
    cost_center_id: Optional[int] = None
    calisma_takvimi: Optional[CalismaTakvimiEnum] = None
    is_active: Optional[int] = None
    updated_by: Optional[int] = None


class PersonnelDraftContractResponse(PersonnelDraftContractBase):
    """Schema for PersonnelDraftContract response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    personnel: Optional[PersonnelMinimal] = None
    cost_center: Optional[CostCenterMinimal] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v) if v is not None else None
        }
    )


class PersonnelDraftContractInDB(PersonnelDraftContractResponse):
    """Schema for PersonnelDraftContract in database"""
    pass
