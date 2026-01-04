from sqlalchemy import create_engine, text
import os

print("🗑️  Document Type Mapping Temizleniyor...")

# Database connection from .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 1. document_type_mapping temizle
    result = conn.execute(text("DELETE FROM document_type_mapping"))
    conn.commit()
    print(f"✅ document_type_mapping: {result.rowcount} kayıt silindi")
    
    # 2. document_subtypes temizle
    result = conn.execute(text("DELETE FROM document_subtypes"))
    conn.commit()
    print(f"✅ document_subtypes: {result.rowcount} kayıt silindi")
    
    # 3. document_types temizle
    result = conn.execute(text("DELETE FROM document_types"))
    conn.commit()
    print(f"✅ document_types: {result.rowcount} kayıt silindi")
    
    print("\n✅ Tüm tablolar temizlendi!")
