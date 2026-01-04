"""
Mevcut document_type ve document_subtype değerlerini analiz eder.
Migration planı için veri kalitesini değerlendirir.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from app.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 100)
print("EVRAK TİPİ ANALİZ RAPORU")
print("=" * 100)

# 1. Toplam kayıt sayısı
total_query = text("SELECT COUNT(*) as total FROM transactions")
total_result = session.execute(total_query).fetchone()
print(f"\n1. TOPLAM İŞLEM SAYISI: {total_result[0]:,}")

# 2. document_type dağılımı
print("\n" + "=" * 100)
print("2. DOCUMENT_TYPE DAĞILIMI")
print("=" * 100)
type_query = text("""
    SELECT 
        document_type,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) as percentage
    FROM transactions
    WHERE document_type IS NOT NULL AND document_type != ''
    GROUP BY document_type
    ORDER BY count DESC
    LIMIT 50
""")
type_results = session.execute(type_query).fetchall()
print(f"\n{'Document Type':<40} {'Sayı':>15} {'Yüzde':>10}")
print("-" * 70)
for row in type_results:
    print(f"{row[0]:<40} {row[1]:>15,} {row[2]:>9.2f}%")

# 3. document_subtype dağılımı
print("\n" + "=" * 100)
print("3. DOCUMENT_SUBTYPE DAĞILIMI")
print("=" * 100)
subtype_query = text("""
    SELECT 
        document_subtype,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) as percentage
    FROM transactions
    WHERE document_subtype IS NOT NULL AND document_subtype != ''
    GROUP BY document_subtype
    ORDER BY count DESC
    LIMIT 50
""")
subtype_results = session.execute(subtype_query).fetchall()
print(f"\n{'Document Subtype':<40} {'Sayı':>15} {'Yüzde':>10}")
print("-" * 70)
for row in subtype_results:
    print(f"{row[0]:<40} {row[1]:>15,} {row[2]:>9.2f}%")

# 4. Kombinasyon analizi
print("\n" + "=" * 100)
print("4. TİP + ALT TİP KOMBİNASYONLARI (En Yaygın 30)")
print("=" * 100)
combo_query = text("""
    SELECT 
        document_type,
        document_subtype,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) as percentage
    FROM transactions
    WHERE (document_type IS NOT NULL AND document_type != '')
       OR (document_subtype IS NOT NULL AND document_subtype != '')
    GROUP BY document_type, document_subtype
    ORDER BY count DESC
    LIMIT 30
""")
combo_results = session.execute(combo_query).fetchall()
print(f"\n{'Document Type':<30} {'Document Subtype':<30} {'Sayı':>15} {'Yüzde':>10}")
print("-" * 90)
for row in combo_results:
    doc_type = row[0] or '(NULL)'
    doc_subtype = row[1] or '(NULL)'
    print(f"{doc_type:<30} {doc_subtype:<30} {row[2]:>15,} {row[3]:>9.2f}%")

# 5. NULL/Boş değerler
print("\n" + "=" * 100)
print("5. NULL VE BOŞ DEĞER ANALİZİ")
print("=" * 100)
null_query = text("""
    SELECT 
        CASE 
            WHEN document_type IS NULL OR document_type = '' THEN 'Type NULL/Boş'
            ELSE 'Type Dolu'
        END as type_status,
        CASE 
            WHEN document_subtype IS NULL OR document_subtype = '' THEN 'Subtype NULL/Boş'
            ELSE 'Subtype Dolu'
        END as subtype_status,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) as percentage
    FROM transactions
    GROUP BY type_status, subtype_status
    ORDER BY count DESC
""")
null_results = session.execute(null_query).fetchall()
print(f"\n{'Type Durumu':<20} {'Subtype Durumu':<20} {'Sayı':>15} {'Yüzde':>10}")
print("-" * 70)
for row in null_results:
    print(f"{row[0]:<20} {row[1]:<20} {row[2]:>15,} {row[3]:>9.2f}%")

# 6. Veri kalitesi - problemli kayıtlar
print("\n" + "=" * 100)
print("6. VERİ KALİTESİ - PROBLEMLİ KAYITLAR")
print("=" * 100)

# Çok uzun değerler
long_query = text("""
    SELECT COUNT(*) as count
    FROM transactions
    WHERE LENGTH(document_type) > 50 OR LENGTH(document_subtype) > 50
""")
long_result = session.execute(long_query).fetchone()
print(f"\nÇok uzun değerler (>50 karakter): {long_result[0]:,}")

# Özel karakterli değerler
special_query = text("""
    SELECT COUNT(*) as count
    FROM transactions
    WHERE document_type REGEXP '[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ .-]'
       OR document_subtype REGEXP '[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ .-]'
