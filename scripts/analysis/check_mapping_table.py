from sqlalchemy import create_engine, text
import os

# Database connection from .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    mapping_count = conn.execute(text("SELECT COUNT(*) FROM document_type_mapping")).scalar()
    print(f"📊 document_type_mapping kayıt sayısı: {mapping_count}")
    
    if mapping_count > 0:
        # İlk 5 kaydı göster
        rows = conn.execute(text("SELECT * FROM document_type_mapping LIMIT 5")).fetchall()
        print("\n📋 İlk 5 kayıt:")
        for row in rows:
            print(f"  {row}")
