import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# PersonnelContract tablosunda cost_center_id değerleri
contracts = db.execute(text("""
    SELECT id, personnel_id, cost_center_id 
    FROM personnel_contracts 
    LIMIT 20
""")).fetchall()

print(f"\n=== PersonnelContract Cost Center ID Değerleri (İlk 20) ===")
for c in contracts:
    print(f"Contract ID: {c[0]}, Personnel ID: {c[1]}, Cost Center ID: {c[2]}")

# NULL olanlar
null_count = db.execute(text("""
    SELECT COUNT(*) 
    FROM personnel_contracts 
    WHERE cost_center_id IS NULL
""")).scalar()

total_count = db.execute(text("SELECT COUNT(*) FROM personnel_contracts")).scalar()

print(f"\n=== İstatistikler ===")
print(f"Toplam Contract: {total_count}")
print(f"Cost Center ID NULL Olan: {null_count}")
print(f"Cost Center ID Dolu Olan: {total_count - null_count}")

db.close()
