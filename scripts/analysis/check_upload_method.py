#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Faturanın nasıl yüklendiğini kontrol et
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            xml_file_path, 
            created_at,
            updated_at
        FROM einvoices 
        WHERE invoice_number = 'UST2025000008341'
    """)).fetchone()
    
    print(f"XML Path: {result[0]}")
    print(f"created_at: {result[1]}")
    print(f"updated_at: {result[2]}")
