from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 320 hesap kodlarının formatını kontrol et
rows = db.execute(text("""
    SELECT DISTINCT a.code, LENGTH(a.code) as len
    FROM accounts a
    WHERE a.code LIKE '320.%'
    LIMIT 20
""")).fetchall()

print("320 HESAP KODLARI:")
print("="*60)
for r in rows:
    print(f"{r.code} ({r.len} karakter)")

# Örnek bir VKN çıkarma
print()
print("VKN ÇIKARMA DENEMESİ:")
print("="*60)

test = db.execute(text("""
    SELECT 
        a.code,
        SUBSTRING(a.code, 7, 10) as vkn_try1,
        SUBSTRING(a.code, 5, 10) as vkn_try2,
        c.tax_number,
        c.name
    FROM accounts a
    LEFT JOIN contacts c ON c.tax_number = SUBSTRING(a.code, 5, 10)
    WHERE a.code LIKE '320.%'
    LIMIT 5
""")).fetchall()

for t in test:
    print(f"\nKod: {t.code}")
    print(f"  Try1 (pos7): {t.vkn_try1}")
    print(f"  Try2 (pos5): {t.vkn_try2}")
    print(f"  Match: {t.name if t.name else 'YOK'}")

db.close()
