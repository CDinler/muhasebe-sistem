"""Account Pydantic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional


class AccountBase(BaseModel):
    """Base schema for Account"""
    code: str = Field(..., min_length=1, max_length=50, description="Hesap kodu")
    name: str = Field(..., min_length=1, max_length=200, description="Hesap adı")
    account_type: str = Field(..., description="Hesap türü: asset, liability, revenue, expense")
    description: Optional[str] = Field(None, description="Açıklama")


class AccountCreate(AccountBase):
    """Schema for creating an account"""
    pass


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    account_type: Optional[str] = Field(None)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    """Schema for account response"""
    id: int
    is_active: bool

    class Config:
        from_attributes = True
