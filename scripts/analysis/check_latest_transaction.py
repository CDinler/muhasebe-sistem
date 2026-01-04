"""
Test: Import edilen transaction ve transaction_lines tüm alanları kaydediyor mu?
Turkcell faturasını kontrol et - quantity, unit, vat_rate, vat_base, cost_center_id, document_type_id
"""
import sys
sys.path.append('c:/Projects/muhasebe-sistem/backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database bağlantısı
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/muhasebe_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("EN SON IMPORT EDİLEN TRANSACTION VE LİNES KONTROLÜ")
print("=" * 80)

# En son transaction'ı bul
query = text("""
SELECT 
    t.id,
    t.transaction_number,
    t.transaction_date,
    t.document_number,
    t.cost_center_id,
    cc.name as cost_center_name,
    t.document_type_id,
    dt.name as document_type_name,
    t.document_subtype_id,
    ds.name as document_subtype_name
FROM transactions t
LEFT JOIN cost_centers cc ON t.cost_center_id = cc.id
LEFT JOIN document_types dt ON t.document_type_id = dt.id
LEFT JOIN document_subtypes ds ON t.document_subtype_id = ds.id
ORDER BY t.id DESC
LIMIT 1;
""")

result = db.execute(query).fetchone()

if not result:
    print("❌ Hiç transaction yok!")
    sys.exit(1)

transaction_id = result[0]
print(f"\n📝 Transaction ID: {result[0]}")
print(f"📝 Fiş No: {result[1]}")
print(f"📅 Tarih: {result[2]}")
print(f"📄 Belge No: {result[3]}")
print(f"🏢 Cost Center ID: {result[4]} - {result[5] or 'YOK'}")
print(f"📋 Document Type ID: {result[6]} - {result[7] or 'YOK'}")
print(f"📋 Document Subtype ID: {result[8]} - {result[9] or 'YOK'}")

# Transaction alanları kontrolü
if result[4] is None:
    print("❌ cost_center_id NULL!")
else:
    print("✅ cost_center_id DOLU")

if result[6] is None:
    print("❌ document_type_id NULL!")
else:
    print("✅ document_type_id DOLU")

if result[8] is None:
    print("❌ document_subtype_id NULL!")
else:
    print("✅ document_subtype_id DOLU")

# Transaction lines kontrolü
print("\n" + "=" * 80)
print("TRANSACTION LINES KONTROLÜ")
print("=" * 80)

query2 = text("""
SELECT 
    tl.id,
    a.code as account_code,
    a.name as account_name,
    tl.description,
    tl.debit,
    tl.credit,
    tl.quantity,
    tl.unit,
    tl.vat_rate,
    tl.withholding_rate,
    tl.vat_base
FROM transaction_lines tl
JOIN accounts a ON tl.account_id = a.id
WHERE tl.transaction_id = :transaction_id
ORDER BY tl.id;
""")

lines = db.execute(query2, {'transaction_id': transaction_id}).fetchall()

if not lines:
    print("❌ Hiç satır yok!")
    sys.exit(1)

print(f"\n📊 Toplam {len(lines)} satır")
print()

null_count = 0
filled_count = 0

for line in lines:
    print(f"Line ID {line[0]}: {line[1]} - {line[2]}")
    print(f"  Açıklama: {line[3]}")
    print(f"  Borç: {line[4]}, Alacak: {line[5]}")
    
    # quantity, unit kontrolü
    if line[6] is not None:
        print(f"  ✅ Miktar: {line[6]} {line[7] or ''}")
        filled_count += 1
    else:
        print(f"  ❌ Miktar: NULL")
        null_count += 1
    
    # vat_rate kontrolü
    if line[8] is not None:
        print(f"  ✅ KDV Oranı: {float(line[8]):.2%}")
        filled_count += 1
    else:
        print(f"  ❌ KDV Oranı: NULL")
        null_count += 1
    
    # vat_base kontrolü
    if line[10] is not None:
        print(f"  ✅ KDV Matrahı: {line[10]}")
        filled_count += 1
    else:
        print(f"  ❌ KDV Matrahı: NULL")
        null_count += 1
    
    print()

print("=" * 80)
print("ÖZET")
print("=" * 80)
print(f"✅ Dolu alan sayısı: {filled_count}")
print(f"❌ NULL alan sayısı: {null_count}")

if null_count == 0:
    print("\n🎉 TÜM ALANLAR DOLU! SORUN ÇÖZÜLDÜ!")
else:
    print(f"\n⚠️  Hala {null_count} adet NULL alan var!")

db.close()
