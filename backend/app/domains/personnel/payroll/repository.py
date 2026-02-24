"""
Payroll Repository
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import PayrollCalculation
from app.models import LucaBordro
from app.models import MonthlyPuantaj


class PayrollRepository:
    """Bordro hesaplama repository"""
    
    def get_by_period(self, db: Session, yil: int, ay: int) -> List[PayrollCalculation]:
        """Döneme göre bordro kayıtlarını getir"""
        return db.query(PayrollCalculation).filter(
            PayrollCalculation.yil == yil,
            PayrollCalculation.ay == ay
        ).all()
    
    def get_luca_records(self, db: Session, yil: int, ay: int) -> List[LucaBordro]:
        """Luca bordro kayıtlarını getir"""
        return db.query(LucaBordro).filter(
            LucaBordro.yil == yil,
            LucaBordro.ay == ay
        ).all()
    
    def get_puantaj_records(self, db: Session, donem: str) -> List[MonthlyPuantaj]:
        """Puantaj kayıtlarını getir"""
        return db.query(MonthlyPuantaj).filter(
            MonthlyPuantaj.donem == donem
        ).all()
    
    def create(self, db: Session, payroll: PayrollCalculation) -> PayrollCalculation:
        """Yeni bordro kaydı oluştur"""
        db.add(payroll)
        db.flush()
        return payroll
    
    def bulk_create(self, db: Session, payrolls: List[PayrollCalculation]) -> List[PayrollCalculation]:
        """Toplu bordro kaydı oluştur"""
        db.add_all(payrolls)
        db.flush()
        return payrolls
    
    def delete_by_period(self, db: Session, yil: int, ay: int) -> int:
        """Döneme ait bordro kayıtlarını sil"""
        count = db.query(PayrollCalculation).filter(
            PayrollCalculation.yil == yil,
            PayrollCalculation.ay == ay
        ).delete()
        return count


payroll_repo = PayrollRepository()
