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

print("🔄 Eksik Alt Türleri Ekleme (name unique constraint düzeltmesi)")
print("=" * 80)

# Name benzersiz olmalı, bu yüzden parent belirtecek isimler kullan
subtypes_to_add = [
    ('BANKA_TAHSILAT_EFT', 'BANKA_TAHSILAT', 'Tahsilat - EFT/Havale', 'OTOMATIK', 5),
    ('BANKA_TAHSILAT_KART', 'BANKA_TAHSILAT', 'Tahsilat - Kredi Kartı', 'OTOMATIK', 6),
    ('BANKA_TEDIYE_EFT', 'BANKA_TEDIYE', 'Tediye - EFT/Havale', 'OTOMATIK', 1),
    ('BANKA_TEDIYE_KART', 'BANKA_TEDIYE', 'Tediye - Kredi Kartı', 'OTOMATIK', 2),
    ('BANKA_TEDIYE_CEK', 'BANKA_TEDIYE', 'Tediye - Çek', 'OTOMATIK', 3),
    ('BANKA_TEDIYE_SENET', 'BANKA_TEDIYE', 'Tediye - Senet', 'OTOMATIK', 4),
    ('CEK_ODEME', 'CEK_TAHSILAT_ODEME', 'Çek - Ödeme', 'MANUEL', 2),
    ('ALINAN_SENET_CIRO', 'ALINAN_SENET', 'Alınan Senet - Ciro', 'MANUEL', 1),
    ('ALINAN_SENET_PORTFOY', 'ALINAN_SENET', 'Alınan Senet - Portföy', 'MANUEL', 2),
    ('SENET_ODEME', 'SENET_TAHSILAT_ODEME', 'Senet - Ödeme', 'MANUEL', 2),
]

with engine.connect() as conn:
    added = 0
    for code, parent_code, name, category, sort_order in subtypes_to_add:
        # Var mı kontrol et
        exists = conn.execute(text(f"SELECT COUNT(*) FROM document_subtypes WHERE code = '{code}'")).scalar()
        
        if exists == 0:
            try:
                conn.execute(text(f"""
                    INSERT INTO document_subtypes (code, parent_code, name, category, sort_order, is_active)
                    VALUES ('{code}', '{parent_code}', '{name}', '{category}', {sort_order}, 1)
                """))
                conn.commit()
                print(f"✅ Eklendi: {code} ({name})")
                added += 1
            except Exception as e:
                print(f"❌ {code}: {str(e)}")
        else:
            print(f"⏭️  Atlandı: {code} (zaten var)")
    
    print(f"\n📊 {added} kayıt eklendi")

# Doğrulama
print("\n" + "=" * 80)
print("🔍 Final Durum:")
print("=" * 80)

with engine.connect() as conn:
    total = conn.execute(text("SELECT COUNT(*) FROM document_subtypes")).scalar()
    print(f"📄 Toplam alt evrak türü: {total}")
    
    # Alt türü olmayan ana türler
    no_subtypes = conn.execute(text("""
        SELECT code, name
        FROM document_types
        WHERE code NOT IN (SELECT DISTINCT parent_code FROM document_subtypes WHERE parent_code IS NOT NULL)
        ORDER BY category, code
    """)).fetchall()
    
    if no_subtypes:
        print(f"\n⚠️  Alt türü olmayan ana evrak türleri ({len(no_subtypes)}):")
        for code, name in no_subtypes:
            print(f"  - {code} ({name})")
    else:
        print("\n✅ Tüm ana evrak türlerinin alt türü var")
