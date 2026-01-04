"""Personnel domain service (Business logic)"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from app.domains.personnel.repository import personnel_repo, personnel_contract_repo
from app.domains.personnel.schemas import PersonnelCreate, PersonnelUpdate, PersonnelContractCreate
from app.domains.personnel.models import Personnel, PersonnelContract


class PersonnelService:
    """Personnel business logic"""
    
    def create_personnel(self, db: Session, data: PersonnelCreate) -> Personnel:
        """Create new personnel with validation"""
        # Business rule: TC kimlik must be unique
        existing = personnel_repo.get_by_tc_kimlik_no(db, data.tc_kimlik_no)
        if existing:
            raise BusinessException(f"TC kimlik numarası {data.tc_kimlik_no} zaten kayıtlı")
        
        # Business rule: TC kimlik must be 11 digits
        if not data.tc_kimlik_no.isdigit():
            raise ValidationException("TC kimlik no sadece rakamlardan oluşmalı", "tc_kimlik_no")
        
        # Business rule: IBAN validation (if provided)
        if data.iban and not self._validate_iban(data.iban):
            raise ValidationException("Geçersiz IBAN formatı", "iban")
        
        return personnel_repo.create(db, data)
    
    def update_personnel(self, db: Session, personnel_id: int, data: PersonnelUpdate) -> Personnel:
        """Update personnel with validation"""
        personnel = personnel_repo.get(db, personnel_id)
        if not personnel:
            raise NotFoundException("Personnel", personnel_id)
        
        # TC kimlik uniqueness check (if changing)
        if data.tc_kimlik_no and data.tc_kimlik_no != personnel.tc_kimlik_no:
            existing = personnel_repo.get_by_tc_kimlik_no(db, data.tc_kimlik_no)
            if existing:
                raise BusinessException(f"TC kimlik numarası {data.tc_kimlik_no} başka bir personele ait")
        
        # IBAN validation
        if data.iban and not self._validate_iban(data.iban):
            raise ValidationException("Geçersiz IBAN formatı", "iban")
        
        return personnel_repo.update(db, personnel, data)
    
    def delete_personnel(self, db: Session, personnel_id: int) -> bool:
        """Delete personnel (business rule: check if has active contracts)"""
        personnel = personnel_repo.get(db, personnel_id)
        if not personnel:
            raise NotFoundException("Personnel", personnel_id)
        
        # Business rule: Cannot delete personnel with active contracts
        active_contract = personnel_contract_repo.get_active_contract(db, personnel_id)
        if active_contract:
            raise BusinessException("Aktif sözleşmesi olan personel silinemez")
        
        return personnel_repo.delete(db, personnel_id)
    
    def search_personnel(self, db: Session, term: str, skip: int = 0, limit: int = 100) -> List[Personnel]:
        """Search personnel"""
        return personnel_repo.search(db, term, skip, limit)
    
    def _validate_iban(self, iban: str) -> bool:
        """Validate IBAN format (Turkish IBAN)"""
        if not iban:
            return True
        iban = iban.replace(" ", "").upper()
        if len(iban) != 26 or not iban.startswith("TR"):
            return False
        return True


class PersonnelContractService:
    """Personnel contract business logic"""
    
    def create_contract(self, db: Session, data: PersonnelContractCreate) -> PersonnelContract:
        """Create new personnel contract"""
        # Business rule: Personnel must exist
        personnel = personnel_repo.get(db, data.personnel_id)
        if not personnel:
            raise NotFoundException("Personnel", data.personnel_id)
        
        # Business rule: TC must match personnel
        if data.tc_kimlik_no != personnel.tc_kimlik_no:
            raise BusinessException("Sözleşme TC kimlik no personel TC'si ile uyuşmuyor")
        
        # Business rule: Only one active contract per personnel
        existing_active = personnel_contract_repo.get_active_contract(db, data.personnel_id)
        if existing_active and data.is_active == 1:
            raise BusinessException("Bu personelin zaten aktif bir sözleşmesi var")
        
        return personnel_contract_repo.create(db, data)
    
    def get_personnel_contracts(self, db: Session, personnel_id: int) -> List[PersonnelContract]:
        """Get all contracts for personnel"""
        personnel = personnel_repo.get(db, personnel_id)
        if not personnel:
            raise NotFoundException("Personnel", personnel_id)
        
        return personnel_contract_repo.get_by_personnel_id(db, personnel_id)


# Service instances
personnel_service = PersonnelService()
personnel_contract_service = PersonnelContractService()
