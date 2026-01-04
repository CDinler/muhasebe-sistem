"""E-Fatura XML Import Service

UBL-TR formatındaki XML dosyalarını parse edip database'e kaydeder.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, date, time
from decimal import Decimal
from typing import Dict, Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.einvoice import EInvoice
from app.models.contact import Contact


# UBL-TR Namespace'leri
NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
}


def _prepare_raw_data(data: Dict) -> Dict:
    """Date ve Decimal objelerini JSON-serializable formata çevir"""
    result = {}
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, time):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, list):
            result[key] = [_prepare_raw_data(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict):
            result[key] = _prepare_raw_data(value)
        else:
            result[key] = value
    return result


def get_text(element, path: str, namespaces: dict = NAMESPACES) -> Optional[str]:
    """XML element'ten text değer çıkar"""
    if element is None:
        return None
    found = element.find(path, namespaces)
    return found.text.strip() if found is not None and found.text else None


def get_decimal(element, path: str, namespaces: dict = NAMESPACES) -> Optional[Decimal]:
    """XML element'ten Decimal değer çıkar"""
    text = get_text(element, path, namespaces)
    if text:
        try:
            return Decimal(text)
        except:
            return None
    return None


def parse_xml_invoice(xml_content: bytes, filename: str) -> Tuple[Dict, List[str]]:
    """
    UBL-TR XML faturayı parse et
    
    Returns:
        (invoice_data, errors) tuple
    """
    errors = []
    
    try:
        # XML parse
        root = ET.fromstring(xml_content)
        
        # ETTN (UUID)
        ettn = get_text(root, './/cbc:UUID')
        
        # Fatura Numarası
        invoice_number = get_text(root, './/cbc:ID')
        
        # Fatura Tarihi
        invoice_date_str = get_text(root, './/cbc:IssueDate')
        invoice_date = None
        if invoice_date_str:
            try:
                invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date()
            except:
                errors.append(f'Geçersiz tarih: {invoice_date_str}')
        
        # İmzalanma Zamanı (SigningTime)
        signing_time = None
        # Önce namespace'li deneyalım (xades:SigningTime)
        signing_time_str = get_text(root, './/{*}SigningTime')
        if not signing_time_str:
            # Namespace olmadan da dene
            signing_time_str = get_text(root, './/SigningTime')
        
        if signing_time_str:
            try:
                # ISO 8601 format: 2025-12-10T11:40:07.1066709Z veya +03:00
                # Timezone bilgisini temizle
                cleaned_time = signing_time_str.replace('Z', '+00:00')
                # +03:00 gibi timezone varsa doğrudan parse et
                signing_time = datetime.fromisoformat(cleaned_time)
            except:
                try:
                    # Alternatif format dene (timezone olmadan)
                    signing_time = datetime.strptime(signing_time_str[:19], '%Y-%m-%dT%H:%M:%S')
                except:
                    pass  # SigningTime opsiyonel
        
        # Fatura Tipi & Senaryo
        invoice_type_code = get_text(root, './/cbc:InvoiceTypeCode')
        invoice_profile = get_text(root, './/cbc:ProfileID')
        
        # Para Birimi
        currency = get_text(root, './/cbc:DocumentCurrencyCode') or 'TRY'
        
        # Kur Bilgisi
        exchange_rate = get_decimal(root, './/cac:PricingExchangeRate/cbc:CalculationRate')
        
        # === SUPPLIER (Satıcı - Gönderici) ===
        supplier = root.find('.//cac:AccountingSupplierParty/cac:Party', NAMESPACES)
        
        # Supplier VKN/TCKN
        supplier_tax_number = None
        supplier_id_scheme = 'VKN'
        if supplier:
            tax_scheme = supplier.find('.//cac:PartyTaxScheme', NAMESPACES)
            if tax_scheme:
                tax_id = get_text(tax_scheme, './/cbc:TaxLevelCode')
                if not tax_id:
                    tax_id_elem = tax_scheme.find('.//cac:TaxScheme/cbc:ID', NAMESPACES)
                    if tax_id_elem is not None:
                        supplier_id_scheme = tax_id_elem.text.strip() if tax_id_elem.text else 'VKN'
                    
                    tax_id = get_text(tax_scheme, './/cac:TaxScheme/cbc:TaxTypeCode')
                
                if tax_id:
                    supplier_tax_number = tax_id.strip()
                    # TCKN 11 hane, VKN 10 hane
                    if len(supplier_tax_number) == 11:
                        supplier_id_scheme = 'TCKN'
            
            # E-arşivde PartyIdentification/ID olarak da olabilir
            if not supplier_tax_number:
                party_id = get_text(supplier, './/cac:PartyIdentification/cbc:ID[@schemeID="VKN"]')
                if not party_id:
                    party_id = get_text(supplier, './/cac:PartyIdentification/cbc:ID[@schemeID="TCKN"]')
                if not party_id:
                    party_id = get_text(supplier, './/cac:PartyIdentification/cbc:ID')
                if party_id:
                    supplier_tax_number = party_id.strip()
                    if len(supplier_tax_number) == 11:
                        supplier_id_scheme = 'TCKN'
        
        # Supplier İsim
        supplier_name = None
        if supplier:
            party_name = supplier.find('.//cac:PartyName/cbc:Name', NAMESPACES)
            if party_name is not None and party_name.text:
                supplier_name = party_name.text.strip()
            else:
                # Alternatif isim alanı
                party_legal_entity = supplier.find('.//cac:PartyLegalEntity/cbc:RegistrationName', NAMESPACES)
                if party_legal_entity is not None and party_legal_entity.text:
                    supplier_name = party_legal_entity.text.strip()
            
            # Şahıs için FirstName + FamilyName
            if not supplier_name:
                person = supplier.find('.//cac:Person', NAMESPACES)
                if person is not None:
                    first_name = get_text(person, './/cbc:FirstName')
                    family_name = get_text(person, './/cbc:FamilyName')
                    if first_name and family_name:
                        supplier_name = f"{first_name} {family_name}".strip()
                    elif first_name:
                        supplier_name = first_name.strip()
                    elif family_name:
                        supplier_name = family_name.strip()
        
        # Supplier Adres
        supplier_address = None
        supplier_city = None
        supplier_district = None
        supplier_postal_code = None
        if supplier:
            address = supplier.find('.//cac:PostalAddress', NAMESPACES)
            if address is not None:
                # Sokak
                street = get_text(address, './/cbc:StreetName')
                building = get_text(address, './/cbc:BuildingNumber')
                room = get_text(address, './/cbc:Room')
                
                addr_parts = []
                if street:
                    addr_parts.append(street)
                if building:
                    addr_parts.append(f'No:{building}')
                if room:
                    addr_parts.append(room)
                
                supplier_address = ' '.join(addr_parts) if addr_parts else None
                
                # Şehir & İlçe
                supplier_city = get_text(address, './/cbc:CityName')
                supplier_district = get_text(address, './/cbc:District')
                supplier_postal_code = get_text(address, './/cbc:PostalZone')
        
        # Supplier Vergi Dairesi
        supplier_tax_office = None
        if supplier:
            tax_office = get_text(supplier, './/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name')
            if tax_office:
                supplier_tax_office = tax_office.strip()
        
        # Supplier İletişim
        supplier_phone = None
        supplier_email = None
        supplier_iban = None
        if supplier:
            contact = supplier.find('.//cac:Contact', NAMESPACES)
            if contact is not None:
                supplier_phone = get_text(contact, './/cbc:Telephone')
                supplier_email = get_text(contact, './/cbc:ElectronicMail')
        
        # Supplier IBAN (PaymentMeans içinde PayeeFinancialAccount)
        # İlk TRY para birimli IBAN'ı alıyoruz
        payment_means_list = root.findall('.//cac:PaymentMeans', NAMESPACES)
        for payment_means in payment_means_list:
            currency_code = get_text(payment_means, './/cac:PayeeFinancialAccount/cbc:CurrencyCode')
            if currency_code == 'TRY' or not currency_code:  # TRY veya para birimi belirtilmemiş
                iban = get_text(payment_means, './/cac:PayeeFinancialAccount/cbc:ID')
                if iban and iban.startswith('TR'):  # IBAN formatı kontrolü
                    supplier_iban = iban.strip()
                    break  # İlk TRY IBAN'ı bulduk, çık
        
        # === CUSTOMER (Alıcı) ===
        customer = root.find('.//cac:AccountingCustomerParty/cac:Party', NAMESPACES)
        customer_tax_number = None
        customer_name = None
        customer_tax_office = None
        customer_address = None
        customer_city = None
        customer_district = None
        customer_postal_code = None
        customer_phone = None
        customer_email = None
        
        if customer:
            # Vergi Numarası - PartyTaxScheme/TaxID
            tax_scheme = customer.find('.//cac:PartyTaxScheme', NAMESPACES)
            if tax_scheme:
                customer_tax_number = get_text(tax_scheme, './/cbc:TaxID')
                if not customer_tax_number:
                    customer_tax_number = get_text(tax_scheme, './/cac:TaxScheme/cbc:TaxTypeCode')
                
                # Vergi Dairesi
                tax_office = get_text(tax_scheme, './/cac:TaxScheme/cbc:Name')
                if tax_office:
                    customer_tax_office = tax_office.strip()
            
            # E-arşivde PartyIdentification/ID olarak da olabilir
            if not customer_tax_number:
                party_id = get_text(customer, './/cac:PartyIdentification/cbc:ID[@schemeID="VKN"]')
                if not party_id:
                    party_id = get_text(customer, './/cac:PartyIdentification/cbc:ID[@schemeID="TCKN"]')
                if not party_id:
                    party_id = get_text(customer, './/cac:PartyIdentification/cbc:ID')
                if party_id:
                    customer_tax_number = party_id.strip()
            
            # Firma Adı
            party_name = customer.find('.//cac:PartyName/cbc:Name', NAMESPACES)
            if party_name is not None and party_name.text:
                customer_name = party_name.text.strip()
            
            # Şahıs için FirstName + FamilyName
            if not customer_name:
                person = customer.find('.//cac:Person', NAMESPACES)
                if person is not None:
                    first_name = get_text(person, './/cbc:FirstName')
                    family_name = get_text(person, './/cbc:FamilyName')
                    if first_name and family_name:
                        customer_name = f"{first_name} {family_name}".strip()
                    elif first_name:
                        customer_name = first_name.strip()
                    elif family_name:
                        customer_name = family_name.strip()
            
            # Adres Bilgileri
            postal_address = customer.find('.//cac:PostalAddress', NAMESPACES)
            if postal_address is not None:
                street = get_text(postal_address, './/cbc:StreetName')
                building = get_text(postal_address, './/cbc:BuildingNumber')
                customer_city = get_text(postal_address, './/cbc:CityName')
                customer_district = get_text(postal_address, './/cbc:District')
                customer_postal_code = get_text(postal_address, './/cbc:PostalZone')
                
                # Adres birleştir
                address_parts = []
                if street:
                    address_parts.append(street)
                if building:
                    address_parts.append(f"No: {building}")
                if address_parts:
                    customer_address = ' '.join(address_parts)
            
            # İletişim Bilgileri
            contact = customer.find('.//cac:Contact', NAMESPACES)
            if contact is not None:
                customer_phone = get_text(contact, './/cbc:Telephone')
                customer_email = get_text(contact, './/cbc:ElectronicMail')
        
        # === TUTARLAR ===
        
        # Mal Hizmet Toplamı (KDV Hariç)
        line_extension_amount = get_decimal(root, './/cac:LegalMonetaryTotal/cbc:LineExtensionAmount')
        
        # İndirim ve Artırım (UBL-TR)
        allowance_total = get_decimal(root, './/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount')
        charge_total = get_decimal(root, './/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount')
        
        # Vergi Hariç Tutar (İndirim/Artırım Sonrası, KDV Öncesi)
        tax_exclusive_amount = get_decimal(root, './/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount')
        
        # Vergiler Dahil Toplam (KDV Dahil)
        tax_inclusive_amount = get_decimal(root, './/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount')
        
        # Ödenecek Tutar
        payable_amount = get_decimal(root, './/cac:LegalMonetaryTotal/cbc:PayableAmount')
        
        # Stopaj Toplamı
        withholding_total = None
        withholding_subtotal = root.find('.//cac:WithholdingTaxTotal/cac:TaxSubtotal', NAMESPACES)
        if withholding_subtotal is not None:
            withholding_total = get_decimal(withholding_subtotal, './/cbc:TaxAmount')
        
        # === KDV Dağılımı ===
        vat_0_base = vat_0_amount = None
        vat_1_base = vat_1_amount = None
        vat_8_base = vat_8_amount = None
        vat_10_base = vat_10_amount = None
        vat_18_base = vat_18_amount = None
        vat_20_base = vat_20_amount = None
        
        tax_total = root.find('.//cac:TaxTotal', NAMESPACES)
        if tax_total is not None:
            for subtotal in tax_total.findall('.//cac:TaxSubtotal', NAMESPACES):
                tax_category = subtotal.find('.//cac:TaxCategory', NAMESPACES)
                if tax_category is not None:
                    percent_text = get_text(tax_category, './/cbc:Percent')
                    if percent_text:
                        try:
                            percent = int(float(percent_text))
                            base = get_decimal(subtotal, './/cbc:TaxableAmount')
                            amount = get_decimal(subtotal, './/cbc:TaxAmount')
                            
                            if percent == 0:
                                vat_0_base = base
                                vat_0_amount = amount
                            elif percent == 1:
                                vat_1_base = base
                                vat_1_amount = amount
                            elif percent == 8:
                                vat_8_base = base
                                vat_8_amount = amount
                            elif percent == 10:
                                vat_10_base = base
                                vat_10_amount = amount
                            elif percent == 18:
                                vat_18_base = base
                                vat_18_amount = amount
                            elif percent == 20:
                                vat_20_base = base
                                vat_20_amount = amount
                        except:
                            pass
        
        # === VERGİ DETAYLARI (TaxSubtotals) ===
        tax_details = []
        if tax_total is not None:
            for subtotal in tax_total.findall('.//cac:TaxSubtotal', NAMESPACES):
                tax_category = subtotal.find('.//cac:TaxCategory', NAMESPACES)
                tax_scheme = tax_category.find('.//cac:TaxScheme', NAMESPACES) if tax_category is not None else None
                
                tax_detail = {
                    'tax_type_code': get_text(tax_scheme, './/cbc:TaxTypeCode') if tax_scheme is not None else None,
                    'tax_name': get_text(tax_scheme, './/cbc:Name') if tax_scheme is not None else None,
                    'tax_percent': get_decimal(subtotal, './/cbc:Percent'),
                    'taxable_amount': get_decimal(subtotal, './/cbc:TaxableAmount'),
                    'tax_amount': get_decimal(subtotal, './/cbc:TaxAmount'),
                    'currency_code': currency
                }
                
                # İstisna bilgileri (varsa)
                exemption_reason = get_text(subtotal, './/cbc:TaxExemptionReason')
                exemption_code = get_text(subtotal, './/cbc:TaxExemptionReasonCode')
                
                if exemption_reason:
                    tax_detail['exemption_reason'] = exemption_reason
                if exemption_code:
                    tax_detail['exemption_reason_code'] = exemption_code
                
                tax_details.append(tax_detail)
        
        # === FATURA KALEMLERİ ===
        lines_data = []
        for line in root.findall('.//cac:InvoiceLine', NAMESPACES):
            line_dict = {
                'line_id': get_text(line, './/cbc:ID'),
                'item_name': get_text(line, './/cac:Item/cbc:Name'),
                'quantity': get_decimal(line, './/cbc:InvoicedQuantity'),
                'unit_code': get_text(line, './/cbc:InvoicedQuantity[@unitCode]'),  # Birim
                'unit_price': get_decimal(line, './/cac:Price/cbc:PriceAmount'),
                'line_amount': get_decimal(line, './/cbc:LineExtensionAmount')
            }
            
            # KDV oranı (kalemde)
            tax_subtotal = line.find('.//cac:TaxTotal/cac:TaxSubtotal', NAMESPACES)
            if tax_subtotal is not None:
                line_dict['vat_percent'] = get_text(tax_subtotal, './/cac:TaxCategory/cbc:Percent')
                line_dict['vat_amount'] = get_decimal(tax_subtotal, './/cbc:TaxAmount')
            
            lines_data.append(line_dict)
        
        # Invoice Data Dictionary
        invoice_data = {
            'ettn': ettn,
            'invoice_number': invoice_number,
            'invoice_date': invoice_date,
            'signing_time': signing_time,
            'invoice_type': invoice_type_code,
            'invoice_scenario': invoice_profile,
            'currency_code': currency,
            'exchange_rate': exchange_rate,
            
            'supplier_tax_number': supplier_tax_number,
            'supplier_id_scheme': supplier_id_scheme,
            'supplier_name': supplier_name,
            'supplier_tax_office': supplier_tax_office,
            'supplier_address': supplier_address,
            'supplier_city': supplier_city,
            'supplier_district': supplier_district,
            'supplier_postal_code': supplier_postal_code,
            'supplier_phone': supplier_phone,
            'supplier_email': supplier_email,
            'supplier_iban': supplier_iban,
            
            'customer_tax_number': customer_tax_number,
            'customer_name': customer_name,
            'customer_tax_office': customer_tax_office,
            'customer_address': customer_address,
            'customer_city': customer_city,
            'customer_district': customer_district,
            'customer_postal_code': customer_postal_code,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            
            'line_extension_amount': line_extension_amount,
            'allowance_total': allowance_total,
            'charge_total': charge_total,
            'tax_exclusive_amount': tax_exclusive_amount,
            'tax_inclusive_amount': tax_inclusive_amount,
            'payable_amount': payable_amount,
            'withholding_tax_amount': withholding_total,
            
            'tax_details': tax_details,  # VERGİ DETAYLARI
            'lines': lines_data,
            'source_file': filename
        }
        
        return invoice_data, errors
        
    except ET.ParseError as e:
        errors.append(f'XML parse hatası: {str(e)}')
        return {}, errors
    except Exception as e:
        errors.append(f'Beklenmeyen hata: {str(e)}')
        return {}, errors


