"""Cost Center Pydantic schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CostCenterBase(BaseModel):
    code: str
    name: str
    bolum_adi: Optional[str] = None
    is_active: bool = True

class CostCenterCreate(CostCenterBase):
    created_by: Optional[int] = None

class CostCenterUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    bolum_adi: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[int] = None

class CostCenterResponse(CostCenterBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
