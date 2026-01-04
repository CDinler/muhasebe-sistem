import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from app.models.monthly_personnel_record import MonthlyPersonnelRecord

db = SessionLocal()

count = db.query(MonthlyPersonnelRecord).filter(
    MonthlyPersonnelRecord.donem == '2025-11'
).count()

print(f"2025-11 döneminde {count} kayıt var")

if count > 0:
    sample = db.query(MonthlyPersonnelRecord).filter(
        MonthlyPersonnelRecord.donem == '2025-11'
    ).first()
    print(f"Örnek: personnel_id={sample.personnel_id}, bolum_adi={sample.bolum_adi}")

db.close()
