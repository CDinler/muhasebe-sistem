"""Veritabanında satır bilgileri olan faturaları kontrol et"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice
from sqlalchemy import func

db = next(get_db())

print("=" * 80)
print("VERİTABANINDA SATIR BİLGİSİ KONTROLÜ")
print("=" * 80)

# Toplam fatura sayısı
total = db.query(EInvoice).count()
print(f"\nToplam Fatura Sayısı: {total}")

# XML'li fatura sayısı
xml_count = db.query(EInvoice).filter(EInvoice.has_xml == 1).count()
print(f"XML'li Fatura Sayısı: {xml_count}")

# raw_data'sı olan fatura sayısı
raw_data_count = db.query(EInvoice).filter(EInvoice.raw_data.isnot(None)).count()
print(f"raw_data olan Fatura Sayısı: {raw_data_count}")

# İlk 5 faturayı kontrol et
print("\n" + "=" * 80)
print("İLK 5 FATURA DETAYI")
print("=" * 80)

invoices = db.query(EInvoice).limit(5).all()
for inv in invoices:
    print(f"\nID: {inv.id} | No: {inv.invoice_number}")
    print(f"  has_xml: {inv.has_xml}")
    print(f"  raw_data var mı: {bool(inv.raw_data)}")
    
    if inv.raw_data:
        if isinstance(inv.raw_data, str):
            has_invoice_line = '<InvoiceLine' in inv.raw_data
            has_lines_key = False
        elif isinstance(inv.raw_data, dict):
            has_invoice_line = '<InvoiceLine' in str(inv.raw_data)
            has_lines_key = 'lines' in inv.raw_data
        else:
            has_invoice_line = False
            has_lines_key = False
        
        print(f"  InvoiceLine tag: {has_invoice_line}")
        print(f"  'lines' key: {has_lines_key}")
        
        if has_lines_key:
            print(f"  Satır sayısı (lines): {len(inv.raw_data['lines']) if inv.raw_data['lines'] else 0}")
        elif has_invoice_line:
            count = str(inv.raw_data).count('<InvoiceLine')
            print(f"  Satır sayısı (XML): {count}")

print("\n" + "=" * 80)
print("XML SATIR İÇEREN FATURA ARAMA")
print("=" * 80)

# XML satırları olan bir fatura bul
xml_invoices = db.query(EInvoice).filter(EInvoice.has_xml == 1).all()
found_xml_lines = False

for inv in xml_invoices:
    if inv.raw_data and '<InvoiceLine' in str(inv.raw_data):
        print(f"\n✅ BULUNDU! ID: {inv.id} | No: {inv.invoice_number}")
        count = str(inv.raw_data).count('<InvoiceLine')
        print(f"   XML Satır Sayısı: {count}")
        found_xml_lines = True
        break

if not found_xml_lines:
    print("\n❌ XML satırları içeren fatura bulunamadı!")
    print("\nExcel'den import edilen faturalara bakalım...")
    
    # Excel lines olan fatura bul
    for inv in db.query(EInvoice).filter(EInvoice.raw_data.isnot(None)).limit(10).all():
        if inv.raw_data and isinstance(inv.raw_data, dict) and 'lines' in inv.raw_data:
            print(f"\n✅ Excel satırları var! ID: {inv.id} | No: {inv.invoice_number}")
            print(f"   Excel Satır Sayısı: {len(inv.raw_data['lines'])}")
            break
