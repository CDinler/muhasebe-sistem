"""
Document types Türkçe karakter kontrolü
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import SessionLocal
from app.models.document_type import DocumentType

db = SessionLocal()

print("🔍 Document Types - Türkçe Karakter Kontrolü\n")

# Türkçe karakter içeren kayıtları kontrol et
test_codes = ['ALIS_FATURA', 'SATIS_FATURA', 'IADE_FATURA', 'HAKEDIS_FATURA']

for code in test_codes:
    doc_type = db.query(DocumentType).filter(DocumentType.code == code).first()
    if doc_type:
        print(f"✅ {doc_type.code:25} → {doc_type.name}")
        # Türkçe karakterleri kontrol et
        has_turkish = any(c in doc_type.name for c in 'ışğüöçİŞĞÜÖÇ')
        if has_turkish:
            print(f"   ✓ Türkçe karakter algılandı")
    else:
        print(f"❌ {code} bulunamadı")
    print()

# Toplam sayı
total = db.query(DocumentType).count()
print(f"📊 Toplam Ana Evrak Türü: {total}")

db.close()
