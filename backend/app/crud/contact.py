"""Contact CRUD operations"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.contact import Contact
from app.schemas.contact import ContactCreate

def get_contact(db: Session, contact_id: int) -> Optional[Contact]:
    """Tek cari getir"""
    return db.query(Contact).filter(Contact.id == contact_id).first()

def get_contact_by_tax_number(db: Session, tax_number: str) -> Optional[Contact]:
    """Vergi numarasına göre cari getir"""
    return db.query(Contact).filter(Contact.tax_number == tax_number).first()

def get_contacts(db: Session, skip: int = 0, limit: int = 100, is_active: bool = True, contact_type: Optional[str] = None) -> List[Contact]:
    """Carileri listele - personelleri hariç tut"""
    query = db.query(Contact)
    if is_active:
        query = query.filter(Contact.is_active == True)
    if contact_type:
        query = query.filter(Contact.contact_type == contact_type)
    else:
        # Personelleri listeden çıkar
        query = query.filter(
            (Contact.contact_type != 'personnel') | Contact.contact_type.is_(None)
        )
    return query.order_by(Contact.name).offset(skip).limit(limit).all()

def create_contact(db: Session, contact: ContactCreate) -> Contact:
    """Yeni cari oluştur"""
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, contact_id: int, contact: ContactCreate) -> Optional[Contact]:
    """Cari güncelle"""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return None
    
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int) -> bool:
    """Cari sil (soft delete)"""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return False
    
    db_contact.is_active = False
    db.commit()
    return True
