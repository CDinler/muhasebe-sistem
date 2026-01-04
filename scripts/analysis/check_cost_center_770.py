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

print("🔍 Cost Center 770.000 Kontrolü")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, code, name 
        FROM cost_centers 
        WHERE code = '770.000' OR name LIKE '%Merkez%'
        ORDER BY code
    """)).fetchall()
    
    if result:
        print("\n✅ Bulunan Cost Centers:")
        for id, code, name in result:
            print(f"  ID {id:3}: {code:15} - {name}")
    else:
        print("\n❌ 770.000 veya 'Merkez' içeren cost center bulunamadı!")
        
        # Tüm cost center'ları göster
        all_cc = conn.execute(text("""
            SELECT id, code, name 
            FROM cost_centers 
            ORDER BY code
            LIMIT 10
        """)).fetchall()
        
        print("\n📋 İlk 10 Cost Center:")
        for id, code, name in all_cc:
            print(f"  ID {id:3}: {code:15} - {name}")
