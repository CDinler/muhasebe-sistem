from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=== TRANSACTION DESCRIPTIONS (320 hesaplar) ===")
print("="*80)

result = db.execute(text("""
    SELECT t.id, t.description, t.transaction_date
    FROM transactions t
    WHERE id IN (
        SELECT DISTINCT transaction_id 
        FROM transaction_lines 
        WHERE account_id IN (
            SELECT id FROM accounts WHERE code LIKE '320%'
        )
    )
    LIMIT 20
""")).fetchall()

for r in result:
    desc = r.description[:100] if r.description else "NULL"
    print(f"ID:{r.id} | {r.transaction_date} | {desc}")

db.close()
