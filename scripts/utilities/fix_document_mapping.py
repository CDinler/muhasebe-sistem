"""
Document type mapping'i düzeltir.
UTF-8 karakterlerle çalışır.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 100)
print("DOCUMENT TYPE MAPPING DÜZELTİLİYOR")
print("=" * 100)

# 1. Tüm mappingleri temizle
session.execute(text("""
    UPDATE document_type_mapping 
    SET new_document_type_id = NULL, 
        new_document_subtype_id = NULL,
        is_verified = FALSE
"""))
session.commit()
print("\n✅ Eski mappingler temizlendi")

# 2. Document Type Mappings
type_mappings = {
    'BANKA TEDİYE FİŞİ': 'BANKA_TEDIYE',
    'BORDRO': 'BORDRO',
    'KASA TAHSİLAT FİŞİ': 'KASA_TAHSILAT',
    'ALIŞ FATURASI': 'ALIS_FATURA',
    'BANKA TAHSİLAT FİŞİ': 'BANKA_TAHSILAT',
    'SATIŞ FATURASI': 'SATIS_FATURA',
    'YEVMİYE FİŞİ': 'YEVMIYE',
    'HAKEDİŞ RAPORU': 'HAKEDIS',
    'VERİLEN ÇEK': 'VERILEN_CEK',
    'ÇEK TAHSİLAT/ÖDEME': 'CEK_TAHSILAT_ODEME',
    'ALINAN ÇEK': 'ALINAN_CEK',
}

print("\n" + "=" * 100)
print("DOCUMENT TYPE MAPPINGLER")
print("=" * 100)

total_updated = 0
for old_type, code in type_mappings.items():
    result = session.execute(text("""
        UPDATE document_type_mapping m
        SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = :code LIMIT 1)
        WHERE m.old_document_type = :old_type
    """), {'code': code, 'old_type': old_type})
    
    count = result.rowcount
    total_updated += count
    status = "✅" if count > 0 else "⚠️"
    print(f"{status} {old_type:<30} -> {code:<25} ({count} kayıt)")
    
session.commit()
print(f"\nToplam güncellenen type mapping: {total_updated}")

# 3. Document Subtype Mappings
subtype_mappings = {
    'EFT/Havale': 'EFT_HAVALE',
    'Personel Ödemesi': 'PERSONEL_ODEME',
    'Nakit': 'NAKIT',
    'E-Fatura': 'E_FATURA',
    'Kredi Kartı': 'KREDI_KARTI',
    'E-Arşiv': 'E_ARSIV',
    'Düzeltme/Mahsup': 'DUZELTME_MAHSUP',
    'Tedarikçi Çeki': 'TEDARIKCI_CEKI',
    'Kağıt/Matbu': 'KAGIT_MATBU',
    'Müşteri Çeki': 'MUSTERI_CEKI',
    'Ödeme': 'ODEME',
    'Serbest Meslek Makbuzu': 'SMM',
    'Dekont': 'DEKONT',
}

print("\n" + "=" * 100)
print("DOCUMENT SUBTYPE MAPPINGLER")
print("=" * 100)

total_updated = 0
for old_subtype, code in subtype_mappings.items():
    result = session.execute(text("""
        UPDATE document_type_mapping m
        SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = :code LIMIT 1)
        WHERE m.old_document_subtype = :old_subtype
    """), {'code': code, 'old_subtype': old_subtype})
    
    count = result.rowcount
    total_updated += count
    status = "✅" if count > 0 else "⚠️"
    print(f"{status} {old_subtype:<30} -> {code:<25} ({count} kayıt)")
    
session.commit()
print(f"\nToplam güncellenen subtype mapping: {total_updated}")

# 4. Verified flag'i set et
session.execute(text("""
    UPDATE document_type_mapping
    SET is_verified = TRUE
    WHERE new_document_type_id IS NOT NULL 
      AND new_document_subtype_id IS NOT NULL
"""))
session.commit()

# 5. Özet istatistikler
print("\n" + "=" * 100)
print("ÖZET İSTATİSTİKLER")
print("=" * 100)

stats = session.execute(text("""
    SELECT 
        COUNT(*) as total_mappings,
        SUM(record_count) as total_records,
        SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN 1 ELSE 0 END) as complete_mappings,
        SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN record_count ELSE 0 END) as complete_records,
        SUM(CASE WHEN is_verified = 1 THEN 1 ELSE 0 END) as verified_mappings
    FROM document_type_mapping
""")).fetchone()

print(f"\nToplam Mapping: {stats[0]}")
print(f"Tamamlanan Mapping: {stats[2]} / {stats[0]} ({stats[2]*100/stats[0]:.1f}%)")
print(f"\nToplam Kayıt: {stats[1]:,}")
print(f"Eşlenen Kayıt: {stats[3]:,} / {stats[1]:,} ({stats[3]*100/stats[1]:.1f}%)")
print(f"\nDoğrulanmış Mapping: {stats[4]}")

# 6. Eksikler
missing = session.execute(text("""
    SELECT old_document_type, old_document_subtype, record_count
    FROM document_type_mapping
    WHERE (new_document_type_id IS NULL OR new_document_subtype_id IS NULL)
      AND record_count > 0
    ORDER BY record_count DESC
""")).fetchall()

if missing:
    print("\n" + "=" * 100)
    print("⚠️  EKSİK MAPPINGLER")
    print("=" * 100)
    for row in missing:
        old_type = row[0] or '(NULL)'
        old_subtype = row[1] or '(NULL)'
        print(f"  {old_type:<35} + {old_subtype:<35} ({row[2]:,} kayıt)")
else:
    print("\n✅ TÜM MAPPINGLER TAMAMLANDI!")

session.close()
