#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()

null_count = conn.execute(text('SELECT COUNT(*) FROM einvoices WHERE contact_id IS NULL AND supplier_tax_number IS NOT NULL')).scalar()
total = conn.execute(text('SELECT COUNT(*) FROM einvoices WHERE supplier_tax_number IS NOT NULL')).scalar()

print(f"Contact_id NULL: {null_count}/{total} ({100*null_count/total:.1f}%)")
conn.close()
