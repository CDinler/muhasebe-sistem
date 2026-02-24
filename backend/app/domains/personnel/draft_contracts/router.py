"""Personnel Draft Contracts Router"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import PersonnelDraftContract
from app.domains.personnel.draft_contracts.schemas import (
    PersonnelDraftContractCreate,
    PersonnelDraftContractUpdate,
    PersonnelDraftContractResponse
)

router = APIRouter()


@router.get("/", response_model=List[PersonnelDraftContractResponse])
async def get_draft_contracts(
    personnel_id: Optional[int] = None,
    ucret_nevi: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Taslak sözleşmeleri listele - Tüm kayıtları döndür (aktif+pasif)"""
    query = db.query(PersonnelDraftContract).options(
        joinedload(PersonnelDraftContract.personnel),
        joinedload(PersonnelDraftContract.cost_center)
    )
    
    if personnel_id is not None:
        query = query.filter(PersonnelDraftContract.personnel_id == personnel_id)
    if ucret_nevi is not None:
        query = query.filter(PersonnelDraftContract.ucret_nevi == ucret_nevi)
    # is_active filtresi (None ise tüm kayıtlar döner)
    if is_active is not None:
        query = query.filter(PersonnelDraftContract.is_active == (1 if is_active else 0))
    
    # Aktif kayıtlar önce, pasif kayıtlar sonda (is_active DESC: 1->0)  
    query = query.order_by(PersonnelDraftContract.is_active.desc())
    
    draft_contracts = query.offset(skip).limit(limit).all()
    return draft_contracts


@router.get("/{draft_contract_id}", response_model=PersonnelDraftContractResponse)
async def get_draft_contract(
    draft_contract_id: int,
    db: Session = Depends(get_db)
):
    """Tek taslak sözleşme getir"""
    draft_contract = db.query(PersonnelDraftContract).options(
        joinedload(PersonnelDraftContract.personnel),
        joinedload(PersonnelDraftContract.cost_center)
    ).filter(PersonnelDraftContract.id == draft_contract_id).first()
    
    if not draft_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft contract {draft_contract_id} bulunamadı"
        )
    
    return draft_contract


@router.post("/", response_model=PersonnelDraftContractResponse, status_code=status.HTTP_201_CREATED)
async def create_draft_contract(
    draft_contract_data: PersonnelDraftContractCreate,
    db: Session = Depends(get_db)
):
    """Yeni taslak sözleşme oluştur"""
    # Personnel kontrolü
    from app.models import Personnel
    personnel = db.query(Personnel).filter(Personnel.id == draft_contract_data.personnel_id).first()
    if not personnel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personnel {draft_contract_data.personnel_id} bulunamadı"
        )
    
    # Cost center kontrolü (varsa)
    if draft_contract_data.cost_center_id:
        from app.models import CostCenter
        cost_center = db.query(CostCenter).filter(CostCenter.id == draft_contract_data.cost_center_id).first()
        if not cost_center:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cost Center {draft_contract_data.cost_center_id} bulunamadı"
            )
    
    # Yeni draft contract oluştur
    draft_contract = PersonnelDraftContract(**draft_contract_data.dict())
    db.add(draft_contract)
    db.commit()
    db.refresh(draft_contract)
    
    return draft_contract


@router.put("/{draft_contract_id}", response_model=PersonnelDraftContractResponse)
async def update_draft_contract(
    draft_contract_id: int,
    draft_contract_data: PersonnelDraftContractUpdate,
    db: Session = Depends(get_db)
):
    """Taslak sözleşme güncelle"""
    draft_contract = db.query(PersonnelDraftContract).filter(
        PersonnelDraftContract.id == draft_contract_id
    ).first()
    
    if not draft_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft contract {draft_contract_id} bulunamadı"
        )
    
    # Cost center kontrolü (varsa)
    if draft_contract_data.cost_center_id is not None:
        from app.models import CostCenter
        cost_center = db.query(CostCenter).filter(CostCenter.id == draft_contract_data.cost_center_id).first()
        if not cost_center:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cost Center {draft_contract_data.cost_center_id} bulunamadı"
            )
    
    # Update fields
    update_data = draft_contract_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(draft_contract, field, value)
    
    db.commit()
    db.refresh(draft_contract)
    
    return draft_contract


@router.delete("/{draft_contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft_contract(
    draft_contract_id: int,
    db: Session = Depends(get_db)
):
    """Taslak sözleşme sil"""
    draft_contract = db.query(PersonnelDraftContract).filter(
        PersonnelDraftContract.id == draft_contract_id
    ).first()
    
    if not draft_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft contract {draft_contract_id} bulunamadı"
        )
    
    # Personnel_contracts'ta bu draft'ı kullanan var mı kontrol et
    from app.domains.personnel.models import PersonnelContract
    linked_contracts = db.query(PersonnelContract).filter(
        PersonnelContract.personnel_draft_contracts_id == draft_contract_id
    ).count()
    
    if linked_contracts > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu taslak sözleşme {linked_contracts} resmi sözleşmede kullanılıyor. Önce bağlantıları kaldırın."
        )
    
    db.delete(draft_contract)
    db.commit()
    
    return None

 
