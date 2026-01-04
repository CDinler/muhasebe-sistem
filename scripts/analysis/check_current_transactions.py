from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 80)
print("DATABASE'DEKİ MEVCUT 335 TRANSACTION_LINES KONTROLÜ")
print("=" * 80)

# En çok kullanılan 335 hesaplar
result = db.execute(text("""
    SELECT 
        a.code,
        a.name,
        COUNT(tl.id) as tx_count,
        SUM(tl.debit) as total_debit,
        SUM(tl.credit) as total_credit
    FROM accounts a
    JOIN transaction_lines tl ON tl.account_id = a.id
    WHERE a.code LIKE '335.%'
    GROUP BY a.code, a.name
    HAVING COUNT(tl.id) > 0
    ORDER BY tx_count DESC
    LIMIT 30
""")).fetchall()

print("\nEn çok kullanılan 30 personel hesabı:")
print("-" * 80)
print(f"{'Hesap Kodu':<20} {'Ad Soyad':<30} {'TX':<8} {'Borç':<15} {'Alacak':<15}")
print("-" * 80)

for r in result:
    print(f"{r.code:<20} {r.name[:30]:<30} {r.tx_count:<8} {r.total_debit:>14,.2f} {r.total_credit:>14,.2f}")

# Toplam istatistikler
stats = db.execute(text("""
    SELECT 
        COUNT(DISTINCT a.id) as unique_accounts,
        COUNT(tl.id) as total_transactions,
        SUM(tl.debit) as total_debit,
        SUM(tl.credit) as total_credit
    FROM accounts a
    JOIN transaction_lines tl ON tl.account_id = a.id
    WHERE a.code LIKE '335.%'
""")).first()

print("\n" + "=" * 80)
print("TOPLAM İSTATİSTİKLER")
print("=" * 80)
print(f"Transaction olan 335 hesap sayısı: {stats.unique_accounts}")
print(f"Toplam 335 transaction_lines: {stats.total_transactions}")
print(f"Toplam Borç: {stats.total_debit:,.2f} TL")
print(f"Toplam Alacak: {stats.total_credit:,.2f} TL")
print(f"Net Bakiye: {(stats.total_debit - stats.total_credit):,.2f} TL")

# Transaction olmayan 335 hesaplar
empty_accounts = db.execute(text("""
    SELECT COUNT(*) as count
    FROM accounts a
    LEFT JOIN transaction_lines tl ON tl.account_id = a.id
    WHERE a.code LIKE '335.%'
    AND tl.id IS NULL
""")).scalar()

print(f"\nTransaction OLMAYAN 335 hesap: {empty_accounts}")

db.close()
print("\n" + "=" * 80)
