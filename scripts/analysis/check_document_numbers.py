from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("TRANSACTIONS.DOCUMENT_NUMBER KONTROLÜ")
print("="*60)

# Document_number dolu mu?
stats = db.execute(text("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN document_number IS NOT NULL AND document_number != '' THEN 1 ELSE 0 END) as with_doc,
        SUM(CASE WHEN document_number IS NULL OR document_number = '' THEN 1 ELSE 0 END) as without_doc
    FROM transactions
""")).fetchone()

print(f"Toplam transaction: {stats.total}")
print(f"Document number var: {stats.with_doc} ({stats.with_doc/stats.total*100:.1f}%)")
print(f"Document number yok: {stats.without_doc}")
print()

# Örnek document_number'lar
print("ÖRNEK DOCUMENT_NUMBER'LAR:")
print("="*60)
samples = db.execute(text("""
    SELECT document_number, transaction_date, description
    FROM transactions
    WHERE document_number IS NOT NULL 
    AND document_number != ''
    LIMIT 20
""")).fetchall()

for s in samples:
    print(f"{s.document_number} | {s.transaction_date} | {s.description or 'N/A'}")

# E-invoice number'larla eşleşen var mı?
print()
print("E-INVOICE ILE EŞLEŞMELER:")
print("="*60)

matches = db.execute(text("""
    SELECT 
        e.invoice_number,
        e.supplier_tax_number,
        e.payable_amount,
        t.id as transaction_id,
        t.document_number,
        t.transaction_date
    FROM einvoices e
    JOIN transactions t ON e.invoice_number = t.document_number
    WHERE e.invoice_category = 'incoming'
    LIMIT 10
""")).fetchall()

print(f"Direkt eşleşen: {len(matches)} fatura")
for m in matches:
    print(f"✅ {m.invoice_number} → T#{m.transaction_id}")

db.close()
