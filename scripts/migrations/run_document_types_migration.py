"""
Document types migration'ı çalıştır
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Migration dosyasını oku
migration_file = r"c:\Projects\muhasebe-sistem\database\migrations\20251230_comprehensive_document_types.sql"

print("📋 Document Types Migration'ı Çalıştırılıyor...\n")

with open(migration_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# SQL'i satırlara böl ve çalıştır
with engine.connect() as conn:
    try:
        # Transaction başlat
        trans = conn.begin()
        
        # SQL'i noktalı virgüle göre ayır
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        executed = 0
        for statement in statements:
            if statement and len(statement) > 10:  # Boş satırları atla
                try:
                    conn.execute(text(statement))
                    executed += 1
                except Exception as e:
                    if 'does not exist' not in str(e):  # Tablo yoksa hatası önemli değil
                        print(f"⚠️  Uyarı: {str(e)[:100]}")
        
        trans.commit()
        print(f"✅ {executed} SQL ifadesi başarıyla çalıştırıldı\n")
        
        # Kontrol
        result = conn.execute(text("SELECT COUNT(*) FROM document_types"))
        doc_types_count = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM document_subtypes"))
        subtypes_count = result.scalar()
        
        print(f"📊 Sonuç:")
        print(f"   • Ana Evrak Türü: {doc_types_count}")
        print(f"   • Alt Evrak Türü: {subtypes_count}")
        
        # İlk 10 kaydı göster
        print(f"\n📋 İlk 10 Ana Evrak Türü:")
        result = conn.execute(text("SELECT code, name, category FROM document_types ORDER BY sort_order LIMIT 10"))
        for row in result:
            print(f"   • {row[0]:25} - {row[1]:40} ({row[2]})")
            
    except Exception as e:
        trans.rollback()
        print(f"❌ Hata: {e}")
        raise

print("\n✨ Migration tamamlandı!")
