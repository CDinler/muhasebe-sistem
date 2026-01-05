"""
Contracts Router
FastAPI endpoints for personnel contracts
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.personnel_contract import (
    PersonnelContractCreate,
    PersonnelContractUpdate,
    PersonnelContractResponse,
    PersonnelContractList
)
from .service import ContractsService

router = APIRouter()


@router.get("/list", response_model=PersonnelContractList)
def list_contracts(
    personnel_id: Optional[int] = None,
    cost_center_id: Optional[int] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Personel sözleşmelerini listele"""
    service = ContractsService(db)
    contracts = service.list_contracts(personnel_id, cost_center_id, is_active)
    
    return {
        "contracts": contracts,
        "total": len(contracts)
    }


@router.get("/{contract_id}", response_model=PersonnelContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    """Tek sözleşme detayı"""
    service = ContractsService(db)
    contract = service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
    return contract


@router.get("/personnel/{personnel_id}/active", response_model=PersonnelContractResponse)
def get_active_contract(personnel_id: int, db: Session = Depends(get_db)):
    """Personelin aktif sözleşmesini getir"""
    service = ContractsService(db)
    contract = service.get_active_contract(personnel_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Aktif sözleşme bulunamadı")
    return contract


@router.post("/", response_model=PersonnelContractResponse, status_code=201)
def create_contract(contract: PersonnelContractCreate, db: Session = Depends(get_db)):
    """Yeni sözleşme oluştur"""
    service = ContractsService(db)
    return service.create_contract(contract.model_dump())


@router.put("/{contract_id}", response_model=PersonnelContractResponse)
def update_contract(
    contract_id: int,
    contract: PersonnelContractUpdate,
    db: Session = Depends(get_db)
):
    """Sözleşme güncelle"""
    service = ContractsService(db)
    updated = service.update_contract(contract_id, contract.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
    return updated


@router.delete("/{contract_id}", status_code=204)
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    """Sözleşme sil"""
    service = ContractsService(db)
    deleted = service.delete_contract(contract_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
    return None


@router.post("/{contract_id}/deactivate", status_code=204)
def deactivate_contract(contract_id: int, db: Session = Depends(get_db)):
    """Sözleşmeyi pasif yap"""
    service = ContractsService(db)
    deactivated = service.deactivate_contract(contract_id)
    if not deactivated:
        raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
    return None
