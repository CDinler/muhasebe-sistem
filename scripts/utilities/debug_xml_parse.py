from app.core.database import engine
from sqlalchemy import text
import xml.etree.ElementTree as ET

# Fatura raw_data'sını al
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, invoice_number, raw_data FROM einvoices WHERE id = 1"))
    row = result.fetchone()
    
    if row:
        print(f"=== FATURA: {row[1]} (ID: {row[0]}) ===")
        raw_data = row[2]
        
        print(f"\nraw_data tipi: {type(raw_data)}")
        print(f"İlk 200 karakter:\n{raw_data[:200]}")
        
        # Escape karakterlerini kontrol et
        if '&quot;' in raw_data[:500]:
            print("\n⚠️ XML escaped formatında! Unescape gerekli")
            import html
            raw_data = html.unescape(raw_data)
            print(f"Unescape sonrası ilk 200:\n{raw_data[:200]}")
        
        # XML parse et
        try:
            root = ET.fromstring(raw_data)
            print(f"\n✅ XML parse edildi. Root tag: {root.tag}")
            
            # Namespace tanımla
            ns = {
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            }
            
            # InvoiceLine ara
            lines = root.findall('.//cac:InvoiceLine', ns)
            print(f"InvoiceLine sayısı: {len(lines)}")
            
            if lines:
                print("\n✅ İlk satır:")
                first_line = lines[0]
                item = first_line.find('.//cac:Item/cbc:Name', ns)
                print(f"  Ürün: {item.text if item is not None else 'YOK'}")
                
        except Exception as e:
            print(f"\n❌ XML parse hatası: {e}")
