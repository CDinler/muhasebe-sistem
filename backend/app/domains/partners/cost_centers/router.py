"""
Cost Centers Router
FastAPI endpoints for cost centers
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from app.domains.partners.cost_centers.schemas import CostCenterCreate, CostCenterResponse
from .service import CostCenterService

router = APIRouter(tags=["Cost Centers (V2)"])


@router.get("/")
def list_cost_centers(
    skip: int = 0,
    limit: int = 10000,
    is_active: Optional[bool] = None,
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """Maliyet merkezlerini listele"""
    service = CostCenterService(db)
    items = service.list_cost_centers(skip=skip, limit=limit, is_active=is_active)
    total = service.count_cost_centers(is_active=is_active)
    return {"items": items, "total": total}


@router.get("/active", response_model=List[CostCenterResponse])
def get_all_active(
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """Tüm aktif maliyet merkezlerini getir"""
    service = CostCenterService(db)
    return service.get_all_active()


@router.get("/{cost_center_id}", response_model=CostCenterResponse)
def get_cost_center(
    cost_center_id: int,
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """Tek maliyet merkezi detayı"""
    service = CostCenterService(db)
    cost_center = service.get_cost_center(cost_center_id)
    if not cost_center:
        raise HTTPException(status_code=404, detail="Maliyet merkezi bulunamadı")
    return cost_center


@router.get("/code/{code}", response_model=CostCenterResponse)
def get_by_code(
    code: str,
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """Koda göre maliyet merkezi getir"""
    service = CostCenterService(db)
    cost_center = service.get_by_code(code)
    if not cost_center:
        raise HTTPException(status_code=404, detail="Maliyet merkezi bulunamadı")
    return cost_center


@router.post("/", response_model=CostCenterResponse, status_code=201)
def create_cost_center(
    cost_center: CostCenterCreate,
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """Yeni maliyet merkezi oluştur"""
    service = CostCenterService(db)
    try:
        return service.create_cost_center(cost_center.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{cost_center_id}", response_model=CostCenterResponse)
def update_cost_center(
    cost_center_id: int,
    cost_center: CostCenterCreate,
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """Maliyet merkezi güncelle"""
    service = CostCenterService(db)
    try:
        updated = service.update_cost_center(cost_center_id, cost_center.model_dump())
        if not updated:
            raise HTTPException(status_code=404, detail="Maliyet merkezi bulunamadı")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cost_center_id}", status_code=204)
def delete_cost_center(
    cost_center_id: int,
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """Maliyet merkezi sil (soft delete)"""
    service = CostCenterService(db)
    deleted = service.delete_cost_center(cost_center_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Maliyet merkezi bulunamadı")
    return None
