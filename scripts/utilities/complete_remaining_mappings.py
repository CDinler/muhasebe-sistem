"""
Kalan 2 eksik mapping'i tamamlar.
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

# 1. HAKEDİŞ RAPORU + NULL subtype -> HAKEDIS + KAGIT_MATBU
result1 = session.execute(text("""
    UPDATE document_type_mapping m
    SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'KAGIT_MATBU' LIMIT 1)
    WHERE m.old_document_type = 'HAKEDİŞ RAPORU' 
      AND (m.old_document_subtype IS NULL OR m.old_document_subtype = '')
"""))
print(f"✅ HAKEDİŞ RAPORU mappingi tamamlandı: {result1.rowcount} kayıt")

# 2. NULL type + Kağıt/Matbu -> YEVMIYE + KAGIT_MATBU
result2 = session.execute(text("""
    UPDATE document_type_mapping m
    SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'YEVMIYE' LIMIT 1)
    WHERE (m.old_document_type IS NULL OR m.old_document_type = '')
      AND m.old_document_subtype = 'Kağıt/Matbu'
"""))
print(f"✅ NULL + Kağıt/Matbu mappingi tamamlandı: {result2.rowcount} kayıt")

# 3. Verified flag
result3 = session.execute(text("""
    UPDATE document_type_mapping
    SET is_verified = TRUE
    WHERE new_document_type_id IS NOT NULL 
      AND new_document_subtype_id IS NOT NULL 
      AND is_verified = FALSE
"""))
print(f"✅ Verified flag güncellendi: {result3.rowcount} kayıt")

session.commit()

# 4. Son kontrol
stats = session.execute(text("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN 1 ELSE 0 END) as complete,
        SUM(record_count) as total_records,
        SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN record_count ELSE 0 END) as complete_records
    FROM document_type_mapping
""")).fetchone()

print("\n" + "=" * 80)
print("FİNAL DURUM")
print("=" * 80)
print(f"Mapping Tamamlama: {stats[1]} / {stats[0]} ({stats[1]*100/stats[0]:.1f}%)")
print(f"Kayıt Eşleştirme: {stats[3]:,} / {stats[2]:,} ({stats[3]*100/stats[2]:.1f}%)")

if stats[1] == stats[0]:
    print("\n🎉 TÜM MAPPINGLER %100 TAMAMLANDI!")
else:
    print(f"\n⚠️  {stats[0] - stats[1]} mapping hâlâ eksik")

session.close()
