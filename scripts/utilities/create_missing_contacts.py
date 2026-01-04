#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact'ı olmayan 12 fatura için yeni contact oluştur
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.contact import Contact

# Database bağlantısı
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Contact_id NULL olan faturalar
    results = db.execute(text("""
        SELECT 
            e.id,
            e.invoice_number,
            e.supplier_name,
            e.supplier_tax_number,
            e.supplier_tax_office,
            e.supplier_address,
            e.supplier_city,
            e.supplier_district,
            e.supplier_phone,
            e.supplier_email,
            e.supplier_iban,
            e.invoice_category
        FROM einvoices e
        WHERE e.contact_id IS NULL
        AND e.supplier_tax_number IS NOT NULL
    """)).fetchall()
    
    print(f"\n{'='*120}")
    print(f"CONTACT OLUŞTURMA")
    print(f"{'='*120}\n")
    
    created = 0
    already_exists = 0
    
    for row in results:
        invoice_id = row[0]
        invoice_no = row[1]
        supplier_name = row[2]
        vkn = row[3]
        tax_office = row[4]
        address = row[5]
        city = row[6]
        district = row[7]
        phone = row[8]
        email = row[9]
        iban = row[10]
        category = row[11]
        
        # Bu VKN ile contact var mı kontrol et
        existing_contact = db.execute(text(f"""
            SELECT id FROM contacts WHERE tax_number = '{vkn}'
        """)).fetchone()
        
        if existing_contact:
            # Varsa sadece faturaya bağla
            contact_id = existing_contact[0]
            db.execute(text(f"""
                UPDATE einvoices SET contact_id = {contact_id} WHERE id = {invoice_id}
            """))
            print(f"✅ {invoice_no:20s} | {supplier_name:50s} -> Mevcut Contact ID: {contact_id}")
            already_exists += 1
        else:
            # Yeni contact oluştur
            # Code üret
            from app.api.v1.endpoints.einvoices import generate_contact_code
            
            contact_type = 'SUPPLIER' if 'incoming' in category else 'CUSTOMER'
            new_code = generate_contact_code(db, 'supplier' if contact_type == 'SUPPLIER' else 'customer')
            
            new_contact = Contact(
                code=new_code,
                name=supplier_name,
                contact_type=contact_type,
                tax_number=vkn,
                tax_office=tax_office,
                address=address,
                city=city,
                district=district,
                phone=phone,
                email=email,
                iban=iban,
                is_active=True
            )
            
            db.add(new_contact)
            db.flush()
            
            # Faturaya bağla
            db.execute(text(f"""
                UPDATE einvoices SET contact_id = {new_contact.id} WHERE id = {invoice_id}
            """))
            
            print(f"🆕 {invoice_no:20s} | {supplier_name:50s} -> Yeni Contact ID: {new_contact.id} (Code: {new_code})")
            created += 1
    
    db.commit()
    
    print(f"\n{'='*120}")
    print(f"TAMAMLANDI!")
    print(f"{'='*120}")
    print(f"🆕 Yeni oluşturulan: {created}")
    print(f"✅ Mevcut kullanılan: {already_exists}")
    print(f"TOPLAM: {created + already_exists}")
    print(f"{'='*120}\n")
    
finally:
    db.close()
