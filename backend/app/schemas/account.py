"""Account Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional

class AccountBase(BaseModel):
    code: str
    name: str
    account_type: str  # asset, liability, revenue, expense
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class AccountResponse(AccountBase):
    id: int
    
    class Config:
        from_attributes = True
