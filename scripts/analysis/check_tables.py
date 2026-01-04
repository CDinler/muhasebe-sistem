"""Tüm bordro tablolarını listele"""
import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.bind.echo = False

# Tüm tabloları listele
all_tables = db.execute(text("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'muhasebe_luca' 
    ORDER BY table_name
""")).fetchall()

print("\n" + "="*70)
print("TÜM DATABASE TABLOLARI")
print("="*70)
for t in all_tables:
    print(f"  {t[0]}")

# Bordro ilgili tabloları filtrele
print("\n" + "="*70)
print("BORDRO İLGİLİ TABLOLAR")
print("="*70)

bordro_keywords = ['person', 'bordro', 'puantaj', 'payroll', 'contract', 'luca']
bordro_tables = [t[0] for t in all_tables if any(kw in t[0].lower() for kw in bordro_keywords)]

if bordro_tables:
    for table in bordro_tables:
        # Her tablo için kayıt sayısı
        count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"  ✓ {table}: {count} kayıt")
else:
    print("  Hiç bordro tablosu bulunamadı!")

db.close()
