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
    print("❌ SORUN: document_subtypes'da parent_code KOLONU YOK!")
    print("=" * 80)
    
    print("\n📋 Mevcut Durum:")
    print("  - document_types: code, name, category")
    print("  - document_subtypes: code, name, category")
    print("  - İkisi arasında BAĞLANTI YOK (parent_code kolonu eksik)")
    
    print("\n📊 Örnek Kayıtlar:")
    print("\nDocument Types (Ana Evrak Türleri):")
    types = conn.execute(text("""
        SELECT id, code, name, category 
        FROM document_types 
        WHERE category = 'FATURA' 
        LIMIT 5
    """)).fetchall()
    for t in types:
        print(f"  ID {t[0]}: {t[1]} - {t[2]} (Kategori: {t[3]})")
    
    print("\nDocument Subtypes (Alt Evrak Türleri):")
    subtypes = conn.execute(text("""
        SELECT id, code, name, category 
        FROM document_subtypes 
        WHERE category = 'E_BELGE' 
        LIMIT 5
    """)).fetchall()
    for s in subtypes:
        print(f"  ID {s[0]}: {s[1]} - {s[2]} (Kategori: {s[3]})")
    
    print("\n" + "=" * 80)
    print("\n💡 ÇÖZÜM: parent_code KOLONU EKLENMELİ!")
    print("\nSQL:")
    print("""
ALTER TABLE document_subtypes 
ADD COLUMN parent_code VARCHAR(50) AFTER id,
ADD INDEX idx_parent_code (parent_code);

-- Örnek kullanım:
-- E-Fatura alt tipi → ALIS_FATURASI ana türüne bağlı
UPDATE document_subtypes 
SET parent_code = 'ALIS_FATURASI' 
WHERE code = 'E_FATURA' AND category = 'E_BELGE';
    """)
    
    print("\n" + "=" * 80)
    print("\n📋 YEVMIYE_KAYDI_SABLONU.md'deki yapı:")
    print("  - parent_code: Ana evrak türü kodu (ALIS_FATURASI, BANKA_TEDIYE, vb.)")
    print("  - code: Alt tür kodu (E_FATURA, E_ARSIV, NAKIT, CEK, vb.)")
    print("  - Böylece: ALIS_FATURASI → E_FATURA, E_ARSIV, KAGIT_MATBU, ITHALAT")
