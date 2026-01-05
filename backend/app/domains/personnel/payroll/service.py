"""
Payroll Service
Business logic for payroll calculation
"""
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException

from app.domains.personnel.payroll.repository import payroll_repo
from app.models.payroll_calculation import PayrollCalculation


class PayrollService:
    """Bordro hesaplama servisi"""
    
    def __init__(self):
        self.repository = payroll_repo
    
    def get_by_period(self, db: Session, yil: int, ay: int) -> List[PayrollCalculation]:
        """Döneme göre bordro kayıtlarını getir"""
        return self.repository.get_by_period(db, yil, ay)
    
    def calculate_payroll(self, db: Session, yil: int, ay: int, donem: str):
        """
        Bordro hesaplama - V1 endpoint logic'ini kullan
        Şimdilik V1'e forward ediyoruz, ileride buraya taşınacak
        """
        # TODO: V1'deki hesaplama logic'ini buraya taşı
        from app.api.v1.endpoints.bordro_calculation import calculate_bordro as v1_calculate
        from app.api.v1.endpoints.bordro_calculation import CalculateRequest
        
        req = CalculateRequest(yil=yil, ay=ay, donem=donem)
        return v1_calculate(req, db)


payroll_service = PayrollService()
