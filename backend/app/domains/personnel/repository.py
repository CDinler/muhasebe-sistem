"""Personnel domain repository (CRUD operations)"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.shared.base.repository import CRUDBase
from app.domains.personnel.models import Personnel, PersonnelContract
from app.domains.personnel.schemas import (
    PersonnelCreate, 
    PersonnelUpdate,
    PersonnelContractCreate,
    PersonnelContractUpdate
)


class PersonnelRepository(CRUDBase[Personnel, PersonnelCreate, PersonnelUpdate]):
    """Personnel repository with custom queries"""
    
    def get_by_tc_kimlik_no(self, db: Session, tc: str) -> Optional[Personnel]:
        """Get personnel by TC kimlik no"""
        return db.query(self.model).filter(Personnel.tc_kimlik_no == tc).first()
    
    def search(self, db: Session, term: str, skip: int = 0, limit: int = 100) -> List[Personnel]:
        """Search personnel by name or TC"""
        query = db.query(self.model).filter(
            (Personnel.ad.contains(term)) |
            (Personnel.soyad.contains(term)) |
            (Personnel.tc_kimlik_no.contains(term))
        )
        return query.offset(skip).limit(limit).all()


class PersonnelContractRepository(CRUDBase[PersonnelContract, PersonnelContractCreate, PersonnelContractUpdate]):
    """Personnel contract repository with custom queries"""
    
    def get_by_personnel_id(self, db: Session, personnel_id: int) -> List[PersonnelContract]:
        """Get all contracts for a personnel"""
        return db.query(self.model).filter(
            PersonnelContract.personnel_id == personnel_id
        ).all()
    
    def get_active_contract(self, db: Session, personnel_id: int) -> Optional[PersonnelContract]:
        """Get active contract for personnel"""
        return db.query(self.model).filter(
            PersonnelContract.personnel_id == personnel_id,
            PersonnelContract.is_active == 1
        ).first()
    
    def get_by_cost_center(self, db: Session, cost_center_id: int) -> List[PersonnelContract]:
        """Get all contracts for a cost center"""
        return db.query(self.model).filter(
            PersonnelContract.cost_center_id == cost_center_id,
            PersonnelContract.is_active == 1
        ).all()


# Repository instances
personnel_repo = PersonnelRepository(Personnel)
personnel_contract_repo = PersonnelContractRepository(PersonnelContract)
