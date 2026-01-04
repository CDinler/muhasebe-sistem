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

print("📊 document_types Code/Name Eşleştirmesi")
print("=" * 80)

with engine.connect() as conn:
    types = conn.execute(text("""
        SELECT code, name, 
               (SELECT COUNT(*) FROM transactions WHERE document_type_id = document_types.id) AS txn_count
        FROM document_types 
        WHERE name IN (
            'Alış Faturası', 'Satış Faturası', 'İade Faturası',
            'Banka Virman', 'Mahsup Fişi', 'Yevmiye Fişi',
            'Açılış Fişi', 'Düzeltici Fiş'
        )
        ORDER BY name
    """)).fetchall()
    
    for code, name, txn_count in types:
        print(f"{name:25} → CODE: {code:20} ({txn_count} txn)")

print("\n" + "=" * 80)
print("💡 Strateji:")
print("   - Eski code'ları yeni code'lara rename ETME (transactions bozulur)")
print("   - Eski code'ları KORU, transactions'lar bunları kullansın")
print("   - YEVMIYE_KAYDI_SABLONU.md code'ları sadece ALIASLAR olsun")
