#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contact_id NULL olan faturaları bul
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # NULL contact_id olan faturalar
    results = conn.execute(text("""
        SELECT 
            id,
            invoice_number,
            supplier_name,
            supplier_tax_number,
            issue_date,
            created_at
        FROM einvoices 
        WHERE contact_id IS NULL
        AND supplier_tax_number IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 20
    """)).fetchall()
    
    print(f"\n{'='*120}")
    print(f"CONTACT_ID NULL OLAN FATURALAR (Son 20)")
    print(f"{'='*120}\n")
    
    for row in results:
        print(f"ID: {row[0]:4d} | {row[1]:20s} | {row[2]:40s} | VKN: {row[3]} | {row[4]} | {row[5]}")
        
        # Bu VKN ile contact var mı?
        contact = conn.execute(text(f"""
            SELECT id, name 
            FROM contacts 
            WHERE tax_number = '{row[3]}'
        """)).fetchone()
        
        if contact:
            print(f"       ⚠️ CONTACT VAR! ID: {contact[0]}, Name: {contact[1]}")
        else:
            print(f"       ❌ Contact yok")
        print()
    
    # Toplam sayı
    total = conn.execute(text("""
        SELECT COUNT(*) 
        FROM einvoices 
        WHERE contact_id IS NULL 
        AND supplier_tax_number IS NOT NULL
    """)).scalar()
    
    print(f"\n{'='*120}")
    print(f"TOPLAM: {total} fatura")
    print(f"{'='*120}")
