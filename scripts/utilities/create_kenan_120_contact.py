import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text
from datetime import datetime

db = SessionLocal()
db.bind.echo = False

print("=" * 80)
print("120.00547 CONTACT OLUŞTURMA")
print("=" * 80)

# 320.00547 contact bilgilerini al
contact_320 = db.execute(text("""
    SELECT name, tax_number, phone, email, address 
    FROM contacts 
    WHERE code = '320.00547'
""")).fetchone()

if contact_320:
    print(f"\n320.00547 contact bilgileri:")
    print(f"  Name: {contact_320[0]}")
    print(f"  Tax Number: {contact_320[1]}")
    print(f"  Phone: {contact_320[2]}")
    print(f"  Email: {contact_320[3]}")
    print(f"  Address: {contact_320[4]}")
    
    # 120.00547 için contact oluştur
    print(f"\n120.00547 contact oluşturuluyor...")
    
    db.execute(text("""
        INSERT INTO contacts (
            code, name, contact_type, tax_number, 
            phone, email, address, is_active
        ) VALUES (
            '120.00547',
            :name,
            'customer',
            :tax_number,
            :phone,
            :email,
            :address,
            1
        )
    """), {
        'name': contact_320[0],
        'tax_number': contact_320[1],
        'phone': contact_320[2],
        'email': contact_320[3],
        'address': contact_320[4]
    })
    
    db.commit()
    
    # Kontrol et
    new_contact = db.execute(text("SELECT id, code, name FROM contacts WHERE code = '120.00547'")).fetchone()
    
    if new_contact:
        print(f"\n✅ BAŞARILI!")
        print(f"   ID: {new_contact[0]}")
        print(f"   Code: {new_contact[1]}")
        print(f"   Name: {new_contact[2]}")
        print(f"\n🎉 Artık Kenan Köse'nin raporunu açtığında 3 SEKME göreceksin:")
        print(f"   1. Birleşik (120 + 320)")
        print(f"   2. 320 - Satıcılar (113 işlem)")
        print(f"   3. 120 - Müşteriler (41 işlem)")
    else:
        print(f"\n❌ Oluşturulamadı!")
else:
    print(f"\n❌ 320.00547 contact bulunamadı!")

db.close()
