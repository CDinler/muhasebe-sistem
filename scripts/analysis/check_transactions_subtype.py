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
    print("📊 Transactions tablosunda document_subtype_id kullanımı:")
    
    # document_subtype_id NULL olanlar
    null_count = conn.execute(text("SELECT COUNT(*) FROM transactions WHERE document_subtype_id IS NULL")).scalar()
    print(f"  NULL: {null_count}")
    
    # document_subtype_id NULL olmayanlar
    not_null_count = conn.execute(text("SELECT COUNT(*) FROM transactions WHERE document_subtype_id IS NOT NULL")).scalar()
    print(f"  NOT NULL: {not_null_count}")
    
    if not_null_count > 0:
        print("\n  Kullanılan document_subtype_id'ler:")
        rows = conn.execute(text("""
            SELECT document_subtype_id, COUNT(*) as count
            FROM transactions
            WHERE document_subtype_id IS NOT NULL
            GROUP BY document_subtype_id
            ORDER BY count DESC
        """)).fetchall()
        for row in rows:
            print(f"    ID {row[0]}: {row[1]} transaction")
