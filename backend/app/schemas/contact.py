"""Contact Pydantic schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import date

class ContactBase(BaseModel):
    name: str
    code: Optional[str] = None
    tax_number: Optional[str] = None
    tax_office: Optional[str] = None
    contact_type: Optional[str] = "both"  # customer, supplier, both
    is_active: bool = True
    
    # İletişim
    phone: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "TÜRKİYE"
    
    # Fatura Adresi
    invoice_address: Optional[str] = None
    invoice_city: Optional[str] = None
    invoice_district: Optional[str] = None
    
    # Yetkili Kişi
    contact_person: Optional[str] = None
    contact_person_phone: Optional[str] = None
    contact_person_email: Optional[str] = None
    contact_person_title: Optional[str] = None
    
    # İş Bilgileri
    sector: Optional[str] = None
    region: Optional[str] = None
    customer_group: Optional[str] = None
    
    # Finansal
    risk_limit: Optional[Decimal] = Decimal('0')
    payment_term_days: Optional[int] = 0
    payment_method: Optional[str] = "Havale"
    discount_rate: Optional[Decimal] = Decimal('0')
    
    # Banka
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_account_no: Optional[str] = None
    iban: Optional[str] = None
    swift: Optional[str] = None
    
    # Notlar
    notes: Optional[str] = None
    private_notes: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    tax_number: Optional[str] = None
    tax_office: Optional[str] = None
    contact_type: Optional[str] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    invoice_address: Optional[str] = None
    invoice_city: Optional[str] = None
    invoice_district: Optional[str] = None
    contact_person: Optional[str] = None
    contact_person_phone: Optional[str] = None
    contact_person_email: Optional[str] = None
    contact_person_title: Optional[str] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    customer_group: Optional[str] = None
    risk_limit: Optional[Decimal] = None
    payment_term_days: Optional[int] = None
    payment_method: Optional[str] = None
    discount_rate: Optional[Decimal] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_account_no: Optional[str] = None
    iban: Optional[str] = None
    swift: Optional[str] = None
    notes: Optional[str] = None
    private_notes: Optional[str] = None

class ContactResponse(ContactBase):
    id: int
    current_balance: Optional[Decimal] = Decimal('0')
    first_transaction_date: Optional[date] = None
    last_transaction_date: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)
