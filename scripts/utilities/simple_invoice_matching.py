from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("E-FATURA BASIT EŞLEŞTIRME (DOCUMENT_NUMBER)")
print("="*60)

# Basit eşleştirme: einvoices.invoice_number = transactions.document_number
result = db.execute(text("""
    UPDATE einvoices e
    JOIN transactions t ON e.invoice_number = t.document_number
    SET e.transaction_id = t.id
    WHERE e.invoice_category = 'incoming'
    AND e.transaction_id IS NULL
"""))

print(f"✅ {result.rowcount} e-fatura eşleştirildi")

db.commit()

# İstatistik
stats = db.execute(text("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN transaction_id IS NOT NULL THEN 1 ELSE 0 END) as matched,
        SUM(CASE WHEN transaction_id IS NULL THEN 1 ELSE 0 END) as unmatched
    FROM einvoices
    WHERE invoice_category = 'incoming'
""")).fetchone()

print()
print("SONUÇ:")
print(f"  Toplam gelen e-fatura: {stats.total}")
print(f"  Eşleşmiş: {stats.matched} ({stats.matched/stats.total*100:.1f}%)")
print(f"  Eşleşmemiş: {stats.unmatched} ({stats.unmatched/stats.total*100:.1f}%)")

# Eşleşmeyen örnekler
if stats.unmatched > 0:
    print()
    print("EŞLEŞMEYEN ÖRNEKLER (ilk 10):")
    print("="*60)
    unmatched = db.execute(text("""
        SELECT 
            e.invoice_number,
            e.supplier_tax_number,
            e.payable_amount,
            e.issue_date,
            c.name as contact_name
        FROM einvoices e
        LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
        WHERE e.invoice_category = 'incoming'
        AND e.transaction_id IS NULL
        LIMIT 10
    """)).fetchall()
    
    for u in unmatched:
        print(f"❌ {u.invoice_number} | {u.contact_name} | {u.payable_amount:.2f}₺ | {u.issue_date}")

db.close()
