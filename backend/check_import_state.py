#!/usr/bin/env python3
"""Import sonrası counter durumunu kontrol et"""

from sqlalchemy import create_engine, text
from app.core.config import Settings

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()

try:
    # Son 3 transaction
    result = conn.execute(text("""
        SELECT transaction_number, description, created_at 
        FROM transactions 
        WHERE transaction_number LIKE 'F%' 
        ORDER BY transaction_number DESC 
        LIMIT 3
    """))
    
    print("\n📊 SON 3 TRANSACTION:")
    for row in result:
        print(f"   {row[0]} | {row[1][:60]} | {row[2]}")
    
    # Counter durumu
    counter = conn.execute(text("SELECT last_number FROM transaction_counter WHERE id = 1")).fetchone()
    counter_value = counter[0] if counter else 0
    
    print(f"\n🔢 COUNTER DURUMU:")
    print(f"   last_number: {counter_value}")
    print(f"   Sonraki numara: F{counter_value+1:08d}")
    
    # Senkronizasyon kontrolü
    max_trans = conn.execute(text("""
        SELECT CAST(SUBSTRING(transaction_number, 2) AS UNSIGNED) as num 
        FROM transactions 
        WHERE transaction_number LIKE 'F%' 
        ORDER BY num DESC 
        LIMIT 1
    """)).fetchone()
    
    max_num = max_trans[0] if max_trans else 0
    
    print(f"\n✅ SENKRONİZASYON:")
    if max_num == counter_value:
        print(f"   ✓ SENKRON! (Max trans: {max_num}, Counter: {counter_value})")
    else:
        print(f"   ✗ DESENKRONİZE! (Max trans: {max_num}, Counter: {counter_value})")
        print(f"   Fark: {abs(max_num - counter_value)}")
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
finally:
    conn.close()
