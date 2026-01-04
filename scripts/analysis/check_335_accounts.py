"""335 Personel hesaplarını kontrol et"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 335 hesap sayısı
result = db.execute(text("SELECT COUNT(*) FROM accounts WHERE code LIKE '335.%'"))
count = result.fetchone()[0]
print(f"=" * 60)
print(f"335 HESAP KONTROLÜ")
print(f"=" * 60)
print(f"Toplam 335 hesap sayısı: {count}")

# Örnek hesaplar
sample = db.execute(text("""
    SELECT code, name 
    FROM accounts 
    WHERE code LIKE '335.%' 
    ORDER BY code 
    LIMIT 10
""")).fetchall()

print(f"\nİlk 10 örnek 335 hesap:")
for row in sample:
    print(f"  {row[0]:20} - {row[1]:40}")

# Transaction_lines kontrolü
tx_result = db.execute(text("""
    SELECT COUNT(DISTINCT tl.account_id) as hesap_sayisi, 
           COUNT(*) as kayit_sayisi
    FROM transaction_lines tl
    JOIN accounts a ON a.id = tl.account_id
    WHERE a.code LIKE '335.%'
""")).fetchone()

print(f"\nTransaction_lines'da 335 hesaplar:")
print(f"  Hareket görmüş hesap sayısı: {tx_result[0]}")
print(f"  Toplam kayıt sayısı: {tx_result[1]}")

# Personnel tablosunda account_id kontrolü
pers_result = db.execute(text("""
    SELECT 
        COUNT(*) as toplam_personel,
        COUNT(account_id) as hesap_atanmis,
        COUNT(*) - COUNT(account_id) as hesap_atanmamis
    FROM personnel
""")).fetchone()

print(f"\nPersonnel tablosu:")
print(f"  Toplam personel: {pers_result[0]}")
print(f"  Hesap atanmış: {pers_result[1]}")
print(f"  Hesap atanmamış: {pers_result[2]}")

# Personnel - Account eşleşmesi
matched = db.execute(text("""
    SELECT 
        p.tckn,
        p.first_name,
        p.last_name,
        a.code,
        a.name
    FROM personnel p
    LEFT JOIN accounts a ON a.id = p.account_id
    WHERE p.tckn IS NOT NULL
    ORDER BY p.first_name, p.last_name
    LIMIT 5
""")).fetchall()

print(f"\nİlk 5 personel - hesap eşleşmesi:")
for row in matched:
    print(f"  {row[0]} - {row[1]} {row[2]:20} -> {row[3] or 'HESAP YOK'}")

db.close()
print(f"=" * 60)
