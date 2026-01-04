"""
SQL Test: En son transaction ve lines kontrolü
"""
import psycopg2
from decimal import Decimal

# Database bağlantısı
conn = psycopg2.connect(
    dbname="muhasebe_db",
    user="postgres",
    password="12345",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

print("=" * 80)
print("EN SON TRANSACTION VE LINES KONTROLÜ")
print("=" * 80)

# En son transaction'ı bul
cur.execute("""
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

result = cur.fetchone()

if not result:
    print("❌ Hiç transaction yok!")
    cur.close()
    conn.close()
    exit(1)

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

cur.execute("""
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
WHERE tl.transaction_id = %s
ORDER BY tl.id;
""", (transaction_id,))

lines = cur.fetchall()

if not lines:
    print("❌ Hiç satır yok!")
    cur.close()
    conn.close()
    exit(1)

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
        print(f"  ⚠️  Miktar: NULL")
        null_count += 1
    
    # vat_rate kontrolü
    if line[8] is not None:
        print(f"  ✅ KDV Oranı: {float(line[8]):.2%}")
        filled_count += 1
    else:
        print(f"  ⚠️  KDV Oranı: NULL")
        null_count += 1
    
    # vat_base kontrolü
    if line[10] is not None:
        print(f"  ✅ KDV Matrahı: {line[10]}")
        filled_count += 1
    else:
        print(f"  ⚠️  KDV Matrahı: NULL")
        null_count += 1
    
    print()

print("=" * 80)
print("ÖZET")
print("=" * 80)
print(f"✅ Dolu alan sayısı: {filled_count}")
print(f"❌ NULL alan sayısı: {null_count}")

# Kritik alanlar kontrolü
critical_passed = (
    result[4] is not None and  # cost_center_id
    result[6] is not None and  # document_type_id
    result[8] is not None  # document_subtype_id
)

if critical_passed:
    print("✅ TRANSACTION METADATA: Tüm alanlar dolu!")
else:
    print("❌ TRANSACTION METADATA: Bazı alanlar NULL!")

if null_count == 0:
    print("\n🎉 TÜM ALANLAR DOLU! SORUN ÇÖZÜLDÜ!")
else:
    print(f"\n⚠️  Hala {null_count} adet NULL alan var!")

cur.close()
conn.close()
