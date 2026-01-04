"""
Türkcell fatura kayıtlarını analiz eder.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 100)
print("TÜRKCELL FATURA KAYITLARI ANALİZİ")
print("=" * 100)

# 1. Description'da Türkcell geçen kayıtlar
query = text("""
    SELECT 
        t.id,
        t.transaction_number,
        t.transaction_date,
        t.description,
        t.document_type,
        t.document_subtype,
        GROUP_CONCAT(CONCAT(a.code, ': ', tl.debit, '/', tl.credit) SEPARATOR ' | ') as entries
    FROM transactions t
    LEFT JOIN transaction_lines tl ON t.id = tl.transaction_id
    LEFT JOIN accounts a ON tl.account_id = a.id
    WHERE LOWER(t.description) LIKE '%türkcell%' 
       OR LOWER(t.description) LIKE '%turkcell%'
    GROUP BY t.id
    ORDER BY t.transaction_date DESC
    LIMIT 20
""")

results = session.execute(query).fetchall()

if results:
    print(f"\n{len(results)} işlem bulundu (son 20):\n")
    for row in results:
        print(f"ID: {row[0]}")
        print(f"Fiş No: {row[1]}")
        print(f"Tarih: {row[2]}")
        print(f"Açıklama: {row[3][:100]}")
        print(f"Evrak: {row[4]} / {row[5]}")
        print(f"Kayıtlar: {row[6][:150]}")
        print("-" * 100)
else:
    print("\n❌ Türkcell ile ilgili kayıt bulunamadı")

# 2. İstatistikler
stats_query = text("""
    SELECT 
        COUNT(*) as toplam,
        COUNT(DISTINCT t.transaction_date) as farkli_gun,
        MIN(t.transaction_date) as ilk_tarih,
        MAX(t.transaction_date) as son_tarih,
        SUM(tl.debit) as toplam_borc,
        SUM(tl.credit) as toplam_alacak
    FROM transactions t
    LEFT JOIN transaction_lines tl ON t.id = tl.transaction_id
    WHERE LOWER(t.description) LIKE '%türkcell%' 
       OR LOWER(t.description) LIKE '%turkcell%'
""")

stats = session.execute(stats_query).fetchone()

if stats and stats[0] > 0:
    print("\n" + "=" * 100)
    print("İSTATİSTİKLER")
    print("=" * 100)
    print(f"Toplam İşlem: {stats[0]}")
    print(f"Farklı Gün: {stats[1]}")
    print(f"İlk Tarih: {stats[2]}")
    print(f"Son Tarih: {stats[3]}")
    print(f"Toplam Borç: {stats[4]:,.2f} TL")
    print(f"Toplam Alacak: {stats[5]:,.2f} TL")

session.close()
