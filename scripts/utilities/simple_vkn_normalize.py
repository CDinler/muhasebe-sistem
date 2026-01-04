from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("DUPLICATE KONTROLÜ")
print("="*60)

# Duplicate test
result = db.execute(text("""
    SELECT 
        c1.id, c1.name, c1.tax_number,
        c2.id as dup_id, c2.name as dup_name
    FROM contacts c1
    JOIN contacts c2 ON c2.tax_number = LPAD(c1.tax_number, 10, '0')
    WHERE LENGTH(c1.tax_number) IN (8, 9)
    AND c1.id != c2.id
    LIMIT 10
""")).fetchall()

if result:
    print(f"\n{len(result)} duplicate bulundu:")
    for r in result:
        print(f"  ID:{r.id:4d} {r.tax_number:10s} → LPAD = {r.dup_name} (ID:{r.dup_id})")
else:
    print("\n✅ Duplicate yok!")

# Güvenle güncellenebilecek sayı
safe = db.execute(text("""
    SELECT COUNT(*) FROM contacts c1
    WHERE LENGTH(c1.tax_number) IN (8, 9)
    AND NOT EXISTS (
        SELECT 1 FROM contacts c2
        WHERE c2.tax_number = LPAD(c1.tax_number, 10, '0')
        AND c2.id != c1.id
    )
""")).scalar()

print(f"\n✅ Güvenle normalize edilebilir: {safe} kayıt")

# Şimdi güncelle
print("\nNormalize ediliyor...")
result = db.execute(text("""
    UPDATE contacts c1
    SET tax_number = LPAD(tax_number, 10, '0')
    WHERE LENGTH(c1.tax_number) IN (8, 9)
    AND NOT EXISTS (
        SELECT 1 FROM contacts c2
        WHERE c2.tax_number = LPAD(c1.tax_number, 10, '0')
        AND c2.id != c1.id
    )
"""))

db.commit()
print(f"✅ {result.rowcount} kayıt güncellendi")

# Eksik contact kontrolü
missing = db.execute(text("""
    SELECT COUNT(DISTINCT e.supplier_tax_number)
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    AND c.id IS NULL
""")).scalar()

print(f"\n📊 Eksik contact: {missing}")

db.close()
