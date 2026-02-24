"""
Contacts Service
Business logic for contacts
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .repository import ContactRepository
from .models import Contact


class ContactService:
    """Cari business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContactRepository(db)
    
    def get_contact(self, contact_id: int) -> Optional[Contact]:
        """Tek cari getir"""
        return self.repo.get_by_id(contact_id)
    
    def get_by_tax_number(self, tax_number: str) -> Optional[Contact]:
        """Vergi numarasına göre cari getir"""
        return self.repo.get_by_tax_number(tax_number)
    
    def list_contacts(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = True,
        contact_type: Optional[str] = None
    ) -> List[Contact]:
        """Carileri listele"""
        return self.repo.get_list(
            skip=skip,
            limit=limit,
            is_active=is_active,
            contact_type=contact_type
        )
    
    def search_contacts(self, search_text: str, is_active: bool = True) -> List[Contact]:
        """Cari ara"""
        return self.repo.search(search_text, is_active)
    
    def count_contacts(self, is_active: bool = True, contact_type: Optional[str] = None) -> int:
        """Cari sayısını döndür"""
        return self.repo.count(is_active=is_active, contact_type=contact_type)
    
    def generate_contact_code(self, contact_type: str) -> str:
        """
        Otomatik cari kodu üret
        Müşteri: 120.xxxxx, Satıcı: 320.xxxxx
        """
        prefix = '120' if contact_type == 'customer' else '320'
        
        last_contact = self.db.query(Contact).filter(
            Contact.code.like(f'{prefix}.%')
        ).order_by(Contact.code.desc()).first()
        
        if last_contact and last_contact.code:
            try:
                last_num = int(last_contact.code.split('.')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'{prefix}.{new_num:05d}'
    
    def create_contact(self, contact_data: dict) -> Contact:
        """Yeni cari oluştur"""
        # Vergi numarası kontrolü
        if contact_data.get('tax_number'):
            existing = self.repo.get_by_tax_number(contact_data['tax_number'])
            if existing:
                raise ValueError("Bu vergi numarası zaten kayıtlı")
        
        # Cari kodu kontrolü
        if contact_data.get('code'):
            existing = self.repo.get_by_code(contact_data['code'])
            if existing:
                raise ValueError("Bu cari kodu zaten kullanılıyor")
        
        return self.repo.create(contact_data)
    
    def update_contact(self, contact_id: int, contact_data: dict) -> Optional[Contact]:
        """Cari güncelle"""
        # Mevcut cariyi kontrol et
        existing = self.repo.get_by_id(contact_id)
        if not existing:
            return None
        
        # Vergi numarası değişiyorsa ve başkası kullanıyorsa hata
        if contact_data.get('tax_number') and contact_data['tax_number'] != existing.tax_number:
            duplicate = self.repo.get_by_tax_number(contact_data['tax_number'])
            if duplicate:
                raise ValueError("Bu vergi numarası başka bir cari tarafından kullanılıyor")
        
        return self.repo.update(contact_id, contact_data)
    
    def delete_contact(self, contact_id: int) -> bool:
        """Cari sil (soft delete)"""
        return self.repo.soft_delete(contact_id)
    
    def bulk_import_contacts(self, contacts_data: List[dict]) -> int:
        """Toplu cari yükleme"""
        # TODO: Daha fazla validasyon eklenebilir
        return self.repo.bulk_create(contacts_data)
