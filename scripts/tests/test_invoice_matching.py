from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=== E-FATURA ÖRNEĞİ ===")
einvoice = db.execute(text("""
    SELECT id, invoice_number, supplier_tax_number, issue_date, payable_amount
    FROM einvoices
    WHERE supplier_tax_number IN (
        SELECT tax_number FROM contacts WHERE id IN (
            SELECT DISTINCT contact_id FROM transaction_lines LIMIT 5
        )
    )
    LIMIT 1
""")).fetchone()

if einvoice:
    print(f"E-Fatura ID: {einvoice.id}")
    print(f"Evrak No: {einvoice.invoice_number}")
    print(f"VKN: {einvoice.supplier_tax_number}")
    print(f"Tarih: {einvoice.issue_date}")
    print(f"Tutar: {einvoice.payable_amount}")
    
    print("\n=== BU VKN'NİN TRANSACTION_LINES KAYITLARI ===")
    
    # Bu VKN'nin contact_id'sini bul
    contact = db.execute(text("""
        SELECT id FROM contacts WHERE tax_number = :vkn
    """), {'vkn': einvoice.supplier_tax_number}).fetchone()
    
    if contact:
        print(f"Contact ID: {contact.id}")
        
        # Bu contact'ın transaction_lines kayıtlarını göster
        lines = db.execute(text("""
            SELECT 
                tl.id,
                tl.transaction_id,
                t.transaction_date,
                tl.debit,
                tl.credit,
                tl.description
            FROM transaction_lines tl
            JOIN transactions t ON t.id = tl.transaction_id
            WHERE tl.contact_id = :contact_id
            AND ABS(tl.credit - :amount) < 100
            LIMIT 10
        """), {
            'contact_id': contact.id,
            'amount': float(einvoice.payable_amount)
        }).fetchall()
        
        print("\nEşleşen kayıtlar:")
        for line in lines:
            print(f"  TL ID:{line.id} | Tr:{line.transaction_id} | {line.transaction_date} | Credit:{line.credit} | {line.description}")
        
        if not lines:
            print("  ❌ Hiç eşleşme yok!")
            
            # Tarihe bakmadan sadece contact_id ile ara
            print("\n  Tarih/tutar filtresi olmadan bu contact'ın TÜM kayıtları:")
            all_lines = db.execute(text("""
                SELECT 
                    tl.id,
                    tl.transaction_id,
                    t.transaction_date,
                    tl.debit,
                    tl.credit
                FROM transaction_lines tl
                JOIN transactions t ON t.id = tl.transaction_id
                WHERE tl.contact_id = :contact_id
                LIMIT 5
            """), {'contact_id': contact.id}).fetchall()
            
            for line in all_lines:
                print(f"  TL ID:{line.id} | {line.transaction_date} | Debit:{line.debit} | Credit:{line.credit}")

db.close()
