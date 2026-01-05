"""Transaction Pydantic schemas"""
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

# Transaction schemas
class TransactionBase(BaseModel):
    transaction_number: str
    transaction_date: date
    accounting_period: str
    cost_center_id: Optional[int] = None
    description: Optional[str] = None
    document_type: Optional[str] = None
    document_subtype: Optional[str] = None
    document_number: Optional[str] = None
    related_invoice_number: Optional[str] = None

class TransactionCreate(TransactionBase):
    lines: List[TransactionLineCreate] = []

class TransactionResponse(TransactionBase):
    id: int
    document_type_id: Optional[int] = None
    document_subtype_id: Optional[int] = None  
    lines: List[TransactionLineResponse] = []

    model_config = ConfigDict(from_attributes=True)
