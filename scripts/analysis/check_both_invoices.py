#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
İki faturanın IBAN durumunu kontrol et
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database bağlantısı
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # İki fatura
    invoices = [
        ("UST2025000008341", "25.12.2025"),  # IBAN YOK
        ("UST2025000008062", "13.12.2025"),  # IBAN VAR
    ]
    
    for invoice_no, date in invoices:
        from sqlalchemy import text
        result = db.execute(text(f"""
            SELECT 
                e.id,
                e.invoice_number,
                e.issue_date,
                e.signing_time,
                e.contact_id,
                e.supplier_iban as xml_iban,
                c.iban as contact_iban,
                c.name as contact_name,
                c.tax_number
            FROM einvoices e
            LEFT JOIN contacts c ON e.contact_id = c.id
            WHERE e.invoice_number = '{invoice_no}'
        """)).fetchone()
        
        if result:
            print(f"\n{'='*80}")
            print(f"FATURA: {invoice_no} ({date})")
            print(f"{'='*80}")
            print(f"ID: {result[0]}")
            print(f"Issue Date: {result[2]}")
            print(f"Signing Time: {result[3]}")
            print(f"Contact ID: {result[4]}")
            print(f"Contact Name: {result[7]}")
            print(f"Contact VKN: {result[8]}")
            print(f"\nIBAN Durumu:")
            print(f"  XML IBAN (supplier_iban): {result[5] or 'YOK'}")
            print(f"  Contact IBAN: {result[6] or 'YOK'}")
            print(f"\nUI'da görünmesi gereken IBAN: {result[6] or result[5] or 'YOK'}")
        else:
            print(f"\n❌ {invoice_no} bulunamadı!")
    
finally:
    db.close()
