"""
Cost Centers Repository
Database operations for cost centers
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .models import CostCenter


class CostCenterRepository:
    """Maliyet merkezi repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, cost_center_id: int) -> Optional[CostCenter]:
        """ID'ye göre maliyet merkezi getir"""
        return self.db.query(CostCenter).filter(CostCenter.id == cost_center_id).first()
    
    def get_by_code(self, code: str) -> Optional[CostCenter]:
        """Koda göre maliyet merkezi getir"""
        return self.db.query(CostCenter).filter(CostCenter.code == code).first()
    
    def get_list(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = True
    ) -> List[CostCenter]:
        """Maliyet merkezlerini listele"""
        query = self.db.query(CostCenter).filter(CostCenter.is_active == is_active)
        return query.offset(skip).limit(limit).all()
    
    def get_all_active(self) -> List[CostCenter]:
        """Tüm aktif maliyet merkezlerini getir"""
        return self.db.query(CostCenter).filter(CostCenter.is_active == True).all()
    
    def create(self, cost_center_data: dict) -> CostCenter:
        """Yeni maliyet merkezi oluştur"""
        cost_center = CostCenter(**cost_center_data)
        self.db.add(cost_center)
        self.db.commit()
        self.db.refresh(cost_center)
        return cost_center
    
    def update(self, cost_center_id: int, cost_center_data: dict) -> Optional[CostCenter]:
        """Maliyet merkezi güncelle"""
        cost_center = self.get_by_id(cost_center_id)
        if not cost_center:
            return None
        
        for key, value in cost_center_data.items():
            setattr(cost_center, key, value)
        
        self.db.commit()
        self.db.refresh(cost_center)
        return cost_center
    
    def soft_delete(self, cost_center_id: int) -> bool:
        """Maliyet merkezi soft delete"""
        cost_center = self.get_by_id(cost_center_id)
        if not cost_center:
            return False
        
        cost_center.is_active = False
        self.db.commit()
        return True
