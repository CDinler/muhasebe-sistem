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
from .service import ReportsService

router = APIRouter()


@router.get('/mizan', response_model=MizanReport)
def get_mizan_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Mizan (Trial Balance) raporu"""
    service = ReportsService(db)
    return service.get_mizan_report(start_date, end_date, cost_center_id)


@router.get('/income-statement', response_model=IncomeStatement)
def get_income_statement(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Gelir Tablosu (Income Statement)"""
    service = ReportsService(db)
    return service.get_income_statement(start_date, end_date, cost_center_id)


@router.get('/debtor-creditor', response_model=DebtorCreditorReport)
def get_debtor_creditor_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Borç/Alacak raporu"""
    service = ReportsService(db)
    return service.get_debtor_creditor_report(start_date, end_date, cost_center_id)


@router.get('/cari', response_model=CariReport)
def get_cari_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    contact_id: Optional[int] = Query(None, description='Cari ID'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Cari hesap raporu"""
    service = ReportsService(db)
    return service.get_cari_report(start_date, end_date, contact_id, cost_center_id)


@router.get('/muavin', response_model=MuavinReport)
def get_muavin_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    account_code: Optional[str] = Query(None, description='Hesap Kodu'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    db: Session = Depends(get_db)
):
    """Muavin defteri (General Ledger)"""
    service = ReportsService(db)
    return service.get_muavin_report(start_date, end_date, account_code, cost_center_id)
