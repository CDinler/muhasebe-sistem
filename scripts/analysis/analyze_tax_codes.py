"""Fatura vergi kodlarını detaylı analiz et"""
import xml.etree.ElementTree as ET
from app.core.database import get_db
from app.models.einvoice import EInvoice

def analyze_invoice_taxes():
    db = next(get_db())
    
    # Belirtilen faturayı bul
    invoice = db.query(EInvoice).filter(
        EInvoice.invoice_uuid == 'da2db336-8cd0-4153-91fb-d0e65deee20e'
    ).first()
    
    if not invoice:
        print("❌ Fatura bulunamadı!")
        return
    
    print(f"\n{'='*80}")
    print(f"FATURA: {invoice.invoice_number}")
    print(f"UUID: {invoice.invoice_uuid}")
    print(f"Tedarikçi: {invoice.supplier_name}")
    print(f"Toplam: {invoice.payable_amount} TL")
    print(f"{'='*80}\n")
    
    # XML'i parse et
    root = ET.fromstring(invoice.raw_data)
    ns = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    # TaxTotal içindeki tüm TaxSubtotal'ları bul
    tax_totals = root.findall('.//cac:TaxTotal', ns)
    
    print(f"📊 Toplam TaxTotal sayısı: {len(tax_totals)}\n")
    
    for idx, tax_total in enumerate(tax_totals, 1):
        total_amount = tax_total.find('cbc:TaxAmount', ns)
        print(f"\n--- TaxTotal #{idx} ---")
        if total_amount is not None:
            print(f"Toplam Vergi: {total_amount.text} {total_amount.get('currencyID', 'TRY')}")
        
        subtotals = tax_total.findall('.//cac:TaxSubtotal', ns)
        print(f"Alt Vergi Sayısı: {len(subtotals)}\n")
        
        for sub_idx, subtotal in enumerate(subtotals, 1):
            taxable_amount = subtotal.find('cbc:TaxableAmount', ns)
            tax_amount = subtotal.find('cbc:TaxAmount', ns)
            percent = subtotal.find('cbc:Percent', ns)
            
            tax_scheme = subtotal.find('.//cac:TaxScheme', ns)
            tax_name = tax_scheme.find('cbc:Name', ns) if tax_scheme is not None else None
            tax_code = tax_scheme.find('cbc:TaxTypeCode', ns) if tax_scheme is not None else None
            
            print(f"  Vergi #{sub_idx}:")
            print(f"    Vergi Adı: {tax_name.text if tax_name is not None else 'N/A'}")
            print(f"    Vergi Kodu: {tax_code.text if tax_code is not None else 'N/A'}")
            print(f"    Matrah: {taxable_amount.text if taxable_amount is not None else '0'} TL")
            print(f"    Vergi Tutarı: {tax_amount.text if tax_amount is not None else '0'} TL")
            print(f"    Oran: %{percent.text if percent is not None else '0'}")
            print()
    
    # Şu anki DB'de ne var?
    print(f"\n{'='*80}")
    print("📝 Şu Anki DB Verileri:")
    print(f"{'='*80}")
    print(f"tax_total (DB): {invoice.tax_total}")
    print(f"tax_exclusive_amount (DB): {invoice.tax_exclusive_amount}")
    print(f"tax_inclusive_amount (DB): {invoice.tax_inclusive_amount}")
    print(f"payable_amount (DB): {invoice.payable_amount}")
    
    # InvoiceLines'ı da kontrol et
    print(f"\n{'='*80}")
    print("📋 Fatura Satırları:")
    print(f"{'='*80}")
    
    invoice_lines = root.findall('.//cac:InvoiceLine', ns)
    for line in invoice_lines:
        line_id = line.find('cbc:ID', ns)
        item_name = line.find('.//cbc:Name', ns)
        line_ext = line.find('cbc:LineExtensionAmount', ns)
        quantity = line.find('cbc:InvoicedQuantity', ns)
        
        print(f"\nSatır #{line_id.text if line_id is not None else 'N/A'}:")
        print(f"  Ürün/Hizmet: {item_name.text if item_name is not None else 'N/A'}")
        print(f"  Miktar: {quantity.text if quantity is not None else '1'} {quantity.get('unitCode', '') if quantity is not None else ''}")
        print(f"  Tutar: {line_ext.text if line_ext is not None else '0'} TL")
        
        # Satır bazlı vergiler var mı?
        line_taxes = line.findall('.//cac:TaxTotal', ns)
        if line_taxes:
            print(f"  Satır Vergileri: {len(line_taxes)} adet")
            for lt in line_taxes:
                lt_amount = lt.find('cbc:TaxAmount', ns)
                print(f"    - {lt_amount.text if lt_amount is not None else '0'} TL")

if __name__ == '__main__':
    analyze_invoice_taxes()
