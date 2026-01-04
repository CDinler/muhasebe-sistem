"""
Vergi detaylarını test et - XML'den parse edip veritabanına kaydet
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
from app.models.invoice_tax import InvoiceTax
from app.services.einvoice_xml_service import parse_xml_invoice, create_einvoice_from_xml
import xml.etree.ElementTree as ET

def test_tax_parsing():
    """Vergi detaylarını parse et ve kaydet"""
    db = SessionLocal()
    
    try:
        # Test faturası
        invoice = db.query(EInvoice).filter(
            EInvoice.invoice_number == '0012025270801375'
        ).first()
        
        if not invoice:
            print("✗ Fatura bulunamadı!")
            return
        
        print(f"=== FATURA: {invoice.invoice_number} ===")
        print(f"ETTN: {invoice.invoice_uuid}")
        print(f"Toplam: {invoice.payable_amount} TRY")
        
        # XML'i parse et
        invoice_data, errors = parse_xml_invoice(
            invoice.raw_data.encode('utf-8') if isinstance(invoice.raw_data, str) else invoice.raw_data,
            'test.xml'
        )
        
        if errors:
            print(f"\n✗ Parse hataları:")
            for err in errors:
                print(f"  - {err}")
            return
        
        # Vergi detaylarını kontrol et
        tax_details = invoice_data.get('tax_details', [])
        print(f"\n=== PARSE EDİLEN VERGİ DETAYLARI ({len(tax_details)} adet) ===")
        
        for idx, tax in enumerate(tax_details, 1):
            print(f"\n{idx}. {tax.get('tax_name')} ({tax.get('tax_type_code')})")
            print(f"   Oran      : %{tax.get('tax_percent')}")
            print(f"   Matrah    : {tax.get('taxable_amount')} {tax.get('currency_code')}")
            print(f"   Vergi     : {tax.get('tax_amount')} {tax.get('currency_code')}")
            if tax.get('exemption_reason_code'):
                print(f"   İstisna   : {tax.get('exemption_reason_code')} - {tax.get('exemption_reason')}")
        
        # Veritabanındaki mevcut kayıtları kontrol et
        existing_taxes = db.query(InvoiceTax).filter(
            InvoiceTax.einvoice_id == invoice.id
        ).all()
        
        print(f"\n\n=== VERİTABANINDAKİ KAYITLAR ({len(existing_taxes)} adet) ===")
        if existing_taxes:
            for tax in existing_taxes:
                print(f"  - {tax.tax_name} ({tax.tax_type_code}): %{tax.tax_percent}")
                print(f"    Matrah: {tax.taxable_amount} | Vergi: {tax.tax_amount}")
        else:
            print("  (Henüz kaydedilmemiş)")
        
        # Kaydet
        print(f"\n\n=== VERGİ DETAYLARINI KAYDEDME ===")
        
        # Önce eski kayıtları sil
        deleted = db.query(InvoiceTax).filter(
            InvoiceTax.einvoice_id == invoice.id
        ).delete()
        print(f"✓ {deleted} eski kayıt silindi")
        
        # Yeni kayıtları ekle
        for tax_detail in tax_details:
            invoice_tax = InvoiceTax(
                einvoice_id=invoice.id,
                tax_type_code=tax_detail.get('tax_type_code', '0015'),
                tax_name=tax_detail.get('tax_name', 'KDV'),
                tax_percent=tax_detail.get('tax_percent', 0),
                taxable_amount=tax_detail.get('taxable_amount', 0),
                tax_amount=tax_detail.get('tax_amount', 0),
                currency_code=tax_detail.get('currency_code', 'TRY'),
                exemption_reason_code=tax_detail.get('exemption_reason_code'),
                exemption_reason=tax_detail.get('exemption_reason')
            )
            db.add(invoice_tax)
        
        db.commit()
        print(f"✓ {len(tax_details)} vergi kaydı eklendi")
        
        # Kontrol et
        saved_taxes = db.query(InvoiceTax).filter(
            InvoiceTax.einvoice_id == invoice.id
        ).all()
        
        print(f"\n=== KAYDEDILEN VERGİLER ({len(saved_taxes)} adet) ===")
        total_tax = 0
        for tax in saved_taxes:
            print(f"  ✓ {tax.tax_name} ({tax.tax_type_code})")
            print(f"    %{tax.tax_percent} | Matrah: {tax.taxable_amount} TRY | Vergi: {tax.tax_amount} TRY")
            total_tax += float(tax.tax_amount)
        
        print(f"\n=== TOPLAM VERGİ: {total_tax:.2f} TRY ===")
        print(f"XML'deki toplam: {invoice_data.get('tax_inclusive_amount', 0) - invoice_data.get('tax_exclusive_amount', 0):.2f} TRY")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("VERGİ DETAYLARI TEST")
    print("=" * 80)
    
    test_tax_parsing()
    
    print("\n" + "=" * 80)
