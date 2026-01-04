from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 60)
print("335 PERSONEL HESAP RAPOR KONTROLÜ")
print("=" * 60)

# 1. Personnel-Account ilişkisini kontrol et
print("\n1️⃣ Personnel -> Account (335) ilişkileri (ilk 10):")
print("-" * 60)
result = db.execute(text("""
    SELECT 
        p.tckn,
        CONCAT(p.first_name, ' ', p.last_name) as ad,
        a.code,
        a.name
    FROM personnel p
    JOIN accounts a ON p.account_id = a.id
    WHERE a.code LIKE '335.%'
    ORDER BY a.code
    LIMIT 10
""")).fetchall()

for r in result:
    print(f"{r[0]} | {r[1]:30} | {r[2]:15} | {r[3]}")

# 2. 335 Hesap sayılarını kontrol et
print("\n2️⃣ 335 Hesap İstatistikleri:")
print("-" * 60)
stats = db.execute(text("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN code REGEXP '^335\\.[0-9]{11}$' THEN 1 END) as yeni_format,
        COUNT(CASE WHEN code REGEXP '^335\\.[0-9]{5}$' THEN 1 END) as eski_format,
        COUNT(CASE WHEN name LIKE '%ESKİ%' THEN 1 END) as eski_isimli
    FROM accounts
    WHERE code LIKE '335.%'
""")).first()

print(f"Toplam 335 hesap: {stats.total}")
print(f"YENİ format (335.TCKN): {stats.yeni_format}")
print(f"ESKİ format (335.00001): {stats.eski_format}")
print(f"'ESKİ' isimli: {stats.eski_isimli}")

# 3. Transaction_lines kontrolü
print("\n3️⃣ Transaction Lines (335 hesaplarda):")
print("-" * 60)
tx_stats = db.execute(text("""
    SELECT 
        a.code,
        COUNT(tl.id) as tx_count,
        SUM(tl.debit) as total_debit,
        SUM(tl.credit) as total_credit
    FROM accounts a
    LEFT JOIN transaction_lines tl ON tl.account_id = a.id
    WHERE a.code LIKE '335.%'
    GROUP BY a.code
    HAVING COUNT(tl.id) > 0
    ORDER BY tx_count DESC
    LIMIT 5
""")).fetchall()

print("En çok transaction olan 335 hesaplar:")
for r in tx_stats:
    print(f"{r[0]:15} | TX: {r[1]:5} | Borç: {r[2]:12.2f} | Alacak: {r[3]:12.2f}")

# 4. Personnel tablosunda account_id NULL olanlar
print("\n4️⃣ Personnel (account_id NULL olanlar):")
print("-" * 60)
null_count = db.execute(text("""
    SELECT COUNT(*) 
    FROM personnel 
    WHERE account_id IS NULL
""")).scalar()

print(f"Hesabı olmayan personel: {null_count}")

# 5. Rapor sorgusu TEST (get_personnel_accounts_excel mantığı)
print("\n5️⃣ RAPOR SORGUSU TESTİ (2025-11 bordrosu):")
print("-" * 60)

# Bakiye hesaplama (rapordaki sorgu)
balances = db.execute(text("""
    SELECT 
        a.code,
        SUM(tl.debit) as total_debit,
        SUM(tl.credit) as total_credit,
        SUM(tl.debit) - SUM(tl.credit) as balance
    FROM accounts a
    LEFT JOIN transaction_lines tl ON tl.account_id = a.id
    WHERE a.code LIKE '335.%'
    GROUP BY a.code
    HAVING SUM(tl.debit) - SUM(tl.credit) != 0
    ORDER BY balance DESC
    LIMIT 5
""")).fetchall()

print("En yüksek bakiyeli 335 hesaplar:")
for r in balances:
    print(f"{r[0]:15} | Borç: {r[1]:12.2f} | Alacak: {r[2]:12.2f} | Bakiye: {r[3]:12.2f}")

# 6. 2025-11 Bordrosu + Personnel + Account JOIN
print("\n6️⃣ 2025-11 Bordro + Personnel (ilk 5):")
print("-" * 60)
from app.models.personnel import Personnel
from app.models.luca_bordro import LucaBordro
from app.models.account import Account

query = db.query(
    Personnel.tckn,
    Personnel.first_name,
    Personnel.last_name,
    Account.code,
    Account.name
).join(
    LucaBordro, Personnel.tckn == LucaBordro.tckn
).outerjoin(
    Account, Personnel.account_id == Account.id
).filter(
    LucaBordro.donem == '2025-11'
).distinct().order_by(
    Personnel.first_name,
    Personnel.last_name
).limit(5).all()

for p in query:
    print(f"{p.tckn} | {p.first_name} {p.last_name:20} | {p.code or 'HESAP YOK':15} | {p.name or ''}")

db.close()

print("\n" + "=" * 60)
print("KONTROL TAMAMLANDI")
print("=" * 60)
