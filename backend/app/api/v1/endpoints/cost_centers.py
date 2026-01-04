# -*- coding: utf-8 -*-
"""Cost Center API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud import cost_center as crud
from app.schemas.cost_center import CostCenterCreate, CostCenterUpdate, CostCenterResponse

router = APIRouter()

@router.get("/", response_model=List[CostCenterResponse])
def list_cost_centers(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Şantiyeleri listele"""
    cost_centers = crud.get_cost_centers(db, skip=skip, limit=limit, is_active=is_active)
    return cost_centers

@router.get("/{cost_center_id}", response_model=CostCenterResponse)
def get_cost_center(cost_center_id: int, db: Session = Depends(get_db)):
    """Tek şantiye detayı"""
    cost_center = crud.get_cost_center(db, cost_center_id)
    if not cost_center:
        raise HTTPException(status_code=404, detail="Cost center not found")
    return cost_center

@router.get("/code/{code}", response_model=CostCenterResponse)
def get_cost_center_by_code(code: str, db: Session = Depends(get_db)):
    """Şantiye koduna göre getir"""
    cost_center = crud.get_cost_center_by_code(db, code)
    if not cost_center:
        raise HTTPException(status_code=404, detail="Cost center not found")
    return cost_center

@router.post("/", response_model=CostCenterResponse, status_code=201)
def create_cost_center(cost_center: CostCenterCreate, db: Session = Depends(get_db)):
    """Yeni şantiye oluştur"""
    existing = crud.get_cost_center_by_code(db, cost_center.code)
    if existing:
        raise HTTPException(status_code=400, detail="Cost center code already exists")
    
    return crud.create_cost_center(db, cost_center)

@router.put("/{cost_center_id}", response_model=CostCenterResponse)
def update_cost_center(
    cost_center_id: int,
    cost_center: CostCenterUpdate,
    db: Session = Depends(get_db)
):
    """Şantiye güncelle"""
    updated = crud.update_cost_center(db, cost_center_id, cost_center)
    if not updated:
        raise HTTPException(status_code=404, detail="Cost center not found")
    return updated

@router.delete("/{cost_center_id}", status_code=204)
def delete_cost_center(cost_center_id: int, db: Session = Depends(get_db)):
    """Şantiye sil (soft delete)"""
    deleted = crud.delete_cost_center(db, cost_center_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cost center not found")
    return None
