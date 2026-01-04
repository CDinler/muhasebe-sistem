import sys
sys.path.insert(0, 'c:/Projects/muhasebe-sistem/backend')
from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root@localhost:3306/muhasebe_sistem")
with engine.connect() as conn:
    # Transaction ID'yi bul
    result = conn.execute(text("SELECT id FROM transactions WHERE transaction_number = 'F00026298'"))
    row = result.fetchone()
    
    if row:
        tid = row[0]
        print(f"Transaction bulundu: ID={tid}")
        
        # Satırları sil
        conn.execute(text(f"DELETE FROM transaction_lines WHERE transaction_id = {tid}"))
        print("Transaction lines silindi")
        
        # Mapping sil
        conn.execute(text(f"DELETE FROM invoice_transaction_mappings WHERE transaction_id = {tid}"))
        print("Mappings silindi")
        
        # Transaction sil
        conn.execute(text("DELETE FROM transactions WHERE transaction_number = 'F00026298'"))
        conn.commit()
        print("✅ F00026298 transaction silindi!")
    else:
        print("Transaction bulunamadı")
