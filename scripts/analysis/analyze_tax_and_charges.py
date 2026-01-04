"""
Faturalardaki vergi ve masrafları analiz et
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import sys

sys.path.insert(0, str(Path(__file__).parent))
from app.models.einvoice import EInvoice
from app.core.config import settings

# XML namespace
NS = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
}

def analyze_invoice(ettn: str):
    """Belirli bir faturanın vergi ve masraflarını analiz et"""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    with Session(engine) as session:
        stmt = select(EInvoice).where(EInvoice.invoice_uuid == ettn)
        invoice = session.execute(stmt).scalar_one_or_none()
        
        if not invoice:
            print(f"❌ Fatura bulunamadı: {ettn}")
            return
        
        print(f"\n{'='*80}")
        print(f"FATURA: {ettn}")
        print(f"Belge No: {invoice.invoice_number}")
        print(f"Tedarikçi: {invoice.supplier_name}")
        print(f"{'='*80}\n")
        
        if not invoice.raw_data:
            print("❌ raw_data yok!")
            return
        
        try:
            root = ET.fromstring(invoice.raw_data)
            
            # 1. TaxTotal - Fatura seviyesinde toplam vergiler
            print("📊 FATURA SEVİYESİ VERGİLER (TaxTotal):")
            print("-" * 80)
            
            tax_totals = root.findall('.//cac:TaxTotal', NS)
            if tax_totals:
                for i, tax_total in enumerate(tax_totals, 1):
                    # Toplam vergi tutarı
                    tax_amount_elem = tax_total.find('cbc:TaxAmount', NS)
                    if tax_amount_elem is not None:
                        tax_amount = tax_amount_elem.text
                        currency = tax_amount_elem.get('currencyID', 'TRY')
                        print(f"  Toplam Vergi #{i}: {tax_amount} {currency}")
                    
                    # Alt vergi detayları
                    tax_subtotals = tax_total.findall('.//cac:TaxSubtotal', NS)
                    for j, subtotal in enumerate(tax_subtotals, 1):
                        taxable_amount = subtotal.find('cbc:TaxableAmount', NS)
                        tax_amt = subtotal.find('cbc:TaxAmount', NS)
                        tax_category = subtotal.find('.//cac:TaxCategory', NS)
                        
                        matrah = taxable_amount.text if taxable_amount is not None else "N/A"
                        tutar = tax_amt.text if tax_amt is not None else "N/A"
                        
                        if tax_category is not None:
                            tax_scheme = tax_category.find('.//cac:TaxScheme/cbc:Name', NS)
                            percent = tax_category.find('cbc:Percent', NS)
                            
                            vergi_adi = tax_scheme.text if tax_scheme is not None else "N/A"
                            oran = percent.text if percent is not None else "N/A"
                            
                            print(f"    {j}. {vergi_adi} %{oran}")
                            print(f"       Matrah: {matrah} TRY, Tutar: {tutar} TRY")
            else:
                print("  ❌ TaxTotal bulunamadı")
            
            # 2. AllowanceCharge - İndirim/Masraflar
            print(f"\n📊 İNDİRİM/MASRAFLAR (AllowanceCharge):")
            print("-" * 80)
            
            allowance_charges = root.findall('.//cac:AllowanceCharge', NS)
            if allowance_charges:
                for i, ac in enumerate(allowance_charges, 1):
                    charge_indicator = ac.find('cbc:ChargeIndicator', NS)
                    is_charge = charge_indicator.text.lower() == 'true' if charge_indicator is not None else False
                    
                    reason = ac.find('cbc:AllowanceChargeReason', NS)
                    amount = ac.find('cbc:Amount', NS)
                    
                    tip = "MASRAF/ÜCRET" if is_charge else "İNDİRİM"
                    neden = reason.text if reason is not None else "N/A"
                    tutar = amount.text if amount is not None else "N/A"
                    
                    print(f"  {i}. [{tip}] {neden}: {tutar} TRY")
                    
                    # Bu masrafın vergileri
                    ac_tax_total = ac.find('.//cac:TaxTotal', NS)
                    if ac_tax_total is not None:
                        ac_tax_amount = ac_tax_total.find('cbc:TaxAmount', NS)
                        if ac_tax_amount is not None:
                            print(f"     └─ Vergi: {ac_tax_amount.text} TRY")
            else:
                print("  ℹ️  AllowanceCharge bulunamadı")
            
            # 3. LegalMonetaryTotal - Genel toplam bilgileri
            print(f"\n📊 GENEL TOPLAM BİLGİLERİ:")
            print("-" * 80)
            
            monetary = root.find('.//cac:LegalMonetaryTotal', NS)
            if monetary is not None:
                fields = [
                    ('LineExtensionAmount', 'Satır Toplamı'),
                    ('TaxExclusiveAmount', 'Vergi Hariç Tutar'),
                    ('TaxInclusiveAmount', 'Vergi Dahil Tutar'),
                    ('AllowanceTotalAmount', 'Toplam İndirim'),
                    ('ChargeTotalAmount', 'Toplam Masraf'),
                    ('PayableAmount', 'Ödenecek Tutar'),
                ]
                
                for field, label in fields:
                    elem = monetary.find(f'cbc:{field}', NS)
                    if elem is not None:
                        print(f"  {label}: {elem.text} TRY")
            
            # 4. WithholdingTaxTotal - Tevkifat
            print(f"\n📊 TEVKİFAT (WithholdingTaxTotal):")
            print("-" * 80)
            
            withholding = root.findall('.//cac:WithholdingTaxTotal', NS)
            if withholding:
                for i, wt in enumerate(withholding, 1):
                    tax_amount = wt.find('cbc:TaxAmount', NS)
                    if tax_amount is not None:
                        print(f"  {i}. Tevkifat: {tax_amount.text} TRY")
                        
                    tax_subtotals = wt.findall('.//cac:TaxSubtotal', NS)
                    for j, subtotal in enumerate(tax_subtotals, 1):
                        tax_category = subtotal.find('.//cac:TaxCategory', NS)
                        if tax_category is not None:
                            percent = tax_category.find('cbc:Percent', NS)
                            if percent is not None:
                                print(f"     %{percent.text}")
            else:
                print("  ℹ️  Tevkifat yok")
            
        except Exception as e:
            print(f"❌ XML parse hatası: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    # Test faturaları
    test_invoices = [
        '9d24ecf5-fbaf-49e8-82ab-233761b7e67e',  # Vergi ve masraf örneği
        '48ad10c7-de65-47bb-8619-f7b0ca37755f',  # KDV boş olan
        '68cede74-620b-4bb6-9b7d-41836412b4a4',  # KDV boş olan
    ]
    
    for ettn in test_invoices:
        analyze_invoice(ettn)
        print("\n")
