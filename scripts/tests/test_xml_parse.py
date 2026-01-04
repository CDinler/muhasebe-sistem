"""XML içeriğini kontrol et"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice

db = next(get_db())

invoice = db.query(EInvoice).filter(EInvoice.id == 1).first()

print(f"ID: {invoice.id}")
print(f"Fatura No: {invoice.invoice_number}")
print(f"\nraw_data tipi: {type(invoice.raw_data)}")
print(f"raw_data uzunluğu: {len(invoice.raw_data)}")

# InvoiceLine var mı?
has_invoice_line = '<InvoiceLine' in invoice.raw_data if invoice.raw_data else False
print(f"\n'<InvoiceLine' içeriyor mu: {has_invoice_line}")

# Alternatif namespace ile de dene
has_cac_invoice_line = 'cac:InvoiceLine' in invoice.raw_data if invoice.raw_data else False
print(f"'cac:InvoiceLine' içeriyor mu: {has_cac_invoice_line}")

# XML'i parse edip bakalım
if invoice.raw_data:
    import xml.etree.ElementTree as ET
    
    try:
        root = ET.fromstring(invoice.raw_data)
        print(f"\n✅ XML parse edildi!")
        print(f"Root tag: {root.tag}")
        
        # Namespace
        ns = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
        
        # InvoiceLine bul
        lines = root.findall('.//cac:InvoiceLine', ns)
        print(f"\nInvoiceLine sayısı: {len(lines)}")
        
        if lines:
            print(f"\n✅ SATIRLAR VAR!")
            line = lines[0]
            
            # İlk satırın detayını göster
            item_name = line.find('.//cac:Item/cbc:Name', ns)
            qty = line.find('cbc:InvoicedQuantity', ns)
            price = line.find('.//cac:Price/cbc:PriceAmount', ns)
            
            print(f"İlk satır:")
            print(f"  Ürün: {item_name.text if item_name is not None else 'YOK'}")
            print(f"  Miktar: {qty.text if qty is not None else 'YOK'}")
            print(f"  Fiyat: {price.text if price is not None else 'YOK'}")
    except Exception as e:
        print(f"\n❌ XML parse hatası: {e}")
        import traceback
        traceback.print_exc()
