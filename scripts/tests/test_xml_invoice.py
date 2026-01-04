"""XML'li fatura testi"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice

db = next(get_db())

# XML'li fatura bul
invoice = db.query(EInvoice).filter(EInvoice.has_xml == 1).first()

if invoice:
    print(f"XML'li fatura bulundu: ID={invoice.id}")
    print(f"Fatura No: {invoice.invoice_number}")
    print(f"raw_data var mi: {bool(invoice.raw_data)}")
    if invoice.raw_data:
        has_invoice_line = '<InvoiceLine' in invoice.raw_data
        print(f"InvoiceLine tag var mi: {has_invoice_line}")
        if has_invoice_line:
            # Kac satir var?
            count = invoice.raw_data.count('<InvoiceLine')
            print(f"Satir sayisi: {count}")
        
        # Test API çağrısı
        import requests
        response = requests.get(f'http://localhost:8000/api/v1/einvoices/{invoice.id}')
        if response.status_code == 200:
            data = response.json()
            print(f"\nAPI Response:")
            print(f"  invoice_lines var mi: {'invoice_lines' in data}")
            if 'invoice_lines' in data:
                print(f"  invoice_lines sayisi: {len(data['invoice_lines'])}")
                if data['invoice_lines']:
                    print(f"  Ilk satir: {data['invoice_lines'][0]}")
        else:
            print(f"\nAPI Error: {response.status_code}")
    else:
        print("raw_data YOK!")
else:
    print("XML'li fatura bulunamadi")
