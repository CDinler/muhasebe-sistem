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

print("🔐 Foreign Key Constraint Ekleme")
print("=" * 80)

with engine.connect() as conn:
    # Önce constraint var mı kontrol et
    fk_exists = conn.execute(text("""
        SELECT COUNT(*) 
        FROM information_schema.TABLE_CONSTRAINTS 
        WHERE CONSTRAINT_SCHEMA = 'muhasebe_sistem'
        AND TABLE_NAME = 'document_subtypes'
        AND CONSTRAINT_NAME = 'fk_subtype_parent'
    """)).scalar()
    
    if fk_exists > 0:
        print("✅ fk_subtype_parent constraint zaten var")
    else:
        print("⚠️  fk_subtype_parent constraint yok, ekleniyor...")
        
        try:
            # Önce tüm parent_code'ların geçerli olduğundan emin ol
            invalid = conn.execute(text("""
                SELECT COUNT(*) 
                FROM document_subtypes 
                WHERE parent_code NOT IN (SELECT code FROM document_types)
            """)).scalar()
            
            if invalid > 0:
                print(f"❌ {invalid} geçersiz parent_code var! Constraint eklenemez.")
                exit(1)
            
            # Constraint ekle
            conn.execute(text("""
                ALTER TABLE document_subtypes 
                ADD CONSTRAINT fk_subtype_parent 
                FOREIGN KEY (parent_code) 
                REFERENCES document_types(code)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            """))
            conn.commit()
            print("✅ fk_subtype_parent constraint eklendi")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
    
    # Doğrulama
    print("\n" + "=" * 80)
    print("🔍 Constraint Kontrolü:")
    print("=" * 80)
    
    constraints = conn.execute(text("""
        SELECT 
            CONSTRAINT_NAME,
            CONSTRAINT_TYPE
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = 'muhasebe_sistem'
        AND TABLE_NAME = 'document_subtypes'
    """)).fetchall()
    
    for name, ctype in constraints:
        print(f"  {ctype:15}: {name}")
