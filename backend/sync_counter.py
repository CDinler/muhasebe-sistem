#!/usr/bin/env python3
"""Counter'ı transactions tablosundaki gerçek max değere senkronize et"""

from sqlalchemy import create_engine, text
from app.core.config import Settings

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()
trans = conn.begin()

try:
    # transactions'daki en büyük F numarasını bul
    result = conn.execute(text("""
        SELECT CAST(SUBSTRING(transaction_number, 2) AS UNSIGNED) as num 
        FROM transactions 
        WHERE transaction_number LIKE 'F%' 
        ORDER BY num DESC 
        LIMIT 1
    """)).fetchone()
    
    max_num = result[0] if result else 0
    
    # Counter'ı güncelle
    conn.execute(text("UPDATE transaction_counter SET last_number = :num WHERE id = 1"), 
                 {"num": max_num})
    
    trans.commit()
    
    print(f"\n✅ Counter senkronize edildi!")
    print(f"   Transactions'daki max: F{max_num:08d}")
    print(f"   Counter güncellendi: {max_num}")
    print(f"   Sonraki numara: F{max_num+1:08d}")
    
except Exception as e:
    trans.rollback()
    print(f"\n❌ HATA: {e}")
    raise
finally:
    conn.close()
