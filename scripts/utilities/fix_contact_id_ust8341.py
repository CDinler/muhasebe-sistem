#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UST2025000008341 faturasına contact_id ata
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
    # Contact ID'yi bul
    contact = db.execute(text("""
        SELECT id FROM contacts WHERE tax_number = '35566411922'
    """)).fetchone()
    
    if contact:
        contact_id = contact[0]
        print(f"Contact ID: {contact_id}")
        
        # Faturaya contact_id ata
        result = db.execute(text(f"""
            UPDATE einvoices 
            SET contact_id = {contact_id}
            WHERE invoice_number = 'UST2025000008341'
        """))
        db.commit()
        
        print(f"✅ Fatura güncellendi! contact_id={contact_id} atandı.")
        
        # Kontrol et
        check = db.execute(text("""
            SELECT e.invoice_number, e.contact_id, c.name, c.iban
            FROM einvoices e
            LEFT JOIN contacts c ON e.contact_id = c.id
            WHERE e.invoice_number = 'UST2025000008341'
        """)).fetchone()
        
        print(f"\nKontrol:")
        print(f"  Invoice: {check[0]}")
        print(f"  Contact ID: {check[1]}")
        print(f"  Contact Name: {check[2]}")
        print(f"  Contact IBAN: {check[3]}")
    else:
        print("❌ Contact bulunamadı!")
    
finally:
    db.close()
