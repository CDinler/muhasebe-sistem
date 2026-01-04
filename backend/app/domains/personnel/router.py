"""Personnel domain API router"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.domains.personnel.service import personnel_service, personnel_contract_service
from app.domains.personnel.schemas import (
    PersonnelCreate,
    PersonnelUpdate,
    PersonnelResponse,
    PersonnelList,
    PersonnelContractCreate,
    PersonnelContractResponse
)
from app.domains.personnel.repository import personnel_repo, personnel_contract_repo

router = APIRouter()


@router.get("/", response_model=PersonnelList)
def get_personnel(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get personnel list with optional search"""
    if search:
        items = personnel_service.search_personnel(db, search, skip, limit)
        total = len(items)  # For search, we just count results
    else:
        items = personnel_repo.get_multi(db, skip, limit)
        total = personnel_repo.count(db)
    
    return PersonnelList(
        items=items,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{personnel_id}", response_model=PersonnelResponse)
def get_personnel_by_id(
    personnel_id: int,
    db: Session = Depends(get_db)
):
    """Get single personnel by ID"""
    personnel = personnel_repo.get(db, personnel_id)
    if not personnel:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Personnel", personnel_id)
    return personnel


@router.post("/", response_model=PersonnelResponse)
def create_personnel(
    data: PersonnelCreate,
    db: Session = Depends(get_db)
):
    """Create new personnel"""
    return personnel_service.create_personnel(db, data)


@router.put("/{personnel_id}", response_model=PersonnelResponse)
def update_personnel(
    personnel_id: int,
    data: PersonnelUpdate,
    db: Session = Depends(get_db)
):
    """Update personnel"""
    return personnel_service.update_personnel(db, personnel_id, data)


@router.delete("/{personnel_id}")
def delete_personnel(
    personnel_id: int,
    db: Session = Depends(get_db)
):
    """Delete personnel"""
    success = personnel_service.delete_personnel(db, personnel_id)
    return {"success": success, "message": "Personnel deleted successfully"}


# PersonnelContract endpoints
@router.post("/contracts", response_model=PersonnelContractResponse)
def create_personnel_contract(
    data: PersonnelContractCreate,
    db: Session = Depends(get_db)
):
    """Create new personnel contract"""
    return personnel_contract_service.create_contract(db, data)


@router.get("/{personnel_id}/contracts")
def get_personnel_contracts(
    personnel_id: int,
    db: Session = Depends(get_db)
):
    """Get all contracts for a personnel"""
    contracts = personnel_contract_service.get_personnel_contracts(db, personnel_id)
    return {"items": contracts, "total": len(contracts)}
