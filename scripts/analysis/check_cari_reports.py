import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Contacts sayısı
contacts_count = db.execute(text("SELECT COUNT(*) FROM contacts")).scalar()
print(f"📊 Contacts: {contacts_count:,}")

# Active contacts
active_contacts = db.execute(text("SELECT COUNT(*) FROM contacts WHERE is_active = 1")).scalar()
print(f"✅ Active Contacts: {active_contacts:,}")

# 120/320 hesaplar
cari_accounts = db.execute(text("SELECT COUNT(*) FROM accounts WHERE code LIKE '120.%' OR code LIKE '320.%'")).scalar()
print(f"📋 Cari Hesaplar (120/320): {cari_accounts:,}")

# Transaction_lines'da 120/320 kullanımı
result = db.execute(text("""
    SELECT COUNT(DISTINCT tl.id) as count
    FROM transaction_lines tl
    JOIN accounts a ON tl.account_id = a.id
    WHERE a.code LIKE '120.%' OR a.code LIKE '320.%'
""")).fetchone()
print(f"💼 Transaction Lines (120/320): {result[0]:,}")

# Örnek bir contact al
sample = db.execute(text("SELECT id, code, name FROM contacts WHERE is_active = 1 LIMIT 5")).fetchall()
print("\n📝 Örnek Cariler:")
for row in sample:
    print(f"  - {row[0]}: {row[1]} - {row[2]}")
    
    # Bu carinin account_id'sini bul
    account = db.execute(text(f"SELECT id, code FROM accounts WHERE code = '{row[1]}'")).fetchone()
    if account:
        print(f"    Account ID: {account[0]}, Code: {account[1]}")
        
        # Bu hesapta transaction_lines var mı?
        tx_count = db.execute(text(f"SELECT COUNT(*) FROM transaction_lines WHERE account_id = {account[0]}")).scalar()
        print(f"    Transaction Lines: {tx_count:,}")
    else:
        print(f"    ⚠️ Account bulunamadı!")

db.close()
