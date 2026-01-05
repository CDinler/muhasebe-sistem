"""
Reports Service
Business logic for financial reports
"""
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from .repository import ReportsRepository


class ReportsService:
    """Raporlama business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportsRepository(db)
    
    def get_mizan_report(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ):
        """Mizan (Trial Balance) raporu"""
        return self.repo.get_mizan(start_date, end_date, cost_center_id)
    
    def get_income_statement(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ):
        """Gelir Tablosu (Income Statement)"""
        return self.repo.get_income_statement(start_date, end_date, cost_center_id)
    
    def get_debtor_creditor_report(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ):
        """Borç/Alacak raporu"""
        return self.repo.get_debtor_creditor(start_date, end_date, cost_center_id)
    
    def get_cari_report(
        self,
        start_date: date,
        end_date: date,
        contact_id: Optional[int] = None,
        cost_center_id: Optional[int] = None
    ):
        """Cari hesap raporu"""
        return self.repo.get_cari_report(
            start_date,
            end_date,
            contact_id,
            cost_center_id
        )
    
    def get_muavin_report(
        self,
        start_date: date,
        end_date: date,
        account_code: Optional[str] = None,
        cost_center_id: Optional[int] = None
    ):
        """Muavin defteri (General Ledger)"""
        return self.repo.get_muavin_report(
            start_date,
            end_date,
            account_code,
            cost_center_id
        )
