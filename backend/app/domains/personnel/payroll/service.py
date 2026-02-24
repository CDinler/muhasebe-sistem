"""
Payroll Service
Business logic for payroll calculation
"""
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException

from app.domains.personnel.payroll.repository import payroll_repo
from app.models import PayrollCalculation


class PayrollService:
    """Bordro hesaplama servisi"""
    
    def __init__(self):
        self.repository = payroll_repo
    
    def get_by_period(self, db: Session, yil: int, ay: int) -> List[PayrollCalculation]:
        """Döneme göre bordro kayıtlarını getir"""
        return self.repository.get_by_period(db, yil, ay)
    
    def calculate_payroll(self, db: Session, yil: int, ay: int, donem: str):
        """
        Bordro hesaplama - V2 service kullan
        """
        from app.domains.personnel.bordro_calculation.service import BordroCalculationService
        
        service = BordroCalculationService(db)
        return service.calculate(yil, ay)


payroll_service = PayrollService()
