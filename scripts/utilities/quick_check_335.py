from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 80)
print("335 PERSONEL HESAPLARI - HIZLI KONTROL")
print("=" * 80)

# 1. Hesap sayıları
print("\n1️⃣ HESAP SAYILARI:")
print("-" * 80)
result = db.execute(text("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN code REGEXP '^335\\.[0-9]{11}$' THEN 1 END) as yeni_format,
        COUNT(CASE WHEN code REGEXP '^335\\.[0-9]{5}$' THEN 1 END) as eski_format,
        COUNT(CASE WHEN name LIKE '%ESKİ%' THEN 1 END) as eski_isimli
    FROM accounts
    WHERE code LIKE '335.%'
""")).first()

print(f"📊 Toplam 335 hesap: {result.total}")
print(f"✅ YENİ format (335.TCKN - 11 haneli): {result.yeni_format}")
print(f"❌ ESKİ format (335.00001 - 5 haneli): {result.eski_format}")
print(f"❌ 'ESKİ' kelimesi içeren: {result.eski_isimli}")

# 2. Transaction sayıları
print("\n2️⃣ TRANSACTION SAYILARI:")
print("-" * 80)
tx_result = db.execute(text("""
    SELECT COUNT(*) 
    FROM transaction_lines tl 
    JOIN accounts a ON tl.account_id = a.id 
    WHERE a.code LIKE '335.%'
""")).scalar()

print(f"📊 335 hesaplardaki toplam transaction: {tx_result}")

# 3. Personnel - Account ilişkisi
print("\n3️⃣ PERSONNEL - ACCOUNT İLİŞKİSİ:")
print("-" * 80)
personnel_result = db.execute(text("""
    SELECT 
        COUNT(*) as total_personnel,
        COUNT(account_id) as with_account,
        COUNT(*) - COUNT(account_id) as without_account
    FROM personnel
""")).first()

print(f"📊 Toplam personel: {personnel_result.total_personnel}")
print(f"✅ Hesabı olan: {personnel_result.with_account}")
print(f"❌ Hesabı olmayan: {personnel_result.without_account}")

# 4. 2025-11 Bordrosunda kaç personel var?
print("\n4️⃣ 2025-11 BORDROSU:")
print("-" * 80)
bordro_result = db.execute(text("""
    SELECT COUNT(DISTINCT tckn) 
    FROM luca_bordro 
    WHERE donem = '2025-11'
""")).scalar()

print(f"📊 2025-11'de çalışan personel: {bordro_result}")

# 5. Rapor query'si ile eşleşme (2025-11 bordro + personnel + account)
print("\n5️⃣ RAPOR QUERY'Sİ (2025-11 Bordro + Personnel + Account):")
print("-" * 80)
rapor_result = db.execute(text("""
    SELECT 
        COUNT(DISTINCT p.tckn) as personel_sayisi,
        COUNT(DISTINCT CASE WHEN p.account_id IS NOT NULL THEN p.tckn END) as hesapli,
        COUNT(DISTINCT CASE WHEN p.account_id IS NULL THEN p.tckn END) as hesapsiz
    FROM personnel p
    INNER JOIN luca_bordro lb ON p.tckn = lb.tckn
    WHERE lb.donem = '2025-11'
""")).first()

print(f"📊 Rapordaki toplam personel: {rapor_result.personel_sayisi}")
print(f"✅ Hesabı olan: {rapor_result.hesapli}")
print(f"❌ Hesabı olmayan: {rapor_result.hesapsiz}")

# 6. İlk 5 personelin hesap bilgileri
print("\n6️⃣ ÖRNEK PERSONEL VERİLERİ (2025-11 bordrosundan):")
print("-" * 80)
sample = db.execute(text("""
    SELECT 
        p.tckn,
        CONCAT(p.first_name, ' ', p.last_name) as ad_soyad,
        a.code as hesap_kodu,
        a.name as hesap_adi
    FROM personnel p
    INNER JOIN luca_bordro lb ON p.tckn = lb.tckn
    LEFT JOIN accounts a ON p.account_id = a.id
    WHERE lb.donem = '2025-11'
    ORDER BY p.first_name, p.last_name
    LIMIT 5
""")).fetchall()

for row in sample:
    hesap = row.hesap_kodu if row.hesap_kodu else "❌ HESAP YOK"
    print(f"{row.tckn} | {row.ad_soyad:30} | {hesap}")

# 7. Hesabı olmayan personeller var mı?
print("\n7️⃣ HESABI OLMAYAN PERSONELLER (varsa):")
print("-" * 80)
no_account = db.execute(text("""
    SELECT 
        p.tckn,
        CONCAT(p.first_name, ' ', p.last_name) as ad_soyad
    FROM personnel p
    INNER JOIN luca_bordro lb ON p.tckn = lb.tckn
    WHERE lb.donem = '2025-11'
    AND p.account_id IS NULL
    LIMIT 10
""")).fetchall()

if no_account:
    print(f"⚠️ UYARI: {len(no_account)} personelin hesabı yok!")
    for row in no_account:
        print(f"  - {row.tckn} | {row.ad_soyad}")
else:
    print("✅ Tüm personellerin hesabı var!")

db.close()

print("\n" + "=" * 80)
print("KONTROL TAMAMLANDI")
print("=" * 80)
