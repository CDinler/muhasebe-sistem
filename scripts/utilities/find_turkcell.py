import sys
sys.path.insert(0, 'c:/Projects/muhasebe-sistem/backend')
from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root@localhost:3306/muhasebe_sistem")
with engine.connect() as conn:
    # Turkcell faturalarını bul
    result = conn.execute(text("""
        SELECT id, invoice_number, processing_status, transaction_id 
        FROM einvoices 
        WHERE supplier_name LIKE '%TURKCELL%'
        ORDER BY id DESC LIMIT 5
    """))
    
    for row in result:
        print(f"ID: {row[0]}, No: {row[1]}, Status: {row[2]}, Transaction: {row[3]}")
