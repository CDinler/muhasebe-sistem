"""
Document types listesi
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("📋 Document Types Listesi:\n")

result = db.execute(text("SELECT code, name, category FROM document_types ORDER BY sort_order"))

for idx, row in enumerate(result, 1):
    print(f"{idx:2}. {row[0]:30} - {row[1]:45} ({row[2]})")

db.close()
