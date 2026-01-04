"""Cost Center CRUD operations"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.cost_center import CostCenter
from app.schemas.cost_center import CostCenterCreate, CostCenterUpdate

def get_cost_center(db: Session, cost_center_id: int) -> Optional[CostCenter]:
    """Tek şantiye getir"""
    return db.query(CostCenter).filter(CostCenter.id == cost_center_id).first()

def get_cost_center_by_code(db: Session, code: str) -> Optional[CostCenter]:
    """Şantiye koduna göre getir"""
    return db.query(CostCenter).filter(CostCenter.code == code).first()

def get_cost_centers(db: Session, skip: int = 0, limit: int = 100, is_active: bool = True) -> List[CostCenter]:
    """Şantiyeleri listele"""
    query = db.query(CostCenter)
    if is_active:
        query = query.filter(CostCenter.is_active == True)
    return query.order_by(CostCenter.code).offset(skip).limit(limit).all()

def create_cost_center(db: Session, cost_center: CostCenterCreate) -> CostCenter:
    """Yeni şantiye oluştur"""
    db_cost_center = CostCenter(**cost_center.model_dump())
    db.add(db_cost_center)
    db.commit()
    db.refresh(db_cost_center)
    return db_cost_center

def update_cost_center(db: Session, cost_center_id: int, cost_center: CostCenterUpdate) -> Optional[CostCenter]:
    """Şantiye güncelle"""
    db_cost_center = get_cost_center(db, cost_center_id)
    if not db_cost_center:
        return None
    
    update_data = cost_center.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cost_center, key, value)
    
    db.commit()
    db.refresh(db_cost_center)
    return db_cost_center

def delete_cost_center(db: Session, cost_center_id: int) -> bool:
    """Şantiye sil (soft delete)"""
    db_cost_center = get_cost_center(db, cost_center_id)
    if not db_cost_center:
        return False
    
    db_cost_center.is_active = False
    db.commit()
    return True
