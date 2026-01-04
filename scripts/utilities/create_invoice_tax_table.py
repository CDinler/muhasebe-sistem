"""
invoice_taxes tablosunu oluştur ve mevcut faturaları analiz et
"""
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
from app.core.database import Base
from app.models.invoice_tax import InvoiceTax
from app.models.einvoice import EInvoice
import xml.etree.ElementTree as ET

# Veritabanı bağlantısı
engine = create_engine(settings.DATABASE_URL)

def check_and_create_table():
    """invoice_taxes tablosunu kontrol et ve gerekirse oluştur"""
    inspector = inspect(engine)
    
    if 'invoice_taxes' in inspector.get_table_names():
        print("✓ invoice_taxes tablosu zaten mevcut")
        
        # Tablo yapısını göster
        columns = inspector.get_columns('invoice_taxes')
        print("\n=== TABLO YAPISI ===")
        for col in columns:
            print(f"  {col['name']:<25} {col['type']}")
        
        # Kayıt sayısını göster
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as cnt FROM invoice_taxes"))
            count = result.scalar()
            print(f"\n✓ Toplam kayıt: {count}")
    else:
        print("✗ invoice_taxes tablosu yok, oluşturuluyor...")
        
        # Tabloyu oluştur
        InvoiceTax.__table__.create(engine)
        print("✓ Tablo oluşturuldu!")

def analyze_existing_invoices():
    """Mevcut faturaların vergi detaylarını analiz et"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Namespace tanımları
        ns = {
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
        
        # Örnek faturayı kontrol et
        invoice = db.query(EInvoice).filter(
            EInvoice.invoice_number == '0012025270801375'
        ).first()
        
        if invoice:
            print(f"\n=== FATURA: {invoice.invoice_number} ===")
            print(f"ETTN: {invoice.invoice_uuid}")
            print(f"Toplam: {invoice.payable_amount} TRY")
            
            # XML'i parse et
            root = ET.fromstring(invoice.raw_data)
            
            # TaxTotal'ı bul
            tax_total_elem = root.find('.//cac:TaxTotal', ns)
            
            if tax_total_elem:
                total_tax = tax_total_elem.find('cbc:TaxAmount', ns)
                print(f"\nToplam Vergi (TaxAmount): {total_tax.text if total_tax is not None else 'N/A'} {total_tax.get('currencyID') if total_tax is not None else ''}")
                
                # TaxSubtotal'ları bul
                tax_subtotals = tax_total_elem.findall('.//cac:TaxSubtotal', ns)
                print(f"\nVergi Satırları: {len(tax_subtotals)}")
                print("-" * 80)
                
                for idx, subtotal in enumerate(tax_subtotals, 1):
                    taxable_amt = subtotal.find('cbc:TaxableAmount', ns)
                    tax_amt = subtotal.find('cbc:TaxAmount', ns)
                    percent = subtotal.find('cbc:Percent', ns)
                    
                    tax_category = subtotal.find('.//cac:TaxCategory', ns)
                    tax_scheme = tax_category.find('.//cac:TaxScheme', ns) if tax_category is not None else None
                    
                    tax_name = tax_scheme.find('cbc:Name', ns) if tax_scheme is not None else None
                    tax_type_code = tax_scheme.find('cbc:TaxTypeCode', ns) if tax_scheme is not None else None
                    
                    print(f"\n{idx}. Vergi Satırı:")
                    print(f"   Kod       : {tax_type_code.text if tax_type_code is not None else 'N/A'}")
                    print(f"   Adı       : {tax_name.text if tax_name is not None else 'N/A'}")
                    print(f"   Oran      : %{percent.text if percent is not None else 'N/A'}")
                    print(f"   Matrah    : {taxable_amt.text if taxable_amt is not None else 'N/A'} {taxable_amt.get('currencyID') if taxable_amt is not None else ''}")
                    print(f"   Vergi     : {tax_amt.text if tax_amt is not None else 'N/A'} {tax_amt.get('currencyID') if tax_amt is not None else ''}")
            
            # Veritabanındaki vergi kayıtlarını kontrol et
            existing_taxes = db.query(InvoiceTax).filter(
                InvoiceTax.einvoice_id == invoice.id
            ).all()
            
            print(f"\n\n=== VERİTABANINDAKİ KAYITLAR ===")
            if existing_taxes:
                print(f"Toplam {len(existing_taxes)} vergi kaydı bulundu:")
                for tax in existing_taxes:
                    print(f"  - {tax.tax_name} ({tax.tax_type_code}): %{tax.tax_percent} | Matrah: {tax.taxable_amount} | Vergi: {tax.tax_amount}")
            else:
                print("✗ Hiç vergi kaydı yok!")
        else:
            print("✗ Fatura bulunamadı!")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("VERGİ DETAYLARI TABLO KONTROLÜ")
    print("=" * 80)
    
    # Tabloyu kontrol et/oluştur
    check_and_create_table()
    
    # Mevcut faturaları analiz et
    analyze_existing_invoices()
    
    print("\n" + "=" * 80)
