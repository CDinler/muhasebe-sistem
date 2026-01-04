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
    print("📋 Mevcut document_types:")
    types_rows = conn.execute(text("SELECT id, code, name FROM document_types ORDER BY id")).fetchall()
    for row in types_rows:
        print(f"  ID {row[0]}: {row[1]} - {row[2]}")
    
    print("\n📋 Mevcut document_subtypes (transactions'da kullanılanlar):")
    subtypes_rows = conn.execute(text("""
        SELECT DISTINCT ds.id, ds.parent_code, ds.code, ds.name
        FROM document_subtypes ds
        INNER JOIN transactions t ON t.document_subtype_id = ds.id
        ORDER BY ds.id
    """)).fetchall()
    for row in subtypes_rows:
        print(f"  ID {row[0]}: {row[1]} → {row[2]} - {row[3]}")