""")
try:
    special_result = session.execute(special_query).fetchone()
    print(f"Özel karakterli değerler: {special_result[0]:,}")
except Exception as e:
    print(f"Özel karakter kontrolü başarısız (normal): {str(e)[:50]}")

# 7. "Gelen/Giden" pattern analizi
print("\n" + "=" * 100)
print("7. GELEN/GİDEN PATTERN ANALİZİ")
print("=" * 100)
pattern_query = text("""
    SELECT 
        CASE 
            WHEN document_type LIKE '%Gelen%' THEN 'Gelen içeren'
            WHEN document_type LIKE '%Giden%' THEN 'Giden içeren'
            WHEN document_type LIKE '%Alış%' THEN 'Alış içeren'
            WHEN document_type LIKE '%Satış%' THEN 'Satış içeren'
            ELSE 'Diğer'
        END as pattern,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE document_type IS NOT NULL AND document_type != ''), 2) as percentage
    FROM transactions
    WHERE document_type IS NOT NULL AND document_type != ''
    GROUP BY pattern
    ORDER BY count DESC
""")
pattern_results = session.execute(pattern_query).fetchall()
print(f"\n{'Pattern':<20} {'Sayı':>15} {'Yüzde':>10}")
print("-" * 50)
for row in pattern_results:
    print(f"{row[0]:<20} {row[1]:>15,} {row[2]:>9.2f}%")

# 8. E-Fatura/E-Arşiv analizi
print("\n" + "=" * 100)
print("8. E-FATURA/E-ARŞİV ANALİZİ")
print("=" * 100)
efatura_query = text("""
    SELECT 
        CASE 
            WHEN document_subtype LIKE '%E-Fatura%' OR document_subtype LIKE '%e-fatura%' THEN 'E-Fatura'
            WHEN document_subtype LIKE '%E-Arşiv%' OR document_subtype LIKE '%e-arşiv%' OR document_subtype LIKE '%E-Arsiv%' THEN 'E-Arşiv'
            WHEN document_subtype LIKE '%E-İrsaliye%' OR document_subtype LIKE '%e-irsaliye%' THEN 'E-İrsaliye'
            WHEN document_subtype LIKE '%E-SMM%' OR document_subtype LIKE '%e-smm%' THEN 'E-SMM'
            WHEN document_subtype IS NOT NULL AND document_subtype != '' THEN 'Diğer Alt Tip'
            ELSE 'Boş'
        END as e_doc_type,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) as percentage
    FROM transactions
    GROUP BY e_doc_type
    ORDER BY count DESC
""")
efatura_results = session.execute(efatura_query).fetchall()
print(f"\n{'E-Belge Tipi':<25} {'Sayı':>15} {'Yüzde':>10}")
print("-" * 55)
for row in efatura_results:
    print(f"{row[0]:<25} {row[1]:>15,} {row[2]:>9.2f}%")

# 9. Yıllara göre dağılım
print("\n" + "=" * 100)
print("9. YILLARA GÖRE EVRAK TİPİ KULLANIMI")
print("=" * 100)
year_query = text("""
    SELECT 
        YEAR(transaction_date) as year,
        COUNT(*) as total,
        SUM(CASE WHEN document_type IS NOT NULL AND document_type != '' THEN 1 ELSE 0 END) as with_type,
        ROUND(SUM(CASE WHEN document_type IS NOT NULL AND document_type != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as type_percentage
    FROM transactions
    WHERE transaction_date IS NOT NULL
    GROUP BY YEAR(transaction_date)
    ORDER BY year DESC
    LIMIT 10
""")
year_results = session.execute(year_query).fetchall()
print(f"\n{'Yıl':<10} {'Toplam':>15} {'Type Dolu':>15} {'Yüzde':>10}")
print("-" * 55)
for row in year_results:
    print(f"{row[0]:<10} {row[1]:>15,} {row[2]:>15,} {row[3]:>9.2f}%")

print("\n" + "=" * 100)
print("ANALİZ TAMAMLANDI")
print("=" * 100)
print("\nÖNERİLER:")
print("1. Mevcut veri kalitesini yukarıdaki tablolarda inceleyin")
print("2. Sık kullanılan kombinasyonları not edin")
print("3. Migration sırasında bu değerlerin yeni sisteme nasıl map edileceğini planlayın")
print("4. NULL/Boş kayıtlar için varsayılan değer belirleyin")
print("5. 'Gelen/Giden' → 'Alış/Satış' dönüşümü için mapping tablosu oluşturun")

session.close()
