#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact_id NULL olan ama contact'ı var olan faturaları toplu düzelt
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database bağlantısı
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # NULL contact_id olan faturalar
    results = db.execute(text("""
        SELECT 
            e.id,
            e.invoice_number,
            e.supplier_name,
            e.supplier_tax_number
        FROM einvoices e
        WHERE e.contact_id IS NULL
        AND e.supplier_tax_number IS NOT NULL
    """)).fetchall()
    
    print(f"\n{'='*120}")
    print(f"CONTACT_ID NULL OLAN FATURALARI DÜZELTİYORUM")
    print(f"{'='*120}\n")
    
    fixed = 0
    no_contact = 0
    
    for row in results:
        invoice_id = row[0]
        invoice_no = row[1]
        supplier_name = row[2]
        vkn = row[3]
        
        # Bu VKN ile contact var mı?
        contact = db.execute(text(f"""
            SELECT id, name 
            FROM contacts 
            WHERE tax_number = '{vkn}'
        """)).fetchone()
        
        if contact:
            contact_id = contact[0]
            # Faturaya contact_id ata
            db.execute(text(f"""
                UPDATE einvoices 
                SET contact_id = {contact_id}
                WHERE id = {invoice_id}
            """))
            print(f"✅ {invoice_no:20s} | {supplier_name:50s} -> Contact ID: {contact_id}")
            fixed += 1
        else:
            print(f"❌ {invoice_no:20s} | {supplier_name:50s} | VKN: {vkn} -> Contact bulunamadı")
            no_contact += 1
    
    db.commit()
    
    print(f"\n{'='*120}")
    print(f"TAMAMLANDI!")
    print(f"{'='*120}")
    print(f"✅ Düzeltilen: {fixed}")
    print(f"❌ Contact bulunamayan: {no_contact}")
    print(f"TOPLAM: {fixed + no_contact}")
    print(f"{'='*120}\n")
    
finally:
    db.close()
