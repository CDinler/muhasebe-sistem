"""Personnel domain schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime, date


# Personnel schemas
class PersonnelBase(BaseModel):
    tc_kimlik_no: str = Field(..., max_length=11, min_length=11)
    ad: str = Field(..., max_length=100)
    soyad: str = Field(..., max_length=100)
    accounts_id: Optional[int] = None
    iban: Optional[str] = Field(None, max_length=34)


class PersonnelCreate(PersonnelBase):
    created_by: Optional[int] = None


class PersonnelUpdate(BaseModel):
    tc_kimlik_no: Optional[str] = Field(None, max_length=11, min_length=11)
    ad: Optional[str] = Field(None, max_length=100)
    soyad: Optional[str] = Field(None, max_length=100)
    accounts_id: Optional[int] = None
    iban: Optional[str] = Field(None, max_length=34)
    updated_by: Optional[int] = None


class PersonnelResponse(PersonnelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class PersonnelList(BaseModel):
    items: list[PersonnelResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)


# PersonnelContract schemas
class PersonnelContractBase(BaseModel):
    personnel_id: int
    tc_kimlik_no: str
    bolum: Optional[str] = None
    ise_giris_tarihi: date
    isten_cikis_tarihi: Optional[date] = None
    is_active: int = 1
    # Moved to personnel_draft_contracts: ucret_nevi, calisma_takvimi, maas2_tutar, maas_hesabi, fm_orani, tatil_orani
    kanun_tipi: str = "K05510_TABI"
    net_brut: Optional[str] = None
    ucret: Optional[float] = None
    iban: Optional[str] = None
    taseron: int = 0
    taseron_id: Optional[int] = None
    departman: Optional[str] = None
    cost_center_id: Optional[int] = None


class PersonnelContractCreate(PersonnelContractBase):
    pass


class PersonnelContractUpdate(BaseModel):
    bolum: Optional[str] = None
    isten_cikis_tarihi: Optional[date] = None
    is_active: Optional[int] = None
    # Removed: ucret_nevi (moved to personnel_draft_contracts)
    maas1_tutar: Optional[float] = None
    cost_center_id: Optional[int] = None


class PersonnelContractResponse(PersonnelContractBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
