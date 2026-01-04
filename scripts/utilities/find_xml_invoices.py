"""XML kaynaklı fatura bul"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice

db = next(get_db())

# Farklı source'lara bak
sources = db.query(EInvoice.source).distinct().all()
print("Sistemdeki source tipleri:", [s[0] for s in sources])

# XML source'lu fatura
xml_invoice = db.query(EInvoice).filter(EInvoice.source == 'xml').first()
if xml_invoice:
    print(f"\nXML source fatura bulundu: ID {xml_invoice.id}")
    print(f"Fatura No: {xml_invoice.invoice_number}")
    print(f"raw_data var mı: {bool(xml_invoice.raw_data)}")
    if xml_invoice.raw_data:
        print(f"raw_data ilk 200 karakter: {str(xml_invoice.raw_data)[:200]}")
else:
    print("\nXML source fatura YOK")

# xml_file_path'i olan fatura
xml_path_invoice = db.query(EInvoice).filter(EInvoice.xml_file_path.isnot(None)).first()
if xml_path_invoice:
    print(f"\nxml_file_path olan fatura: ID {xml_path_invoice.id}")
    print(f"XML path: {xml_path_invoice.xml_file_path}")
