import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.bind.echo = False

print("=" * 80)
print("KENAN KÖSE KONTROLÜ")
print("=" * 80)

# Contact'ları kontrol et
contacts = db.execute(text("""
    SELECT id, code, name, contact_type 
    FROM contacts 
    WHERE LOWER(name) LIKE '%kenan%köse%' OR LOWER(name) LIKE '%kenan köse%'
""")).fetchall()

if contacts:
    print(f"\n✅ {len(contacts)} adet KENAN KÖSE bulundu:\n")
    for c in contacts:
        print(f"  ID: {c[0]}, Code: {c[1]}, Name: {c[2]}, Type: {c[3]}")
        
        # Bu contact'ın hesap planında karşılığı var mı?
        account = db.execute(text(f"SELECT id, code, name FROM accounts WHERE code = '{c[1]}'")).fetchone()
        if account:
            print(f"    ✅ Hesap planında: {account[1]} - {account[2]}")
        else:
            print(f"    ❌ Hesap planında YOK!")
        
        # Bu contact'ın yevmiye kayıtları var mı?
        tx_count = db.execute(text(f"""
            SELECT COUNT(*) 
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE a.code = '{c[1]}'
        """)).scalar()
        print(f"    Yevmiye kayıtları: {tx_count} satır")
        print()
else:
    print("\n❌ KENAN KÖSE bulunamadı!")
    print("\n📝 Oluşturulacak:")
    
    # Sonraki boş 120 ve 320 kodlarını bul
    next_120 = db.execute(text("""
        SELECT CAST(SUBSTRING(code, 5) AS UNSIGNED) + 1 as next_code
        FROM accounts 
        WHERE code LIKE '120.%'
        ORDER BY CAST(SUBSTRING(code, 5) AS UNSIGNED) DESC
        LIMIT 1
    """)).scalar()
    
    next_320 = db.execute(text("""
        SELECT CAST(SUBSTRING(code, 5) AS UNSIGNED) + 1 as next_code
        FROM accounts 
        WHERE code LIKE '320.%'
        ORDER BY CAST(SUBSTRING(code, 5) AS UNSIGNED) DESC
        LIMIT 1
    """)).scalar()
    
    code_120 = f"120.{next_120:05d}" if next_120 else "120.00001"
    code_320 = f"320.{next_320:05d}" if next_320 else "320.00001"
    
    print(f"  - Müşteri (120): {code_120} - Kenan Köse")
    print(f"  - Tedarikçi (320): {code_320} - Kenan Köse")

db.close()
