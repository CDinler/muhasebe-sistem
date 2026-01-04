"""
E-fatura #3497'nin raw_data yapısını incele
"""
from app.core.database import engine
from sqlalchemy import text
import json

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, invoice_number, supplier_name, raw_data 
        FROM einvoices 
        WHERE id = 3497 
        LIMIT 1
    """))
    row = result.fetchone()
    
    if row:
        print(f"ID: {row[0]}")
        print(f"Fatura No: {row[1]}")
        print(f"Tedarikçi: {row[2]}")
        
        if row[3]:
            # String ise parse et
            if isinstance(row[3], str):
                raw = json.loads(row[3])
            else:
                raw = row[3]
                
            print(f"\nraw_data type: {type(raw)}")
            
            if isinstance(raw, dict):
                print(f"raw_data keys ({len(raw)} adet):")
                for key in list(raw.keys())[:20]:
                    value = raw[key]
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {type(value).__name__} (len={len(value) if isinstance(value, list) else 'N/A'})")
                else:
                    val_str = str(value)[:50]
                    print(f"  {key}: {val_str}")
            
            # InvoiceLines var mı kontrol et
            if 'invoice_lines' in raw:
                print(f"\n✓ invoice_lines bulundu! ({len(raw['invoice_lines'])} satır)")
                for i, line in enumerate(raw['invoice_lines'][:3], 1):
                    print(f"\n  Satır {i}:")
                    for k, v in line.items():
                        print(f"    {k}: {v}")
            else:
                print("\n⚠️  invoice_lines bulunamadı")
                
                # Alternatif isimler dene
                for alt_name in ['InvoiceLine', 'lines', 'LineItem', 'items']:
                    if alt_name in raw:
                        print(f"✓ {alt_name} bulundu!")
                        break
        else:
            print("\n⚠️  raw_data NULL")
    else:
        print("⚠️  E-fatura #3497 bulunamadı")
