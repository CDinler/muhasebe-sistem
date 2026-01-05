"""
Contracts Service
Business logic for personnel contracts
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .repository import ContractsRepository
from .models import PersonnelContract


class ContractsService:
    """Personel sözleşmeleri business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContractsRepository(db)
    
    def get_contract(self, contract_id: int) -> Optional[PersonnelContract]:
        """Sözleşme getir"""
        return self.repo.get_by_id(contract_id)
    
    def list_contracts(
        self,
        personnel_id: Optional[int] = None,
        cost_center_id: Optional[int] = None,
        is_active: bool = True
    ) -> List[PersonnelContract]:
        """Sözleşmeleri listele"""
        return self.repo.get_list(personnel_id, cost_center_id, is_active)
    
    def get_active_contract(self, personnel_id: int) -> Optional[PersonnelContract]:
        """Personelin aktif sözleşmesini getir"""
        return self.repo.get_active_by_personnel(personnel_id)
    
    def create_contract(self, contract_data: dict) -> PersonnelContract:
        """Yeni sözleşme oluştur"""
        # Aynı personel için başka aktif sözleşme var mı kontrol et
        personnel_id = contract_data.get('personnel_id')
        if personnel_id:
            existing = self.repo.get_active_by_personnel(personnel_id)
            if existing and contract_data.get('is_active', True):
                # Eski sözleşmeyi pasif yap
                self.repo.deactivate(existing.id)
        
        return self.repo.create(contract_data)
    
    def update_contract(self, contract_id: int, contract_data: dict) -> Optional[PersonnelContract]:
        """Sözleşme güncelle"""
        return self.repo.update(contract_id, contract_data)
    
    def delete_contract(self, contract_id: int) -> bool:
        """Sözleşme sil"""
        return self.repo.delete(contract_id)
    
    def deactivate_contract(self, contract_id: int) -> bool:
        """Sözleşmeyi pasif yap"""
        return self.repo.deactivate(contract_id)
