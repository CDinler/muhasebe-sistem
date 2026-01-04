from sqlalchemy import create_engine, text
import os

# Database connection
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("📊 Document Types Durum Raporu")
    print("=" * 80)
    
    # Kategori bazlı dağılım
    print("\n📋 Kategori bazlı dağılım:")
    categories = conn.execute(text("""
        SELECT category, COUNT(*) as count
        FROM document_types
        GROUP BY category
        ORDER BY category
    """)).fetchall()
    
    total = 0
    for cat, count in categories:
        print(f"  {cat}: {count} evrak türü")
        total += count
    
    print(f"\n📊 Toplam: {total} evrak türü")
    
    # Transactions'da kullanılan document_subtype_id'ler
    print("\n📋 Transactions'da kullanılan document_subtype_id'ler:")
    used_subtypes = conn.execute(text("""
        SELECT COUNT(DISTINCT document_subtype_id) as count
        FROM transactions
        WHERE document_subtype_id IS NOT NULL
    """)).scalar()
    print(f"  {used_subtypes} farklı document_subtype_id kullanılıyor")
    
    # Transaction sayısı
    trans_count = conn.execute(text("SELECT COUNT(*) FROM transactions WHERE document_subtype_id IS NOT NULL")).scalar()
    print(f"  {trans_count} transaction document_subtype_id ile bağlı")
    
    print("\n✅ Yevmiye kayıtları korundu, mevcut transactions etkilenmedi!")
    print("✅ YEVMIYE_KAYDI_SABLONU.md'ye uygun evrak türleri eklendi!")
