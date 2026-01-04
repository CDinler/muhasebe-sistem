#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UST2025000008341 faturasının supplier bilgilerini kontrol et
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
    # 25 Aralık faturası
    result = db.execute(text("""
        SELECT 
            id,
            invoice_number,
            supplier_tax_number,
            supplier_name,
            supplier_iban,
            contact_id,
            xml_file_path,
            issue_date,
            signing_time
        FROM einvoices
        WHERE invoice_number = 'UST2025000008341'
    """)).fetchone()
    
    if result:
        print(f"\n{'='*80}")
        print(f"FATURA: {result[1]}")
        print(f"{'='*80}")
        print(f"Supplier Tax Number: {result[2]}")
        print(f"Supplier Name: {result[3]}")
        print(f"Supplier IBAN (XML): {result[4] or 'YOK'}")
        print(f"Contact ID: {result[5] or 'NULL - İŞTE SORUN!'}")
        print(f"XML File: {result[6]}")
        print(f"Issue Date: {result[7]}")
        print(f"Signing Time: {result[8]}")
        
        # Bu VKN ile contact var mı?
        if result[2]:
            contact = db.execute(text(f"""
                SELECT id, name, iban
                FROM contacts
                WHERE tax_number = '{result[2]}'
            """)).fetchone()
            
            if contact:
                print(f"\n{'='*80}")
                print(f"CONTACT BİLGİSİ VAR!")
                print(f"{'='*80}")
                print(f"Contact ID: {contact[0]}")
                print(f"Contact Name: {contact[1]}")
                print(f"Contact IBAN: {contact[2] or 'YOK'}")
                print(f"\n⚠️ FATURANIN contact_id ALANI NULL, AMA CONTACT VAR!")
                print(f"   Faturaya contact_id={contact[0]} atamalı!")
            else:
                print(f"\n❌ VKN {result[2]} için contact bulunamadı!")
                print(f"   Contact oluşturulmalı veya VKN eşleşmesi kontrol edilmeli!")
    
finally:
    db.close()
