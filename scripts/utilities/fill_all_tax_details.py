"""
TÜM FATURALARIN VERGİ DETAYLARINI DOLDUR
Mevcut faturalardaki XML'leri parse edip vergi detaylarını invoice_taxes tablosuna kaydet
"""
import sys
import io

# Windows terminal encoding sorunu için
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
from app.models.invoice_tax import InvoiceTax
from app.services.einvoice_xml_service import parse_xml_invoice
import xml.etree.ElementTree as ET

def fill_all_tax_details():
    """Tüm faturaların vergi detaylarını doldur"""
    db = SessionLocal()
    
    try:
        # XML'i olan tüm faturaları al
        invoices = db.query(EInvoice).filter(
            EInvoice.has_xml == 1,
            EInvoice.raw_data != None
        ).all()
        
        print(f"=== {len(invoices)} FATURA BULUNDU ===\n")
        
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for idx, invoice in enumerate(invoices, 1):
            print(f"[{idx}/{len(invoices)}] {invoice.invoice_number} ({invoice.invoice_uuid})")
            
            try:
                # Zaten vergi kaydı var mı?
                existing_taxes = db.query(InvoiceTax).filter(
                    InvoiceTax.einvoice_id == invoice.id
                ).count()
                
                if existing_taxes > 0:
                    print(f"  ⊙ Zaten {existing_taxes} vergi kaydı var, atlanıyor...")
                    skip_count += 1
                    continue
                
                # XML'i parse et
                invoice_data, errors = parse_xml_invoice(
                    invoice.raw_data.encode('utf-8') if isinstance(invoice.raw_data, str) else invoice.raw_data,
                    f'{invoice.invoice_number}.xml'
                )
                
                if errors:
                    print(f"  ✗ Parse hatası: {errors[0]}")
                    error_count += 1
                    continue
                
                # Vergi detaylarını al
                tax_details = invoice_data.get('tax_details', [])
                
                if not tax_details:
                    print(f"  ⊙ Vergi detayı yok")
                    skip_count += 1
                    continue
                
                # Vergi detaylarını kaydet
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
                
                print(f"  ✓ {len(tax_details)} vergi kaydı eklendi")
                success_count += 1
                
            except Exception as e:
                db.rollback()
                print(f"  ✗ Hata: {str(e)}")
                error_count += 1
        
        print(f"\n{'='*80}")
        print(f"ÖZET:")
        print(f"  ✓ Başarılı: {success_count}")
        print(f"  ⊙ Atlanan : {skip_count}")
        print(f"  ✗ Hata    : {error_count}")
        print(f"{'='*80}")
        
        # Toplam vergi kaydı sayısı
        total_tax_records = db.query(InvoiceTax).count()
        print(f"\n✓ Toplam vergi kaydı: {total_tax_records}")
        
        # Vergi tiplerine göre dağılım
        from sqlalchemy import func
        tax_distribution = db.query(
            InvoiceTax.tax_type_code,
            InvoiceTax.tax_name,
            func.count(InvoiceTax.id).label('count'),
            func.sum(InvoiceTax.tax_amount).label('total_amount')
        ).group_by(
            InvoiceTax.tax_type_code,
            InvoiceTax.tax_name
        ).all()
        
        if tax_distribution:
            print(f"\n=== VERGİ TİPLERİNE GÖRE DAĞILIM ===")
            for row in tax_distribution:
                print(f"  {row.tax_name} ({row.tax_type_code}): {row.count} kayıt, Toplam: {row.total_amount:.2f} TRY")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("TÜM FATURALARIN VERGİ DETAYLARINI DOLDUR")
    print("=" * 80 + "\n")
    
    fill_all_tax_details()
