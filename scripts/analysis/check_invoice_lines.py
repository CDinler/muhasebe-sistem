"""
Check invoice_lines table structure
"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Tablo var mı kontrol et
    result = conn.execute(text("SHOW TABLES LIKE '%invoice%'"))
    tables = [row[0] for row in result]
    
    print("Invoice ile ilgili tablolar:")
    for table in tables:
        print(f"  - {table}")
    
    # invoice_lines varsa yapısını göster
    if 'invoice_lines' in tables:
        print("\ninvoice_lines tablo yapısı:")
        result = conn.execute(text("DESCRIBE invoice_lines"))
        for row in result:
            print(f"  {row[0]:30} {row[1]:20} {row[2]:5} {row[3]:5}")
        
        # Örnek kayıt
        print("\nÖrnek 5 kayıt:")
        result = conn.execute(text("""
            SELECT id, einvoice_id, line_no, item_name, quantity, unit_price, 
                   line_total, category, account_code
            FROM invoice_lines 
            WHERE einvoice_id = 3497
            LIMIT 5
        """))
        for row in result:
            print(f"  {row}")
    else:
        print("\n⚠️  invoice_lines tablosu bulunamadı!")