def create_einvoice_from_xml(db: Session, invoice_data: Dict) -> EInvoice:
    """Parse edilmiş XML verisinden EInvoice oluştur veya güncelle
    
    XML HER ZAMAN ÖNCELİKLİDİR:
    - Eğer UUID ile eşleşen kayıt varsa ve has_xml=0 (PDF'den parse) ise:
      → Mevcut kaydı XML verisine göre güncelle (PDF yolunu koru)
    - Eğer UUID ile eşleşen kayıt varsa ve has_xml=1 (zaten XML) ise:
      → Duplicate, skip
    - Eğer UUID ile eşleşen kayıt yoksa:
      → Yeni kayıt oluştur
    """
    
    # Check if already exists (UUID unique)
    existing = None
    if invoice_data.get('ettn'):
        existing = db.query(EInvoice).filter(
            EInvoice.invoice_uuid == invoice_data['ettn']
        ).first()
    
    # XML öncelikli güncelleme: PDF'den parse edilmiş kayıt varsa XML ile güncelle
    if existing:
        if existing.has_xml == 0:
            # PDF'den parse edilmiş → XML ile güncelle (PDF yolunu koru)
            pdf_path_backup = existing.pdf_path  # PDF yolunu koru
            
            # XML verisini uygula
            existing.invoice_number = invoice_data.get('invoice_number')
            existing.issue_date = invoice_data.get('invoice_date')
            existing.signing_time = invoice_data.get('signing_time')
            existing.invoice_profile = invoice_data.get('invoice_scenario')
            existing.invoice_type = invoice_data.get('invoice_type')
            existing.invoice_category = invoice_data.get('invoice_category', existing.invoice_category)
            existing.xml_file_path = invoice_data.get('xml_file_path')
            existing.xml_hash = invoice_data.get('xml_hash')
            
            existing.supplier_name = invoice_data.get('supplier_name')
            existing.supplier_tax_number = invoice_data.get('supplier_tax_number')
            existing.supplier_id_scheme = invoice_data.get('supplier_id_scheme')
            existing.supplier_tax_office = invoice_data.get('supplier_tax_office')
            existing.supplier_address = invoice_data.get('supplier_address')
            existing.supplier_city = invoice_data.get('supplier_city')
            existing.supplier_district = invoice_data.get('supplier_district')
            existing.supplier_postal_code = invoice_data.get('supplier_postal_code')
            existing.supplier_phone = invoice_data.get('supplier_phone')
            existing.supplier_email = invoice_data.get('supplier_email')
            existing.supplier_iban = invoice_data.get('supplier_iban')
            
            existing.customer_tax_number = invoice_data.get('customer_tax_number')
            existing.customer_name = invoice_data.get('customer_name')
            
            existing.currency_code = invoice_data.get('currency_code', 'TRY')
            existing.exchange_rate = invoice_data.get('exchange_rate')
            
            existing.line_extension_amount = invoice_data.get('line_extension_amount')
            existing.allowance_total = invoice_data.get('allowance_total')
            existing.charge_total = invoice_data.get('charge_total')
            existing.tax_exclusive_amount = invoice_data.get('tax_exclusive_amount')
            existing.tax_inclusive_amount = invoice_data.get('tax_inclusive_amount')
            existing.payable_amount = invoice_data.get('payable_amount')
            existing.withholding_tax_amount = invoice_data.get('withholding_tax_amount')
            
            # XML ile parse edildi olarak işaretle, PDF'i koru
            existing.has_xml = 1
            existing.source = 'xml'
            existing.pdf_path = pdf_path_backup  # PDF yolunu geri yükle
            existing.raw_data = _prepare_raw_data(invoice_data)
            
            # CONTACT EŞLEŞTİRMESİ YAP (PDF→XML güncellemesinde de gerekli!)
            invoice_category = invoice_data.get('invoice_category', existing.invoice_category)
            
            if 'incoming' in invoice_category:
                # GELEN FATURA: Supplier (tedarikçi) cari olacak
                contact_vkn = invoice_data.get('supplier_tax_number')
                contact_name = invoice_data.get('supplier_name', 'Bilinmeyen Firma')
                contact_tax_office = invoice_data.get('supplier_tax_office')
                contact_address = invoice_data.get('supplier_address')
                contact_city = invoice_data.get('supplier_city')
                contact_district = invoice_data.get('supplier_district')
                contact_postal_code = invoice_data.get('supplier_postal_code')
                contact_phone = invoice_data.get('supplier_phone')
                contact_email = invoice_data.get('supplier_email')
                contact_iban = invoice_data.get('supplier_iban')
                contact_type = 'SUPPLIER'
            else:
                # GİDEN FATURA: Customer (müşteri) cari olacak
                contact_vkn = invoice_data.get('customer_tax_number')
                contact_name = invoice_data.get('customer_name', 'Bilinmeyen Müşteri')
                contact_tax_office = invoice_data.get('customer_tax_office')
                contact_address = invoice_data.get('customer_address')
                contact_city = invoice_data.get('customer_city')
                contact_district = invoice_data.get('customer_district')
                contact_postal_code = invoice_data.get('customer_postal_code')
                contact_phone = invoice_data.get('customer_phone')
                contact_email = invoice_data.get('customer_email')
                contact_iban = None
                contact_type = 'CUSTOMER'
            
            # Match or Create contact if VKN exists
            if contact_vkn and not existing.contact_id:  # contact_id NULL ise eşleştir
                vkn = contact_vkn
                
                # Numeric CAST ile eşleştir
                contact = db.execute(text("""
                    SELECT id FROM contacts 
                    WHERE CAST(tax_number AS UNSIGNED) = CAST(:vkn AS UNSIGNED)
                    LIMIT 1
                """), {"vkn": vkn}).first()
                
                if contact:
                    # Var olan cari - OLMAYAN bilgileri XML'den güncelle
                    contact_obj = db.query(Contact).filter(Contact.id == contact.id).first()
                    
                    updated = False
                    if not contact_obj.name and contact_name:
                        contact_obj.name = contact_name
                        updated = True
                    if not contact_obj.tax_office and contact_tax_office:
                        contact_obj.tax_office = contact_tax_office
                        updated = True
                    if not contact_obj.address and contact_address:
                        contact_obj.address = contact_address
                        updated = True
                    if not contact_obj.city and contact_city:
                        contact_obj.city = contact_city
                        updated = True
                    if not contact_obj.district and contact_district:
                        contact_obj.district = contact_district
                        updated = True
                    if not contact_obj.postal_code and contact_postal_code:
                        contact_obj.postal_code = contact_postal_code
                        updated = True
                    if not contact_obj.phone and contact_phone:
                        contact_obj.phone = contact_phone
                        updated = True
                    if not contact_obj.email and contact_email:
                        contact_obj.email = contact_email
                        updated = True
                    if not contact_obj.iban and contact_iban:
                        contact_obj.iban = contact_iban
                        updated = True
                    
                    if updated:
                        db.flush()
                    
                    existing.contact_id = contact_obj.id
                    existing.processing_status = 'MATCHED'
                else:
                    # YENİ CARİ OLUŞTUR
                    from app.api.v1.endpoints.einvoices import generate_contact_code
                    new_code = generate_contact_code(db, 'supplier' if contact_type == 'SUPPLIER' else 'customer')
                    
                    new_contact = Contact(
                        code=new_code,
                        name=contact_name,
                        contact_type=contact_type,
                        tax_number=vkn,
                        tax_office=contact_tax_office,
                        address=contact_address,
                        city=contact_city,
                        district=contact_district,
                        postal_code=contact_postal_code,
                        phone=contact_phone,
                        email=contact_email,
                        is_active=True
                    )
                    
                    db.add(new_contact)
                    db.flush()
                    
                    existing.contact_id = new_contact.id
                    existing.processing_status = 'MATCHED'
            
            # === VERGİ DETAYLARINI GÜNCELLE (ESKİLERİ SİL, YENİLERİ EKLE) ===
            from app.models.invoice_tax import InvoiceTax
            
            # Eski vergi kayıtlarını sil
            db.query(InvoiceTax).filter(InvoiceTax.einvoice_id == existing.id).delete()
            
            # Yeni vergi detaylarını ekle
            tax_details = invoice_data.get('tax_details', [])
            if tax_details:
                for tax_detail in tax_details:
                    invoice_tax = InvoiceTax(
                        einvoice_id=existing.id,
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
            db.refresh(existing)
            
            return existing
        else:
            # Zaten XML'den parse edilmiş → Duplicate
            raise ValueError(f"Fatura zaten mevcut (UUID: {invoice_data['ettn']})")
    
    # Yeni kayıt oluştur
    einvoice = EInvoice(
        invoice_number=invoice_data.get('invoice_number'),
        issue_date=invoice_data.get('invoice_date'),
        signing_time=invoice_data.get('signing_time'),
        invoice_uuid=invoice_data.get('ettn'),
        invoice_profile=invoice_data.get('invoice_scenario'),
        invoice_type=invoice_data.get('invoice_type'),
        invoice_category=invoice_data.get('invoice_category', 'incoming'),
        xml_file_path=invoice_data.get('xml_file_path'),
        xml_hash=invoice_data.get('xml_hash'),
        
        supplier_name=invoice_data.get('supplier_name'),
        supplier_tax_number=invoice_data.get('supplier_tax_number'),
        supplier_id_scheme=invoice_data.get('supplier_id_scheme'),
        supplier_tax_office=invoice_data.get('supplier_tax_office'),
        supplier_address=invoice_data.get('supplier_address'),
        supplier_city=invoice_data.get('supplier_city'),
        supplier_district=invoice_data.get('supplier_district'),
        supplier_postal_code=invoice_data.get('supplier_postal_code'),
        supplier_phone=invoice_data.get('supplier_phone'),
        supplier_email=invoice_data.get('supplier_email'),
        supplier_iban=invoice_data.get('supplier_iban'),
        
        customer_tax_number=invoice_data.get('customer_tax_number'),
        customer_name=invoice_data.get('customer_name'),
        
        currency_code=invoice_data.get('currency_code', 'TRY'),
        exchange_rate=invoice_data.get('exchange_rate'),
        
        line_extension_amount=invoice_data.get('line_extension_amount'),
        allowance_total=invoice_data.get('allowance_total'),
        charge_total=invoice_data.get('charge_total'),
        tax_exclusive_amount=invoice_data.get('tax_exclusive_amount'),
        tax_inclusive_amount=invoice_data.get('tax_inclusive_amount'),
        payable_amount=invoice_data.get('payable_amount'),
        withholding_tax_amount=invoice_data.get('withholding_tax_amount'),
        
        # XML'den geldiğini işaretle
        has_xml=1,
        source='xml',
        
        processing_status='IMPORTED',
        raw_data=_prepare_raw_data(invoice_data)  # Date'leri string'e çevir
    )
    
    # GELENvs GİDEN FAKTURABelirle - carivye eklenecek tarafı seç
    invoice_category = invoice_data.get('invoice_category', 'incoming')
    
    if 'incoming' in invoice_category:
        # GELEN FATURA: Supplier (tedarikçi) cari olacak
        contact_vkn = invoice_data.get('supplier_tax_number')
        contact_name = invoice_data.get('supplier_name', 'Bilinmeyen Firma')
        contact_tax_office = invoice_data.get('supplier_tax_office')
        contact_address = invoice_data.get('supplier_address')
        contact_city = invoice_data.get('supplier_city')
        contact_district = invoice_data.get('supplier_district')
        contact_postal_code = invoice_data.get('supplier_postal_code')
        contact_phone = invoice_data.get('supplier_phone')
        contact_email = invoice_data.get('supplier_email')
        contact_iban = invoice_data.get('supplier_iban')
        contact_type = 'SUPPLIER'
    else:
        # GİDEN FATURA: Customer (müşteri) cari olacak
        contact_vkn = invoice_data.get('customer_tax_number')
        contact_name = invoice_data.get('customer_name', 'Bilinmeyen Müşteri')
        contact_tax_office = invoice_data.get('customer_tax_office')
        contact_address = invoice_data.get('customer_address')
        contact_city = invoice_data.get('customer_city')
        contact_district = invoice_data.get('customer_district')
        contact_postal_code = invoice_data.get('customer_postal_code')
        contact_phone = invoice_data.get('customer_phone')
        contact_email = invoice_data.get('customer_email')
        contact_iban = None  # Müşteri IBAN'ı genelde XML'de yok
        contact_type = 'CUSTOMER'
    
    # Match or Create contact if VKN exists
    if contact_vkn:
        vkn = contact_vkn
        
        # Numeric CAST ile eşleştir (collation problemi yok)
        contact = db.execute(text("""
            SELECT id FROM contacts 
            WHERE CAST(tax_number AS UNSIGNED) = CAST(:vkn AS UNSIGNED)
            LIMIT 1
        """), {"vkn": vkn}).first()
        
        if contact:
            # Var olan cari - OLMAYAN bilgileri XML'den güncelle
            contact_obj = db.query(Contact).filter(Contact.id == contact.id).first()
            
            # Boş alanları XML'deki verilerle doldur (mevcut veri varsa dokunma)
            updated = False
            
            if not contact_obj.name and contact_name:
                contact_obj.name = contact_name
                updated = True
            
            if not contact_obj.tax_office and contact_tax_office:
                contact_obj.tax_office = contact_tax_office
                updated = True
            
            if not contact_obj.address and contact_address:
                contact_obj.address = contact_address
                updated = True
            
            if not contact_obj.city and contact_city:
                contact_obj.city = contact_city
                updated = True
            
            if not contact_obj.district and contact_district:
                contact_obj.district = contact_district
                updated = True
            
            if not contact_obj.postal_code and contact_postal_code:
                contact_obj.postal_code = contact_postal_code
                updated = True
            
            if not contact_obj.phone and contact_phone:
                contact_obj.phone = contact_phone
                updated = True
            
            if not contact_obj.email and contact_email:
                contact_obj.email = contact_email
                updated = True
            
            if not contact_obj.iban and contact_iban:
                contact_obj.iban = contact_iban
                updated = True
            
            if updated:
                db.flush()  # Güncellemeleri kaydet
            
            einvoice.contact_id = contact_obj.id
            einvoice.processing_status = 'MATCHED'
        else:
            # YENİ CARİ OLUŞTUR
            # Otomatik cari kodu üret
            from app.api.v1.endpoints.einvoices import generate_contact_code
            new_code = generate_contact_code(db, 'supplier' if contact_type == 'SUPPLIER' else 'customer')
            
            # Yeni cari oluştur
            new_contact = Contact(
                code=new_code,
                name=contact_name,
                contact_type=contact_type,
                tax_number=vkn,
                tax_office=contact_tax_office,
                address=contact_address,
                city=contact_city,
                district=contact_district,
                postal_code=contact_postal_code,
                phone=contact_phone,
                email=contact_email,
                is_active=True
            )
            
            db.add(new_contact)
            db.flush()  # ID alabilmek için
            
            einvoice.contact_id = new_contact.id
            einvoice.processing_status = 'MATCHED'
    
    db.add(einvoice)
    db.flush()  # ID'yi al
    
    # === VERGİ DETAYLARINI KAYDET ===
    from app.models.invoice_tax import InvoiceTax
    
    tax_details = invoice_data.get('tax_details', [])
    if tax_details:
        for tax_detail in tax_details:
            invoice_tax = InvoiceTax(
                einvoice_id=einvoice.id,
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
    db.refresh(einvoice)
    
    return einvoice
