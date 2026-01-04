import sys
sys.path.insert(0, 'c:/Projects/muhasebe-sistem/backend')
from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root@localhost:3306/muhasebe_sistem")
with engine.connect() as conn:
    # Transaction 90914'ü sil
    conn.execute(text("DELETE FROM transaction_lines WHERE transaction_id = 90914"))
    conn.execute(text("DELETE FROM invoice_transaction_mappings WHERE transaction_id = 90914"))
    conn.execute(text("DELETE FROM transactions WHERE id = 90914"))
    print("✅ Transaction 90914 silindi")
    
    # Fatura resetle
    conn.execute(text("UPDATE einvoices SET processing_status = 'PENDING', transaction_id = NULL WHERE id = 3496"))
    print("✅ Fatura resetlendi")
    
    # Counter
    conn.execute(text("UPDATE transaction_counter SET last_number = 26298 WHERE id = 1"))
    print("✅ Counter: 26298")
    
    conn.commit()
    print("🎉 Hazır!")
