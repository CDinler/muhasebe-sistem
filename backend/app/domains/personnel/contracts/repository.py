"""
Contracts Repository
Database operations for personnel contracts
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import PersonnelContract


class ContractsRepository:
    """Personel sözleşmeleri repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, contract_id: int) -> Optional[PersonnelContract]:
        """ID'ye göre sözleşme getir"""
        return self.db.query(PersonnelContract).filter(
            PersonnelContract.id == contract_id
        ).first()
    
    def get_list(
        self,
        personnel_id: Optional[int] = None,
        cost_center_id: Optional[int] = None,
        is_active: bool = True
    ) -> List[PersonnelContract]:
        """Sözleşmeleri listele"""
        query = self.db.query(PersonnelContract)
        
        if personnel_id:
            query = query.filter(PersonnelContract.personnel_id == personnel_id)
        
        if cost_center_id:
            query = query.filter(PersonnelContract.cost_center_id == cost_center_id)
        
        if is_active:
            query = query.filter(PersonnelContract.is_active == True)
        
        return query.order_by(PersonnelContract.ise_giris_tarihi.desc()).all()
    
    def get_active_by_personnel(self, personnel_id: int) -> Optional[PersonnelContract]:
        """Personelin aktif sözleşmesini getir"""
        return self.db.query(PersonnelContract).filter(
            and_(
                PersonnelContract.personnel_id == personnel_id,
                PersonnelContract.is_active == True
            )
        ).first()
    
    def create(self, contract_data: dict) -> PersonnelContract:
        """Yeni sözleşme oluştur"""
        contract = PersonnelContract(**contract_data)
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract
    
    def update(self, contract_id: int, contract_data: dict) -> Optional[PersonnelContract]:
        """Sözleşme güncelle"""
        contract = self.get_by_id(contract_id)
        if not contract:
            return None
        
        for key, value in contract_data.items():
            setattr(contract, key, value)
        
        self.db.commit()
        self.db.refresh(contract)
        return contract
    
    def delete(self, contract_id: int) -> bool:
        """Sözleşme sil"""
        contract = self.get_by_id(contract_id)
        if not contract:
            return False
        
        self.db.delete(contract)
        self.db.commit()
        return True
    
    def deactivate(self, contract_id: int) -> bool:
        """Sözleşmeyi pasif yap"""
        contract = self.get_by_id(contract_id)
        if not contract:
            return False
        
        contract.is_active = False
        self.db.commit()
        return True
