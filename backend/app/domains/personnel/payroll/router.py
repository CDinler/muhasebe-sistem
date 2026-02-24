"""
Payroll Router (V2 API)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.domains.personnel.payroll.service import payroll_service
from app.models import PayrollCalculation

router = APIRouter()


class PayrollCalculateRequest(BaseModel):
    """Bordro hesaplama request"""
    yil: int
    ay: int
    donem: str  # YYYY-MM


class PayrollResponse(BaseModel):
    """Bordro response"""
    id: int
    personnel_id: int
    adi_soyadi: str
    yil: int
    ay: int
    brut_ucret: float
    net_ucret: float
    
    class Config:
        from_attributes = True


@router.get('/list')
def list_payrolls(
    yil: int,
    ay: int,
    db: Session = Depends(get_db)
) -> List[PayrollResponse]:
    """
    Döneme göre bordro listesi
    """
    payrolls = payroll_service.get_by_period(db, yil, ay)
    return payrolls


@router.post('/calculate')
def calculate_payroll(
    req: PayrollCalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Bordro hesaplama
    """
    result = payroll_service.calculate_payroll(db, req.yil, req.ay, req.donem)
    return result
