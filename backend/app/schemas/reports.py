# -*- coding: utf-8 -*-
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from decimal import Decimal


class MizanItem(BaseModel):
    account_code: str
    account_name: str
    opening_debit: Decimal
    opening_credit: Decimal
    period_debit: Decimal
    period_credit: Decimal
    closing_debit: Decimal
    closing_credit: Decimal


class MizanReport(BaseModel):
    start_date: date
    end_date: date
    items: List[MizanItem]
    total_opening_debit: Decimal
    total_opening_credit: Decimal
    total_period_debit: Decimal
    total_period_credit: Decimal
    total_closing_debit: Decimal
    total_closing_credit: Decimal


class IncomeStatementItem(BaseModel):
    account_code: str
    account_name: str
    amount: Decimal


class IncomeStatement(BaseModel):
    start_date: date
    end_date: date
    income_items: List[IncomeStatementItem]
    expense_items: List[IncomeStatementItem]
    total_income: Decimal
    total_expense: Decimal
    net_profit: Decimal


class DebtorCreditorItem(BaseModel):
    contact_id: int
    contact_name: str
    tax_number: Optional[str]
    debit: Decimal
    credit: Decimal
    balance: Decimal


class DebtorCreditorReport(BaseModel):
    start_date: date
    end_date: date
    debtors: List[DebtorCreditorItem]
    creditors: List[DebtorCreditorItem]
    total_debtors: Decimal
    total_creditors: Decimal
    net_balance: Decimal


class CariReportItem(BaseModel):
    """Cari raporu fiş satırı - her transaction için bir satır"""
    transaction_id: int
    transaction_number: str
    transaction_date: date
    due_date: Optional[date]  # Vade tarihi
    document_type: Optional[str]  # Evrak türü (Gelen Havale, İhracat Faturası, vs)
    description: Optional[str]
    account_code: str  # 120.xxx veya 320.xxx
    account_name: str
    account_type: str  # 'customer' veya 'supplier'
    currency: Optional[str]  # Döviz cinsi
    currency_debit: Optional[Decimal]  # Döviz borç
    currency_credit: Optional[Decimal]  # Döviz alacak
    currency_balance: Optional[Decimal]  # Döviz bakiye
    debit: Decimal  # TL Borç
    credit: Decimal  # TL Alacak
    balance: Decimal  # TL Kümülatif bakiye


class CariReport(BaseModel):
    """Cari Raporu - 120 ve 320 birleşik fiş fiş"""
    contact_id: Optional[int]
    contact_code: Optional[str]
    contact_name: str
    tax_number: Optional[str]
    start_date: date
    end_date: date
    opening_balance: Decimal
    items: List[CariReportItem]
    closing_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal


class MuavinItem(BaseModel):
    """Muavin defteri satırı - belirli hesap kodunun işlemleri"""
    transaction_id: int
    transaction_number: str
    transaction_date: date
    description: Optional[str]
    debit: Decimal
    credit: Decimal
    balance: Decimal  # Kümülatif bakiye


class MuavinReport(BaseModel):
    """Muavin Defteri - Belirli bir hesap kodunun tüm işlemleri"""
    account_code: str
    account_name: str
    start_date: date
    end_date: date
    opening_balance: Decimal
    items: List[MuavinItem]
    closing_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
