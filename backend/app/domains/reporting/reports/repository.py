"""
Reports Repository
Database operations for financial reports
"""
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from app.crud import reports as reports_crud


class ReportsRepository:
    """Raporlama repository - V1 CRUD fonksiyonlarını wrapper"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_mizan(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ):
        """Mizan raporu"""
        return reports_crud.get_mizan_report(
            self.db,
            start_date,
            end_date,
            cost_center_id
        )
    
    def get_income_statement(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ):
        """Gelir Tablosu"""
        return reports_crud.get_income_statement(
            self.db,
            start_date,
            end_date,
            cost_center_id
        )
    
    def get_debtor_creditor(
        self,
        start_date: date,
        end_date: date,
        cost_center_id: Optional[int] = None
    ):
        """Borç/Alacak raporu"""
        return reports_crud.get_debtor_creditor_report(
            self.db,
            start_date,
            end_date,
            cost_center_id
        )
    
    def get_cari_report(
        self,
        start_date: date,
        end_date: date,
        contact_id: Optional[int] = None,
        cost_center_id: Optional[int] = None
    ):
        """Cari hesap raporu"""
        return reports_crud.get_cari_report(
            self.db,
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
        """Muavin defteri"""
        return reports_crud.get_muavin_report(
            self.db,
            start_date,
            end_date,
            account_code,
            cost_center_id
        )
