from app.core.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)
cols = inspector.get_columns('einvoices')

print("=== EINVOICES TABLO KOLONLARI ===")
json_cols = [c for c in cols if 'json' in c['name'].lower() or 'raw' in c['name'].lower() or 'data' in c['name'].lower()]

if json_cols:
    print("\nJSON/DATA kolonları:")
    for c in json_cols:
        print(f"  - {c['name']}: {c['type']}")
else:
    print("\n❌ JSON kolon YOK!")

# Bir fatura örneği kontrol et
print("\n=== BİR FATURA ÖRNEĞİ ===")
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, invoice_number, raw_data FROM einvoices WHERE raw_data IS NOT NULL LIMIT 1"))
    row = result.fetchone()
    
    if row:
        print(f"ID: {row[0]}, Fatura No: {row[1]}")
        print(f"raw_data içeriği: {row[2][:500] if row[2] else 'BOŞ'}...")
    else:
        print("raw_data olan fatura YOK!")
