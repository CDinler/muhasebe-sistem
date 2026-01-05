"""
Reports Router
FastAPI endpoints for financial reports
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.schemas.reports import (
    MizanReport,
    IncomeStatement,
    DebtorCreditorReport,
    CariReport,
    MuavinReport
)
# 🔄 Use V1 CRUD functions (already working)
from app.crud import reports as reports_crud

router = APIRouter()


@router.get('/mizan', response_model=MizanReport)
def get_mizan_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Mizan (Trial Balance) raporu"""
    # V1 CRUD doesn't support cost_center_id yet, ignore it for now
    return reports_crud.get_mizan_report(db, start_date, end_date)


@router.get('/income-statement', response_model=IncomeStatement)
def get_income_statement(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Gelir Tablosu (Income Statement)"""
    return reports_crud.get_income_statement(db, start_date, end_date)


@router.get('/debtor-creditor', response_model=DebtorCreditorReport)
def get_debtor_creditor_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Borç/Alacak raporu"""
    return reports_crud.get_debtor_creditor_report(db, start_date, end_date)


@router.get('/cari', response_model=CariReport)
def get_cari_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    contact_id: Optional[int] = Query(None, description='Cari ID'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Cari hesap raporu"""
    return reports_crud.get_cari_report(db, start_date, end_date, contact_id)


@router.get('/muavin', response_model=MuavinReport)
def get_muavin_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    account_code: Optional[str] = Query(None, description='Hesap Kodu'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Muavin defteri (General Ledger)"""
    return reports_crud.get_muavin_report(db, start_date, end_date, account_code)
