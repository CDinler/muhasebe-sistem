import pymysql
import xml.etree.ElementTree as ET

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()

# Get invoice raw_data
cursor.execute("SELECT id, invoice_number, supplier_name, raw_data FROM einvoices WHERE invoice_uuid = '9d24ecf5-fbaf-49e8-82ab-233761b7e67e'")
row = cursor.fetchone()

if row:
    invoice_id, invoice_number, supplier_name, raw_xml = row
    print(f"✅ Fatura bulundu: {invoice_number} - {supplier_name}")
    print(f"Raw Data Boyutu: {len(raw_xml)} byte")
    
    # raw_xml JSON string olarak saklanmış olabilir, decode et
    import json
    try:
        raw_xml = json.loads(raw_xml)
    except:
        pass  # Zaten string ise devam et
    
    # Parse XML
    try:
        root = ET.fromstring(raw_xml)
        
        # Namespaces
        ns = {
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
        }
        
        print("\n" + "="*100)
        print("📋 INVOICE LINES (cac:InvoiceLine)")
        print("="*100)
        
        for i, line in enumerate(root.findall('.//cac:InvoiceLine', ns), 1):
            line_id = line.find('cbc:ID', ns)
            item_name = line.find('.//cbc:Name', ns)
            quantity = line.find('.//cbc:InvoicedQuantity', ns)
            unit_code = line.find('.//cbc:InvoicedQuantity[@unitCode]', ns)
            price = line.find('.//cbc:PriceAmount', ns)
            line_amount = line.find('cbc:LineExtensionAmount', ns)
            
            print(f"\nSatır {i} (ID: {line_id.text if line_id is not None else 'N/A'}):")
            print(f"  Ürün/Hizmet: {item_name.text if item_name is not None else 'N/A'}")
            print(f"  Miktar: {quantity.text if quantity is not None else 'N/A'} {unit_code.get('unitCode') if unit_code is not None else ''}")
            print(f"  Birim Fiyat: {price.text if price is not None else 'N/A'}")
            print(f"  Satır Tutarı: {line_amount.text if line_amount is not None else 'N/A'}")
            
            # TaxTotal in line
            for tax in line.findall('.//cac:TaxTotal/cac:TaxSubtotal', ns):
                tax_amount = tax.find('cbc:TaxAmount', ns)
                percent = tax.find('.//cbc:Percent', ns)
                tax_scheme = tax.find('.//cbc:TaxTypeCode', ns)
                print(f"  Vergi: {tax_scheme.text if tax_scheme is not None else 'N/A'} %{percent.text if percent is not None else 'N/A'} = {tax_amount.text if tax_amount is not None else 'N/A'}")
        
        print("\n" + "="*100)
        print("💰 ALLOWANCE/CHARGE (Masraf/İndirim)")
        print("="*100)
        
        for ac in root.findall('.//cac:AllowanceCharge', ns):
            charge_indicator = ac.find('cbc:ChargeIndicator', ns)
            amount = ac.find('cbc:Amount', ns)
            reason = ac.find('cbc:AllowanceChargeReason', ns)
            multiplier = ac.find('cbc:MultiplierFactorNumeric', ns)
            base_amount = ac.find('cbc:BaseAmount', ns)
            
            print(f"\n{'MASRAF' if charge_indicator is not None and charge_indicator.text.lower() == 'true' else 'İNDİRİM'}:")
            print(f"  Açıklama: {reason.text if reason is not None else 'N/A'}")
            print(f"  Tutar: {amount.text if amount is not None else 'N/A'}")
            print(f"  Çarpan: {multiplier.text if multiplier is not None else 'N/A'}")
            print(f"  Matrah: {base_amount.text if base_amount is not None else 'N/A'}")
        
        print("\n" + "="*100)
        print("🔒 TAX TOTAL (Toplam Vergiler)")
        print("="*100)
        
        for tax_total in root.findall('.//cac:TaxTotal', ns):
            total_amount = tax_total.find('cbc:TaxAmount', ns)
            print(f"\nToplam Vergi: {total_amount.text if total_amount is not None else 'N/A'}")
            
            for subtotal in tax_total.findall('cac:TaxSubtotal', ns):
                taxable_amount = subtotal.find('cbc:TaxableAmount', ns)
                tax_amount = subtotal.find('cbc:TaxAmount', ns)
                percent = subtotal.find('.//cbc:Percent', ns)
                tax_scheme = subtotal.find('.//cbc:TaxTypeCode', ns)
                
                print(f"  {tax_scheme.text if tax_scheme is not None else 'N/A'}: Matrah={taxable_amount.text if taxable_amount is not None else 'N/A'} Oran=%{percent.text if percent is not None else 'N/A'} Tutar={tax_amount.text if tax_amount is not None else 'N/A'}")
        
        print("\n" + "="*100)
        print("💵 LEGAL MONETARY TOTAL")
        print("="*100)
        
        lmt = root.find('.//cac:LegalMonetaryTotal', ns)
        if lmt is not None:
            line_ext = lmt.find('cbc:LineExtensionAmount', ns)
            tax_exc = lmt.find('cbc:TaxExclusiveAmount', ns)
            tax_inc = lmt.find('cbc:TaxInclusiveAmount', ns)
            allowance_total = lmt.find('cbc:AllowanceTotalAmount', ns)
            charge_total = lmt.find('cbc:ChargeTotalAmount', ns)
            payable = lmt.find('cbc:PayableAmount', ns)
            
            print(f"Line Extension Amount: {line_ext.text if line_ext is not None else 'N/A'}")
            print(f"Tax Exclusive Amount: {tax_exc.text if tax_exc is not None else 'N/A'}")
            print(f"Tax Inclusive Amount: {tax_inc.text if tax_inc is not None else 'N/A'}")
            print(f"Allowance Total: {allowance_total.text if allowance_total is not None else 'N/A'}")
            print(f"Charge Total: {charge_total.text if charge_total is not None else 'N/A'}")
            print(f"Payable Amount: {payable.text if payable is not None else 'N/A'}")
        
    except Exception as e:
        print(f"❌ XML parse hatası: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Fatura bulunamadı!")

cursor.close()
conn.close()
