from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("TRANSACTION_LINES'A CONTACT_ID EKLEME")
print("="*60)

# accounts.contact_id'den transaction_lines.contact_id'ye kopyala
result = db.execute(text("""
    UPDATE transaction_lines tl
    JOIN accounts a ON tl.account_id = a.id
    SET tl.contact_id = a.contact_id
    WHERE a.contact_id IS NOT NULL
    AND tl.contact_id IS NULL
"""))

print(f"✅ {result.rowcount} transaction_lines güncellendi")

db.commit()

# Kontrol
stats = db.execute(text("""
    SELECT 
        COUNT(*) as total_320,
        SUM(CASE WHEN tl.contact_id IS NOT NULL THEN 1 ELSE 0 END) as with_contact,
        SUM(CASE WHEN tl.contact_id IS NULL THEN 1 ELSE 0 END) as without_contact
    FROM transaction_lines tl
    JOIN accounts a ON tl.account_id = a.id
    WHERE a.code LIKE '320.%'
""")).fetchone()

print()
print(f"📊 320 Hesapları Durum:")
print(f"  Toplam: {stats.total_320}")
print(f"  Contact ID var: {stats.with_contact}")
print(f"  Contact ID yok: {stats.without_contact}")

db.close()
