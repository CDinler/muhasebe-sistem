"""Tüm faturaların raw_data durumunu kontrol et"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice

db = next(get_db())

print("=" * 80)
print("FATURA raw_data ANALİZİ")
print("=" * 80)

# Rastgele 10 faturayı kontrol et
invoices = db.query(EInvoice).filter(EInvoice.has_xml == 1).limit(10).all()

for inv in invoices:
    print(f"\nID: {inv.id} | No: {inv.invoice_number}")
    print(f"  Source: {inv.source}")
    print(f"  XML path: {inv.xml_file_path[:50] if inv.xml_file_path else 'YOK'}...")
    
    if inv.raw_data:
        is_xml = inv.raw_data.startswith('<?xml') or inv.raw_data.startswith('<Invoice')
        has_cac_line = 'cac:InvoiceLine' in inv.raw_data
        has_invoice_line = '<InvoiceLine' in inv.raw_data
        
        print(f"  raw_data XML: {is_xml}")
        print(f"  cac:InvoiceLine: {has_cac_line}")
        print(f"  <InvoiceLine: {has_invoice_line}")
        
        if is_xml and not has_cac_line and not has_invoice_line:
            # XML ama satır yok - ilk 500 karaktere bakalım
            print(f"  İLK 200 KARAKTER: {inv.raw_data[:200]}")
    else:
        print(f"  raw_data: YOK!")

print("\n" + "=" * 80)
print("SONUÇ")
print("=" * 80)

# XML path'i olan ama raw_data'sında InvoiceLine olmayan faturaları say
count_missing = db.query(EInvoice).filter(
    EInvoice.xml_file_path.isnot(None),
    EInvoice.raw_data.isnot(None)
).count()

print(f"XML path'li fatura sayısı: {count_missing}")

# Şimdi XML dosyasından okuyup raw_data ile karşılaştıralım
import os
test_invoice = db.query(EInvoice).filter(EInvoice.id == 2).first()
if test_invoice and test_invoice.xml_file_path and os.path.exists(test_invoice.xml_file_path):
    print(f"\n✅ ID=2 için XML dosyası var: {test_invoice.xml_file_path}")
    with open(test_invoice.xml_file_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    print(f"XML dosyası boyutu: {len(xml_content)}")
    print(f"raw_data boyutu: {len(test_invoice.raw_data) if test_invoice.raw_data else 0}")
    print(f"XML'de cac:InvoiceLine: {'cac:InvoiceLine' in xml_content}")
    print(f"raw_data'da cac:InvoiceLine: {'cac:InvoiceLine' in test_invoice.raw_data if test_invoice.raw_data else False}")
    
    if len(xml_content) != len(test_invoice.raw_data or ''):
        print("\n⚠️ SORUN BULUNDU: XML dosyası ile raw_data FARKLI!")
        print(f"XML dosyası ilk 300: {xml_content[:300]}")
        print(f"raw_data ilk 300: {test_invoice.raw_data[:300] if test_invoice.raw_data else 'YOK'}")
