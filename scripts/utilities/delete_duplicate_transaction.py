"""
F00026298 numaralı transaction'ı sil (Turkcell test kaydı)
PostgreSQL version
"""
from sqlalchemy import create_engine, text

# Database bağlantısı (PostgreSQL)
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/muhasebe_db"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Transaction ID'yi bul
    result = conn.execute(text("""
        SELECT id FROM transactions 
        WHERE transaction_number = 'F00026298'
    """)).fetchone()
    
    if not result:
        print("❌ F00026298 numaralı transaction bulunamadı - zaten silinmiş olabilir")
    else:
        transaction_id = result[0]
        print(f"✅ Transaction bulundu (ID: {transaction_id})")
        
        # Transaction lines'ı sil
        result = conn.execute(text("""
            DELETE FROM transaction_lines 
            WHERE transaction_id = :tid
        """), {'tid': transaction_id})
        print(f"✅ {result.rowcount} transaction_line silindi")
        
        # Mapping'i sil
        result = conn.execute(text("""
            DELETE FROM invoice_transaction_mappings 
            WHERE transaction_id = :tid
        """), {'tid': transaction_id})
        print(f"✅ {result.rowcount} mapping silindi")
        
        # Transaction'ı sil
        result = conn.execute(text("""
            DELETE FROM transactions 
            WHERE id = :tid
        """), {'tid': transaction_id})
        print(f"✅ Transaction silindi")
        
        # E-fatura kaydını resetle
        result = conn.execute(text("""
            UPDATE einvoices 
            SET transaction_id = NULL, 
                processing_status = 'PENDING'
            WHERE transaction_id = :tid
        """), {'tid': transaction_id})
        print(f"✅ {result.rowcount} e-fatura kaydı resetlendi")
        
        conn.commit()
        print("\n🎉 Temizleme tamamlandı! Artık tekrar import yapabilirsin.")

