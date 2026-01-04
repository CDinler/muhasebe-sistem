import sys
sys.path.insert(0, 'c:/Projects/muhasebe-sistem/backend')
from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root@localhost:3306/muhasebe_sistem")
with engine.connect() as conn:
    # 1. Counter güncelle
    conn.execute(text("UPDATE transaction_counter SET last_number = 26298 WHERE id = 1"))
    print("✅ Counter: 26298")
    
    # 2. ID 3496 faturayı resetle
    conn.execute(text("UPDATE einvoices SET processing_status = 'PENDING', transaction_id = NULL WHERE id = 3496"))
    print("✅ Fatura 3496 resetlendi")
    
    conn.commit()
    print("🎉 Hazır!")
