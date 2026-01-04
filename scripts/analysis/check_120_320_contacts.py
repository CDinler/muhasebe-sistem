import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.bind.echo = False

# Aynı VKN'ye sahip hem 120 hem 320 hesapları kontrol et
print("=" * 80)
print("AYNI VKN'DE HEM 120 HEM 320 HESABI OLAN CARİLER")
print("=" * 80)

result = db.execute(text("""
    SELECT 
        c1.id as id_120,
        c1.code as code_120,
        c1.name as name_120,
        c1.tax_number,
        c2.id as id_320,
        c2.code as code_320,
        c2.name as name_320
    FROM contacts c1
    JOIN contacts c2 ON c1.tax_number = c2.tax_number
    WHERE c1.code LIKE '120.%'
      AND c2.code LIKE '320.%'
      AND c1.tax_number IS NOT NULL
      AND c1.tax_number != ''
    LIMIT 10
""")).fetchall()

if result:
    print(f"\n✅ {len(result)} cari bulundu (hem 120 hem 320):\n")
    for row in result:
        print(f"VKN: {row.tax_number}")
        print(f"  120: ID={row.id_120}, Code={row.code_120}, Name={row.name_120}")
        print(f"  320: ID={row.id_320}, Code={row.code_320}, Name={row.name_320}")
        print()
else:
    print("\n❌ Hiç bulunamadı!")

# Aynı isimde hem 120 hem 320 hesabı olanlar
print("\n" + "=" * 80)
print("AYNI İSİMDE HEM 120 HEM 320 HESABI OLAN CARİLER")
print("=" * 80)

result2 = db.execute(text("""
    SELECT 
        c1.id as id_120,
        c1.code as code_120,
        c1.name,
        c2.id as id_320,
        c2.code as code_320
    FROM contacts c1
    JOIN contacts c2 ON LOWER(TRIM(c1.name)) = LOWER(TRIM(c2.name))
    WHERE c1.code LIKE '120.%'
      AND c2.code LIKE '320.%'
    LIMIT 10
""")).fetchall()

if result2:
    print(f"\n✅ {len(result2)} cari bulundu:\n")
    for row in result2:
        print(f"İsim: {row.name}")
        print(f"  120: ID={row.id_120}, Code={row.code_120}")
        print(f"  320: ID={row.id_320}, Code={row.code_320}")
        print()
else:
    print("\n❌ Hiç bulunamadı!")

# Tek bir contact'a ait hem 120 hem 320 transaction_lines var mı?
print("\n" + "=" * 80)
print("BİR CONTACT'A AİT HEM 120 HEM 320 HESAPLARDA İŞLEM")
print("=" * 80)

result3 = db.execute(text("""
    SELECT 
        c.id,
        c.code,
        c.name,
        COUNT(CASE WHEN a.code LIKE '120.%' THEN 1 END) as count_120,
        COUNT(CASE WHEN a.code LIKE '320.%' THEN 1 END) as count_320
    FROM contacts c
    JOIN transaction_lines tl ON tl.contact_id = c.id
    JOIN accounts a ON tl.account_id = a.id
    WHERE a.code LIKE '120.%' OR a.code LIKE '320.%'
    GROUP BY c.id, c.code, c.name
    HAVING count_120 > 0 AND count_320 > 0
    LIMIT 5
""")).fetchall()

if result3:
    print(f"\n✅ {len(result3)} contact bulundu:\n")
    for row in result3:
        print(f"Contact: {row.id} - {row.code} - {row.name}")
        print(f"  120 hareketleri: {row.count_120}")
        print(f"  320 hareketleri: {row.count_320}")
        print()
else:
    print("\n❌ transaction_lines.contact_id boş olduğu için bulunamadı!")
    print("   (Önceki yüklemede contact_id set edilmemişti)")

db.close()
