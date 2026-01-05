"""
Cost Centers Service
Business logic for cost centers
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .repository import CostCenterRepository
from .models import CostCenter


class CostCenterService:
    """Maliyet merkezi business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = CostCenterRepository(db)
    
    def get_cost_center(self, cost_center_id: int) -> Optional[CostCenter]:
        """Tek maliyet merkezi getir"""
        return self.repo.get_by_id(cost_center_id)
    
    def get_by_code(self, code: str) -> Optional[CostCenter]:
        """Koda göre maliyet merkezi getir"""
        return self.repo.get_by_code(code)
    
    def list_cost_centers(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = True
    ) -> List[CostCenter]:
        """Maliyet merkezlerini listele"""
        return self.repo.get_list(skip=skip, limit=limit, is_active=is_active)
    
    def get_all_active(self) -> List[CostCenter]:
        """Tüm aktif maliyet merkezlerini getir"""
        return self.repo.get_all_active()
    
    def create_cost_center(self, cost_center_data: dict) -> CostCenter:
        """Yeni maliyet merkezi oluştur"""
        # Kod kontrolü
        if cost_center_data.get('code'):
            existing = self.repo.get_by_code(cost_center_data['code'])
            if existing:
                raise ValueError("Bu kod zaten kullanılıyor")
        
        return self.repo.create(cost_center_data)
    
    def update_cost_center(self, cost_center_id: int, cost_center_data: dict) -> Optional[CostCenter]:
        """Maliyet merkezi güncelle"""
        # Mevcut maliyet merkezi kontrolü
        existing = self.repo.get_by_id(cost_center_id)
        if not existing:
            return None
        
        # Kod değişiyorsa ve başkası kullanıyorsa hata
        if cost_center_data.get('code') and cost_center_data['code'] != existing.code:
            duplicate = self.repo.get_by_code(cost_center_data['code'])
            if duplicate:
                raise ValueError("Bu kod başka bir maliyet merkezi tarafından kullanılıyor")
        
        return self.repo.update(cost_center_id, cost_center_data)
    
    def delete_cost_center(self, cost_center_id: int) -> bool:
        """Maliyet merkezi sil (soft delete)"""
        return self.repo.soft_delete(cost_center_id)
