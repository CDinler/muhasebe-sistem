"""
Document type mapping durumunu kontrol eder.
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

print("=" * 120)
print("DOCUMENT TYPE MAPPING DURUMU")
print("=" * 120)

# Tüm mappingleri göster
query = text("""
    SELECT 
        m.old_document_type,
        m.old_document_subtype,
        dt.name as new_type,
        ds.name as new_subtype,
        m.record_count,
        m.is_verified,
        CASE 
            WHEN m.new_document_type_id IS NULL THEN '❌ Type Eksik'
            WHEN m.new_document_subtype_id IS NULL THEN '❌ Subtype Eksik'
            WHEN m.is_verified = 1 THEN '✅ Verified'
            ELSE '⚠️  Otomatik'
        END as status
    FROM document_type_mapping m
    LEFT JOIN document_types dt ON m.new_document_type_id = dt.id
    LEFT JOIN document_subtypes ds ON m.new_document_subtype_id = ds.id
    ORDER BY m.record_count DESC
""")

results = session.execute(query).fetchall()

print(f"\n{'Eski Type':<30} {'Eski Subtype':<30} {'Yeni Type':<30} {'Yeni Subtype':<25} {'Kayıt':>8} {'Durum':<12}")
print("-" * 170)

for row in results:
    old_type = row[0] or '(NULL)'
    old_subtype = row[1] or '(NULL)'
    new_type = row[2] or '???'
    new_subtype = row[3] or '???'
    count = row[4]
    status = row[6]
    
    print(f"{old_type:<30} {old_subtype:<30} {new_type:<30} {new_subtype:<25} {count:>8,} {status:<12}")

# Özet istatistikler
print("\n" + "=" * 120)
print("ÖZET İSTATİSTİKLER")
print("=" * 120)

stats_query = text("""
    SELECT 
        COUNT(*) as total_mappings,
        SUM(record_count) as total_records,
        SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN 1 ELSE 0 END) as complete_mappings,
        SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN record_count ELSE 0 END) as complete_records,
        SUM(CASE WHEN is_verified = 1 THEN 1 ELSE 0 END) as verified_mappings,
        SUM(CASE WHEN is_verified = 1 THEN record_count ELSE 0 END) as verified_records
    FROM document_type_mapping
""")

stats = session.execute(stats_query).fetchone()

print(f"\nToplam Mapping Sayısı: {stats[0]}")
print(f"Toplam Kayıt Sayısı: {stats[1]:,}")
print(f"\nTamamlanmış Mappingler: {stats[2]} / {stats[0]} ({stats[2]*100/stats[0]:.1f}%)")
print(f"Tamamlanmış Kayıtlar: {stats[3]:,} / {stats[1]:,} ({stats[3]*100/stats[1]:.1f}%)")
print(f"\nDoğrulanmış Mappingler: {stats[4]} / {stats[0]} ({stats[4]*100/stats[0]:.1f}%)")
print(f"Doğrulanmış Kayıtlar: {stats[5]:,} / {stats[1]:,} ({stats[5]*100/stats[1]:.1f}%)")

# Eksik mappingler
print("\n" + "=" * 120)
print("EKSİK MAPPINGLER (Manuel Düzeltme Gerekebilir)")
print("=" * 120)

missing_query = text("""
    SELECT 
        old_document_type,
        old_document_subtype,
        record_count,
        CASE 
            WHEN new_document_type_id IS NULL THEN 'Type eksik'
            WHEN new_document_subtype_id IS NULL THEN 'Subtype eksik'
        END as problem
    FROM document_type_mapping
    WHERE (new_document_type_id IS NULL OR new_document_subtype_id IS NULL)
      AND record_count > 0
    ORDER BY record_count DESC
""")

missing = session.execute(missing_query).fetchall()

if missing:
    print(f"\n{'Eski Type':<35} {'Eski Subtype':<35} {'Kayıt':>10} {'Problem':<20}")
    print("-" * 105)
    for row in missing:
        old_type = row[0] or '(NULL)'
        old_subtype = row[1] or '(NULL)'
        print(f"{old_type:<35} {old_subtype:<35} {row[2]:>10,} {row[3]:<20}")
else:
    print("\n✅ Tüm mappingler tamamlanmış!")

session.close()
