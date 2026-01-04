from app.core.database import engine
from sqlalchemy import text
import json

# raw_data'sı olan bir fatura al
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, invoice_number, invoice_uuid, raw_data 
        FROM einvoices 
        WHERE raw_data IS NOT NULL AND has_xml = 1
        LIMIT 1
    """))
    row = result.fetchone()
    
    if row:
        print(f"=== FATURA: {row[1]} (ID: {row[0]}) ===")
        print(f"UUID: {row[2]}")
        
        raw_data = row[3]
        print(f"\nraw_data tipi: {type(raw_data)}")
        print(f"raw_data uzunluğu: {len(raw_data) if raw_data else 0}")
        
        # İlk 200 karakter göster
        print(f"\nİlk 200 karakter:\n{raw_data[:200] if raw_data else 'BOŞ'}")
        
        # XML kontrolü
        if raw_data and '<Invoice' in raw_data:
            print("\n✅ raw_data XML formatında")
            
            # InvoiceLine var mı
            if 'InvoiceLine' in raw_data:
                count = raw_data.count('<cac:InvoiceLine>')
                print(f"✅ InvoiceLine tagları VAR! Satır sayısı: {count}")
            else:
                print("❌ InvoiceLine tagları YOK!")
        else:
            print("❌ XML formatında DEĞİL!")
    else:
        print("❌ raw_data olan fatura bulunamadı!")
