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

print("🔍 Document Types ve Subtypes Kontrolü")
print("=" * 80)

with engine.connect() as conn:
    # ALIS_FATURA için ID ve alt türleri
    result = conn.execute(text("""
        SELECT id, code, name 
        FROM document_types 
        WHERE code IN ('ALIS_FATURA', 'SATIS_FATURA')
    """)).fetchall()
    
    print("\n📋 Ana Evrak Türleri (FATURA):")
    for id, code, name in result:
        print(f"  ID {id:3}: {code:20} - {name}")
        
        # Alt türleri
        subtypes = conn.execute(text(f"""
            SELECT id, code, name 
            FROM document_subtypes 
            WHERE parent_code = '{code}'
            ORDER BY sort_order
        """)).fetchall()
        
        for sub_id, sub_code, sub_name in subtypes:
            print(f"       └─ ID {sub_id:3}: {sub_code:30} - {sub_name}")
    
    # E_ARSIV ve E_FATURA alt türlerini özel olarak göster
    print("\n📄 E-Belge Alt Türleri (Migration öncesi eskiler):")
    old_etypes = conn.execute(text("""
        SELECT id, code, name, parent_code
        FROM document_subtypes
        WHERE code IN ('E_FATURA', 'E_ARSIV', 'KAGIT_MATBU')
        ORDER BY id
    """)).fetchall()
    
    for id, code, name, parent in old_etypes:
        print(f"  ID {id:3}: {code:20} - {name:30} (parent: {parent})")
