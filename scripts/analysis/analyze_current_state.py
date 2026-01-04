"""
Mevcut veri yapısını analiz eder:
1. Transaction document types
2. 191 hesap kullanımı
3. KDV oranları
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 80)
print("1. TOPLAM TRANSACTION SAYISI")
print("=" * 80)
result = session.execute(text("SELECT COUNT(*) FROM transactions")).fetchone()
print(f"Toplam: {result[0]:,} adet\n")

print("=" * 80)
print("2. DOCUMENT_TYPE DAĞILIMI (İlk 30)")
print("=" * 80)
result = session.execute(text("""
    SELECT document_type, COUNT(*) as cnt 
    FROM transactions 
    WHERE document_type IS NOT NULL 
    GROUP BY document_type 
    ORDER BY cnt DESC 
    LIMIT 30
"""))
for row in result:
    print(f"{row[0]:50s} {row[1]:>6,} adet")

print("\n" + "=" * 80)
print("3. DOCUMENT_SUBTYPE DAĞILIMI (İlk 30)")
print("=" * 80)
result = session.execute(text("""
    SELECT document_subtype, COUNT(*) as cnt 
    FROM transactions 
    WHERE document_subtype IS NOT NULL 
    GROUP BY document_subtype 
    ORDER BY cnt DESC 
    LIMIT 30
"""))
for row in result:
    print(f"{row[0]:50s} {row[1]:>6,} adet")

print("\n" + "=" * 80)
print("4. 191 HESAP KULLANIMI")
print("=" * 80)
result = session.execute(text("""
    SELECT a.code, a.name, COUNT(DISTINCT tl.transaction_id) as transaction_count, 
           SUM(tl.debit) as total_debit, SUM(tl.credit) as total_credit
    FROM accounts a
    JOIN transaction_lines tl ON a.id = tl.account_id
    WHERE a.code LIKE '191%'
    GROUP BY a.id, a.code, a.name
    ORDER BY a.code
"""))
print(f"{'Hesap Kodu':<15} {'Hesap Adı':<40} {'İşlem':<10} {'BORÇ':<15} {'ALACAK':<15}")
print("-" * 95)
for row in result:
    print(f"{row[0]:<15} {row[1]:<40} {row[2]:<10,} {float(row[3] or 0):>15,.2f} {float(row[4] or 0):>15,.2f}")

print("\n" + "=" * 80)
print("5. KDV ORANLARI (transaction_lines.vat_rate)")
print("=" * 80)
result = session.execute(text("""
    SELECT 
        vat_rate,
        COUNT(*) as usage_count,
        SUM(debit) as total_debit,
        SUM(credit) as total_credit
    FROM transaction_lines
    WHERE vat_rate IS NOT NULL AND vat_rate > 0
    GROUP BY vat_rate
    ORDER BY vat_rate
"""))
print(f"{'KDV Oranı':<15} {'Kullanım':<10} {'BORÇ':<20} {'ALACAK':<20}")
print("-" * 65)
for row in result:
    vat_pct = float(row[0] or 0) * 100
    print(f"%{vat_pct:<14.2f} {row[1]:<10,} {float(row[2] or 0):>20,.2f} {float(row[3] or 0):>20,.2f}")

print("\n" + "=" * 80)
print("6. TEVKİFAT ORANLARI (withholding_rate)")
print("=" * 80)
result = session.execute(text("""
    SELECT 
        withholding_rate,
        COUNT(*) as usage_count,
        SUM(debit) as total_debit,
        SUM(credit) as total_credit
    FROM transaction_lines
    WHERE withholding_rate IS NOT NULL AND withholding_rate > 0
    GROUP BY withholding_rate
    ORDER BY withholding_rate
"""))
print(f"{'Tevkifat Oranı':<15} {'Kullanım':<10} {'BORÇ':<20} {'ALACAK':<20}")
print("-" * 65)
for row in result:
    tevk_pct = float(row[0] or 0) * 100
    print(f"%{tevk_pct:<14.2f} {row[1]:<10,} {float(row[2] or 0):>20,.2f} {float(row[3] or 0):>20,.2f}")

print("\n" + "=" * 80)
print("7. E-FATURA SAYISI")
print("=" * 80)
result = session.execute(text("SELECT COUNT(*) FROM einvoices"))
print(f"Toplam e-fatura: {result.fetchone()[0]:,} adet")

session.close()
print("\n" + "=" * 80)
print("ANALİZ TAMAMLANDI")
print("=" * 80)
