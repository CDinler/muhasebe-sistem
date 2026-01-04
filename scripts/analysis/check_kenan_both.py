import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.bind.echo = False

print("=" * 80)
print("KENAN KÖSE - HEM 120 HEM 320 KONTROLÜ")
print("=" * 80)

# 120.00547 hesabı var mı?
account_120 = db.execute(text("SELECT id, code, name FROM accounts WHERE code = '120.00547'")).fetchone()
account_320 = db.execute(text("SELECT id, code, name FROM accounts WHERE code = '320.00547'")).fetchone()

if account_120:
    print(f"\n✅ 120.00547 hesabı VAR:")
    print(f"   ID: {account_120[0]}, Code: {account_120[1]}, Name: {account_120[2]}")
    
    # Transaction lines var mı?
    tx_120 = db.execute(text(f"SELECT COUNT(*) FROM transaction_lines WHERE account_id = {account_120[0]}")).scalar()
    print(f"   Transaction lines: {tx_120}")
else:
    print(f"\n❌ 120.00547 hesabı YOK!")

if account_320:
    print(f"\n✅ 320.00547 hesabı VAR:")
    print(f"   ID: {account_320[0]}, Code: {account_320[1]}, Name: {account_320[2]}")
    
    # Transaction lines var mı?
    tx_320 = db.execute(text(f"SELECT COUNT(*) FROM transaction_lines WHERE account_id = {account_320[0]}")).scalar()
    print(f"   Transaction lines: {tx_320}")
else:
    print(f"\n❌ 320.00547 hesabı YOK!")

# Contact'ları kontrol et
contact_120 = db.execute(text("SELECT id, code, name FROM contacts WHERE code = '120.00547'")).fetchone()
contact_320 = db.execute(text("SELECT id, code, name FROM contacts WHERE code = '320.00547'")).fetchone()

print("\n" + "=" * 80)
print("CONTACTS TABLOSU")
print("=" * 80)

if contact_120:
    print(f"\n✅ 120.00547 contact VAR:")
    print(f"   ID: {contact_120[0]}, Code: {contact_120[1]}, Name: {contact_120[2]}")
else:
    print(f"\n❌ 120.00547 contact YOK - Oluşturulmalı!")

if contact_320:
    print(f"\n✅ 320.00547 contact VAR:")
    print(f"   ID: {contact_320[0]}, Code: {contact_320[1]}, Name: {contact_320[2]}")
else:
    print(f"\n❌ 320.00547 contact YOK!")

# Eğer ikisi de varsa
if account_120 and account_320:
    print("\n" + "=" * 80)
    print("✅ HEM 120 HEM 320 HESABI VAR!")
    print("=" * 80)
    
    if contact_120 and contact_320:
        print("\n✅ Her iki contact da var - Rapor 3 sekme gösterecek!")
    elif contact_320 and not contact_120:
        print("\n⚠️ 320 contact var ama 120 contact yok")
        print("   120.00547 contact'ı oluşturulacak...")
    elif contact_120 and not contact_320:
        print("\n⚠️ 120 contact var ama 320 contact yok")
        print("   320.00547 contact'ı zaten var gibi görünüyor, kontrol et")

db.close()
