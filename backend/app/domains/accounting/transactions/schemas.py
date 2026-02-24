"""Transaction domain schemas - Migrated from app.schemas.transaction"""
from pydantic import BaseModel, ConfigDict, computed_field
from typing import List, Optional, Any
from datetime import date
from decimal import Decimal


# Transaction Line schemas
class TransactionLineBase(BaseModel):
    account_id: int
    contact_id: Optional[int] = None
    description: Optional[str] = None
    debit: Optional[Decimal] = None
    credit: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    vat_rate: Optional[Decimal] = None  # KDV Oranı (%1=0.01, %10=0.10, %20=0.20)
    withholding_rate: Optional[Decimal] = None  # Tevkifat Oranı (4/10=0.40, 9/10=0.90)
    vat_base: Optional[Decimal] = None  # KDV Matrahı


class TransactionLineCreate(TransactionLineBase):
    pass


class TransactionLineResponse(TransactionLineBase):
    id: int
    transaction_id: int

    @computed_field
    @property
    def account_code(self) -> Optional[str]:
        return getattr(self, '_account_code', None) or (self.account.code if hasattr(self, 'account') and self.account else None)
    
    @computed_field
    @property
    def account_name(self) -> Optional[str]:
        return getattr(self, '_account_name', None) or (self.account.name if hasattr(self, 'account') and self.account else None)

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# Transaction schemas
class TransactionBase(BaseModel):
    transaction_number: str
    transaction_date: date
    accounting_period: str
    cost_center_id: Optional[int] = None
    personnel_id: Optional[int] = None
    description: Optional[str] = None
    document_type_id: Optional[int] = None
    document_number: Optional[str] = None
    related_invoice_number: Optional[str] = None
    draft: Optional[bool] = False


class TransactionCreate(TransactionBase):
    lines: List[TransactionLineCreate] = []


class TransactionResponse(TransactionBase):
    id: int
    
    @computed_field
    @property
    def document_type(self) -> Optional[str]:
        """Evrak türü adı (read-only computed field)"""
        return getattr(self, '_document_type', None)
    
    lines: List[TransactionLineResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    """Transaction list response with pagination"""
    items: List[TransactionResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    'TransactionLineBase',
    'TransactionLineCreate',
    'TransactionLineResponse',
    'TransactionBase',
    'TransactionCreate',
    'TransactionResponse',
    'TransactionListResponse',
]
