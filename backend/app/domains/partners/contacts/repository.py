"""
Contacts Repository
Database operations for contacts
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import Contact


class ContactRepository:
    """Cari repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        """ID'ye göre cari getir"""
        return self.db.query(Contact).filter(Contact.id == contact_id).first()
    
    def get_by_tax_number(self, tax_number: str) -> Optional[Contact]:
        """Vergi numarasına göre cari getir"""
        return self.db.query(Contact).filter(Contact.tax_number == tax_number).first()
    
    def get_by_code(self, code: str) -> Optional[Contact]:
        """Cari koduna göre getir"""
        return self.db.query(Contact).filter(Contact.code == code).first()
    
    def get_list(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = True,
        contact_type: Optional[str] = None
    ) -> List[Contact]:
        """Carileri listele"""
        query = self.db.query(Contact).filter(Contact.is_active == is_active)
        
        if contact_type:
            query = query.filter(Contact.contact_type == contact_type)
        
        return query.offset(skip).limit(limit).all()
    
    def search(
        self,
        search_text: str,
        is_active: bool = True
    ) -> List[Contact]:
        """Cari ara (isim veya vergi numarasında)"""
        search_pattern = f"%{search_text}%"
        return self.db.query(Contact).filter(
            and_(
                Contact.is_active == is_active,
                or_(
                    Contact.name.ilike(search_pattern),
                    Contact.tax_number.ilike(search_pattern),
                    Contact.code.ilike(search_pattern)
                )
            )
        ).all()
    
    def create(self, contact_data: dict) -> Contact:
        """Yeni cari oluştur"""
        contact = Contact(**contact_data)
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact
    
    def update(self, contact_id: int, contact_data: dict) -> Optional[Contact]:
        """Cari güncelle"""
        contact = self.get_by_id(contact_id)
        if not contact:
            return None
        
        for key, value in contact_data.items():
            setattr(contact, key, value)
        
        self.db.commit()
        self.db.refresh(contact)
        return contact
    
    def soft_delete(self, contact_id: int) -> bool:
        """Cari soft delete"""
        contact = self.get_by_id(contact_id)
        if not contact:
            return False
        
        contact.is_active = False
        self.db.commit()
        return True
    
    def bulk_create(self, contacts_data: List[dict]) -> int:
        """Toplu cari oluştur"""
        contacts = [Contact(**data) for data in contacts_data]
        self.db.bulk_save_objects(contacts)
        self.db.commit()
        return len(contacts)
