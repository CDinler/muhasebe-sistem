import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text, func
from app.models.contact import Contact

db = SessionLocal()
db.bind.echo = False

print("=" * 80)
print("AYNI İSME SAHİP FARKLI HESAP KODLU CARİLER")
print("=" * 80)

# Aynı isimde birden fazla contact olan durumlar
duplicates = db.query(
    func.lower(func.trim(Contact.name)).label('normalized_name'),
    func.count(Contact.id).label('count')
).group_by(
    func.lower(func.trim(Contact.name))
).having(
    func.count(Contact.id) > 1
).limit(10).all()

if duplicates:
    print(f"\n✅ {len(duplicates)} isimde duplike var:\n")
    for dup in duplicates:
        print(f"İsim: {dup.normalized_name} ({dup.count} adet)")
        
        # Bu isimdeki tüm contact'ları getir
        contacts = db.query(Contact).filter(
            func.lower(func.trim(Contact.name)) == dup.normalized_name
        ).all()
        
        has_120 = any(c.code and c.code.startswith('120') for c in contacts)
        has_320 = any(c.code and c.code.startswith('320') for c in contacts)
        
        for c in contacts:
            print(f"  - ID: {c.id}, Code: {c.code}, Type: {c.contact_type}")
        
        if has_120 and has_320:
            print(f"  ✅ HEM 120 HEM 320 VAR!")
        print()
else:
    print("\n❌ Aynı isimde birden fazla contact yok")

# Manuel olarak bir contact oluşturalım test için
print("\n" + "=" * 80)
print("TEST: Bir carinin hem 120 hem 320 hesabını oluşturalım")
print("=" * 80)

# İlk contact'ı al
first_contact = db.query(Contact).filter(
    Contact.code.like('320.%')
).first()

if first_contact:
    print(f"\nMevcut: {first_contact.id} - {first_contact.code} - {first_contact.name}")
    
    # Aynı isimde 120'li hesap var mı?
    matching_120 = db.query(Contact).filter(
        Contact.code.like('120.%'),
        func.lower(func.trim(Contact.name)) == func.lower(func.trim(first_contact.name))
    ).first()
    
    if matching_120:
        print(f"Eşleşen 120: {matching_120.id} - {matching_120.code} - {matching_120.name}")
        print("\n✅ Bu cari için rapor açınca 3 sekme göreceksin!")
    else:
        print("\n⚠️ Aynı isimde 120'li hesap yok")
        print("   Raporlar sayfasında test etmek için önce bir cari oluştur:")
        print(f"   İsim: {first_contact.name}")
        print(f"   Kod: 120.XXXXX (otomatik)")
        print(f"   Tip: Müşteri")

db.close()
