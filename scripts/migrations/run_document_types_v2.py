"""
YENİ Document Types Migration'ı Çalıştır (v2)
34 ana tür + 74 alt tür
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

migration_file = r"c:\Projects\muhasebe-sistem\database\migrations\20260101_comprehensive_document_types_v2.sql"

print("📋 YENİ Document Types Migration (v2) Çalıştırılıyor...\n")
print("   • 34 Ana Evrak Türü")
print("   • 74 Alt Evrak Türü")
print("   • YEVMIYE_KAYDI_SABLONU.md'ye uygun\n")

with open(migration_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

with engine.connect() as conn:
    try:
        # SQL statement'ları ayır (noktalı virgül ile)
        statements = []
        for stmt in sql_content.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
        
        # Her statement'ı ayrı ayrı çalıştır
        for i, statement in enumerate(statements, 1):
            try:
                conn.execute(text(statement))
                conn.commit()
            except Exception as e:
                print(f"❌ Statement {i} hatası: {e}")
                conn.rollback()
                raise
        
        print("✅ Migration başarıyla çalıştırıldı!\n")
        
        # Kontrol
        result = conn.execute(text("SELECT COUNT(*) FROM document_types"))
        doc_types_count = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM document_subtypes"))
        subtypes_count = result.scalar()
        
        print(f"📊 Sonuç:")
        print(f"   • Ana Evrak Türü: {doc_types_count}")
        print(f"   • Alt Evrak Türü: {subtypes_count}\n")
        
        # Kategorilere göre dağılım
        print("📋 Kategorilere Göre Dağılım:")
        result = conn.execute(text("""
            SELECT category, COUNT(*) as count 
            FROM document_types 
            GROUP BY category 
            ORDER BY category
        """))
        for row in result:
            print(f"   • {row[0]:15} → {row[1]:2} ana tür")
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        raise

print("\n✨ Tamamlandı!")
