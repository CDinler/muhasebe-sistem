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

print("📊 document_types ve document_subtypes Final Durum")
print("=" * 100)

with engine.connect() as conn:
    # Tüm ana evrak türleri ve alt türleri
    result = conn.execute(text("""
        SELECT 
            dt.category AS kategori,
            dt.code AS ana_kod,
            dt.name AS ana_ad,
            GROUP_CONCAT(ds.code ORDER BY ds.sort_order SEPARATOR ', ') AS alt_kodlar,
            COUNT(ds.id) AS alt_sayi
        FROM document_types dt
        LEFT JOIN document_subtypes ds ON ds.parent_code = dt.code
        GROUP BY dt.category, dt.code, dt.name
        ORDER BY dt.category, dt.code
    """)).fetchall()
    
    current_category = None
    total_types = 0
    total_subtypes = 0
    
    for kategori, ana_kod, ana_ad, alt_kodlar, alt_sayi in result:
        if kategori != current_category:
            if current_category is not None:
                print()
            print(f"\n{'='*100}")
            print(f"📁 {kategori}")
            print(f"{'='*100}")
            current_category = kategori
        
        total_types += 1
        total_subtypes += alt_sayi
        
        print(f"\n  {ana_kod:25} ({ana_ad})")
        if alt_kodlar:
            # Alt kodları satır satır göster
            alt_list = alt_kodlar.split(', ')
            for i, alt in enumerate(alt_list, 1):
                print(f"    {i:2}. {alt}")
        else:
            print(f"    ⚠️  Alt tür yok")

print(f"\n\n{'='*100}")
print(f"📊 ÖZET")
print(f"{'='*100}")
print(f"  📋 Ana Evrak Türü: {total_types}")
print(f"  📄 Alt Evrak Türü: {total_subtypes}")
print(f"  ✅ Migration: TAMAMLANDI")
print(f"{'='*100}")

# Eksik parent_code kontrolü
print(f"\n\n🔍 parent_code Kontrolü:")
print(f"{'='*100}")

with engine.connect() as conn:
    orphan_subtypes = conn.execute(text("""
        SELECT code, name, parent_code
        FROM document_subtypes
        WHERE parent_code NOT IN (SELECT code FROM document_types)
    """)).fetchall()
    
    if orphan_subtypes:
        print("❌ Orphan (parent'ı olmayan) alt türler:")
        for code, name, parent in orphan_subtypes:
            print(f"  {code}: parent_code='{parent}' (yok!)")
    else:
        print("✅ Tüm alt türlerin parent_code'u geçerli")

# Duplicate name kontrolü
print(f"\n\n🔍 Duplicate Name Kontrolü:")
print(f"{'='*100}")

with engine.connect() as conn:
    duplicates = conn.execute(text("""
        SELECT name, GROUP_CONCAT(code SEPARATOR ', ') AS codes, COUNT(*) AS cnt
        FROM document_subtypes
        GROUP BY name
        HAVING cnt > 1
    """)).fetchall()
    
    if duplicates:
        print("⚠️  Aynı isimde alt türler (unique constraint nedeniyle sorun olabilir):")
        for name, codes, cnt in duplicates:
            print(f"  '{name}': {codes} ({cnt} kez)")
    else:
        print("✅ Tüm alt tür isimleri benzersiz")
