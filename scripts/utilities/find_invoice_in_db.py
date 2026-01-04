"""
Veritabanında YCM2025000000033 faturasını ara
"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice

db = next(get_db())

# Fatura numarası ile ara
invoice_number = "YCM2025000000033"
uuid = "0562467c-2077-41ba-848a-b342c6dc42dc"

print("=" * 80)
print(f"VERİTABANINDA FATURA ARAMA: {invoice_number}")
print("=" * 80)

# Fatura numarasına göre ara
invoice = db.query(EInvoice).filter(EInvoice.invoice_number == invoice_number).first()

if invoice:
    print("\n✅ FATURA BULUNDU!")
    print("-" * 80)
    print(f"ID: {invoice.id}")
    print(f"Fatura No: {invoice.invoice_number}")
    print(f"UUID: {invoice.invoice_uuid}")
    print(f"Fatura Tarihi: {invoice.issue_date}")
    print(f"Gönderen: {invoice.supplier_name}")
    print(f"VKN/TCKN: {invoice.supplier_tax_number}")
    print(f"Tutar: {invoice.payable_amount:,.2f} {invoice.currency_code}")
    print(f"Kategori: {invoice.invoice_category}")
    print(f"Profil: {invoice.invoice_profile}")
    print(f"Durum: {invoice.processing_status}")
    
    if invoice.xml_file_path:
        print(f"\nXML Dosya Yolu: {invoice.xml_file_path}")
    else:
        print("\n⚠️  XML dosya yolu kayıtlı değil")
else:
    print("\n❌ FATURA BULUNAMADI")
    print(f"   Aranan fatura numarası: {invoice_number}")
    
    # UUID ile de dene
    print(f"\n   UUID ile aranıyor: {uuid}")
    invoice = db.query(EInvoice).filter(EInvoice.invoice_uuid == uuid).first()
    
    if invoice:
        print("\n   ✅ UUID ile bulundu!")
        print(f"   Fatura No: {invoice.invoice_number}")
    else:
        print("   ❌ UUID ile de bulunamadı")

print("\n" + "=" * 80)
