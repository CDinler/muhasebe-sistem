from sqlalchemy import create_engine, text
import os

print("📋 Document Types Güvenli Güncelleme (Mevcut Kayıtları Koruyarak)")
print("=" * 80)

# Database connection from .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

# SQL dosyasını oku
sql_file_path = os.path.join(os.path.dirname(__file__), '../database/migrations/20260101_update_document_types_safe.sql')
with open(sql_file_path, 'r', encoding='utf-8') as f:
    sql_content = f.read()

with engine.connect() as conn:
    try:
        # SQL statement'ları ayır
        statements = []
        for stmt in sql_content.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--') and len(stmt) > 10:
                statements.append(stmt)
        
        print(f"\n🔄 {len(statements)} SQL statement çalıştırılıyor...\n")
        
        # Her statement'ı ayrı ayrı çalıştır
        success_count = 0
        for i, statement in enumerate(statements, 1):
            try:
                result = conn.execute(text(statement))
                conn.commit()
                
                # İlk 50 karakteri göster
                preview = statement[:50].replace('\n', ' ')
                if result.rowcount > 0:
                    print(f"  ✅ ({i}/{len(statements)}) {result.rowcount} kayıt: {preview}...")
                    success_count += 1
                else:
                    print(f"  ℹ️  ({i}/{len(statements)}) Değişiklik yok: {preview}...")
                    
            except Exception as e:
                print(f"  ⚠️  ({i}/{len(statements)}) Hata (devam ediliyor): {str(e)[:80]}")
                conn.rollback()
        
        print(f"\n✅ Migration tamamlandı! {success_count}/{len(statements)} statement başarılı\n")
        
        # Kontrol: Toplam evrak türü sayısı
        total_types = conn.execute(text("SELECT COUNT(*) FROM document_types")).scalar()
        print(f"📊 Toplam document_types: {total_types}")
        
        # Kategori bazlı dağılım
        print("\n📊 Kategori bazlı dağılım:")
        categories = conn.execute(text("""
            SELECT category, COUNT(*) as count
            FROM document_types
            GROUP BY category
            ORDER BY category
        """)).fetchall()
        for cat in categories:
            print(f"  {cat[0]}: {cat[1]} evrak türü")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
        raise
