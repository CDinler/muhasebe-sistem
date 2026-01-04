import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()

print("INVOICE_TRANSACTION_MAPPINGS TABLOSU:")
print("=" * 100)

# Tablo yapısı
cursor.execute("DESCRIBE invoice_transaction_mappings")
columns = cursor.fetchall()

print("\nTablo Yapısı:")
for col in columns:
    print(f"  {col[0]:20} {col[1]:30} {col[2]:10}")

# Kayıt sayısı
cursor.execute("SELECT COUNT(*) FROM invoice_transaction_mappings")
count = cursor.fetchone()[0]
print(f"\nToplam Kayıt Sayısı: {count}")

if count > 0:
    print("\nSon 10 Kayıt:")
    cursor.execute("""
        SELECT 
            id,
            einvoice_id,
            transaction_id,
            document_number,
            mapping_type,
            confidence_score,
            mapped_at
        FROM invoice_transaction_mappings
        ORDER BY id DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    print(f"{'ID':<6} {'EInvoice':<10} {'Transaction':<12} {'Doc Number':<20} {'Type':<8} {'Score':<7} {'Mapped At'}")
    print("-" * 100)
    for row in rows:
        id, einvoice_id, trans_id, doc_num, map_type, score, mapped_at = row
        print(f"{id:<6} {einvoice_id:<10} {trans_id:<12} {doc_num:<20} {map_type:<8} {score:<7.2f} {mapped_at}")

# Import edilmiş faturalar
cursor.execute("""
    SELECT COUNT(*) 
    FROM einvoices 
    WHERE processing_status = 'COMPLETED' AND transaction_id IS NOT NULL
""")
completed_count = cursor.fetchone()[0]

print(f"\nImport Edilmiş (COMPLETED) Faturalar: {completed_count}")

# Mapping ile import karşılaştırma
cursor.execute("""
    SELECT 
        e.id,
        e.invoice_number,
        e.transaction_id,
        m.id as mapping_id,
        m.mapping_type
    FROM einvoices e
    LEFT JOIN invoice_transaction_mappings m ON e.id = m.einvoice_id
    WHERE e.processing_status = 'COMPLETED' AND e.transaction_id IS NOT NULL
    LIMIT 5
""")

print("\nImport Edilmiş Fatura Örnekleri (Mapping Kontrolü):")
rows = cursor.fetchall()
print(f"{'EInvoice ID':<12} {'Invoice Number':<25} {'Trans ID':<10} {'Mapping ID':<12} {'Mapping Type'}")
print("-" * 100)
for row in rows:
    e_id, inv_num, trans_id, map_id, map_type = row
    status = "✅ MAPPING VAR" if map_id else "❌ MAPPING YOK!"
    print(f"{e_id:<12} {inv_num:<25} {trans_id:<10} {map_id if map_id else 'NULL':<12} {map_type if map_type else 'NULL':<15} {status}")

cursor.close()
conn.close()
