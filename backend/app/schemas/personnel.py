"""Personnel Pydantic schemas"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class PersonnelBase(BaseModel):
    """Base Personnel schema - sadece temel kimlik bilgileri"""
    tc_kimlik_no: str = Field(..., max_length=11, min_length=11)
    ad: str = Field(..., max_length=100)
    soyad: str = Field(..., max_length=100)
    accounts_id: Optional[int] = None
    iban: Optional[str] = Field(None, max_length=34)


class PersonnelCreate(PersonnelBase):
    """Personnel creation schema"""
    created_by: Optional[int] = None


class PersonnelUpdate(BaseModel):
    """Personnel update schema"""
    tc_kimlik_no: Optional[str] = Field(None, max_length=11, min_length=11)
    ad: Optional[str] = Field(None, max_length=100)
    soyad: Optional[str] = Field(None, max_length=100)
    accounts_id: Optional[int] = None
    iban: Optional[str] = Field(None, max_length=34)
    updated_by: Optional[int] = None


class PersonnelResponse(PersonnelBase):
    """Personnel response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class PersonnelList(BaseModel):
    """Personnel list response"""
    items: list[PersonnelResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)
