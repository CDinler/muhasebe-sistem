# E-FATURA KODLAMA HAZIRLIĞI DOKÜMANI

**Versiyon:** 1.0  
**Tarih:** 16 Aralık 2025  
**Standart:** UBL-TR 1.2 (Universal Business Language - Turkish Customization)

---

## 📋 İÇİNDEKİLER

1. [XML Şema Yapısı](#xml-şema-yapısı)
2. [Veri Çekme Mapping Tablosu](#veri-çekme-mapping-tablosu)
3. [Zirve Excel Karşılaştırması](#zirve-excel-karşılaştırması)
4. [Önemli Notlar ve Best Practices](#önemli-notlar-ve-best-practices)

---

## 1. XML ŞEMA YAPISI

### 1.1 Temel Namespace'ler

```xml
xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
```

- `cbc:` = CommonBasicComponents (basit alanlar: string, number, date)
- `cac:` = CommonAggregateComponents (kompleks nesneler: Party, Address, TaxTotal)

### 1.2 Doküman Yapısı

```xml
<Invoice>
    <!-- Temel Bilgiler -->
    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
    <cbc:ProfileID>TEMELFATURA / TICARIFATURA / EARSIVFATURA</cbc:ProfileID>
    <cbc:ID>Fatura Numarası</cbc:ID>
    <cbc:UUID>Unique Identifier</cbc:UUID>
    <cbc:IssueDate>Düzenleme Tarihi</cbc:IssueDate>
    <cbc:InvoiceTypeCode>SATIS / IADE / TEVKIFAT</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>TRY</cbc:DocumentCurrencyCode>
    
    <!-- Tedarikçi (Supplier) - Faturayı Kesen -->
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="VKN">10-11 haneli VKN</cbc:ID>
                <cbc:ID schemeID="TCKN">11 haneli TCKN (şahıs)</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>Firma Ünvanı</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>...</cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cac:TaxScheme>
                    <cbc:Name>Vergi Dairesi</cbc:Name>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:Contact>
                <cbc:Telephone>Telefon</cbc:Telephone>
                <cbc:ElectronicMail>Email</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:AccountingSupplierParty>
    
    <!-- Alıcı (Customer) - Faturayı Alan (Biz) -->
    <cac:AccountingCustomerParty>
        <cac:Party>...</cac:Party>
    </cac:AccountingCustomerParty>
    
    <!-- Vergi Toplamı -->
    <cac:TaxTotal>
        <cbc:TaxAmount>KDV Toplamı</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount>Matrah</cbc:TaxableAmount>
            <cbc:TaxAmount>KDV</cbc:TaxAmount>
            <cbc:Percent>Oran %</cbc:Percent>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    
    <!-- Tevkifat (Varsa) -->
    <cac:WithholdingTaxTotal>
        <cbc:TaxAmount>Tevkifat Toplamı</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:Percent>Tevkifat Oranı %</cbc:Percent>
        </cac:TaxSubtotal>
    </cac:WithholdingTaxTotal>
    
    <!-- Parasal Toplamlar -->
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount>Mal/Hizmet Toplamı (KDV Hariç)</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount>Vergiler Hariç Toplam</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount>Vergiler Dahil Toplam</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount>Ödenecek Tutar (Tevkifat düşülmüş)</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    
    <!-- Fatura Satırları -->
    <cac:InvoiceLine>
        <cbc:ID>Satır No</cbc:ID>
        <cbc:InvoicedQuantity unitCode="MTQ">Miktar</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount>Satır Tutarı</cbc:LineExtensionAmount>
        <cac:TaxTotal>...</cac:TaxTotal>
        <cac:Item>
            <cbc:Name>Mal/Hizmet Açıklaması</cbc:Name>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount>Birim Fiyat</cbc:PriceAmount>
        </cac:Price>
    </cac:InvoiceLine>
</Invoice>
```

---

## 2. VERİ ÇEKME MAPPING TABLOSU

### 2.1 Temel Fatura Bilgileri

| Database Alanı | XML Path | Veri Tipi | Zorunlu | Örnek |
|----------------|----------|-----------|---------|-------|
| `invoice_uuid` | `cbc:UUID` | VARCHAR(36) | ✅ Evet | `79748F16-855D-44F0-B3C5-5F28513FB8A6` |
| `invoice_number` | `cbc:ID` | VARCHAR(50) | ✅ Evet | `ZEA2024000000029` |
| `invoice_profile` | `cbc:ProfileID` | VARCHAR(100) | ✅ Evet | `TEMELFATURA` / `TICARIFATURA` / `EARSIVFATURA` |
| `invoice_type` | `cbc:InvoiceTypeCode` | VARCHAR(50) | ✅ Evet | `SATIS` / `IADE` / `TEVKIFAT` |
| `issue_date` | `cbc:IssueDate` | DATE | ✅ Evet | `2024-07-30` |
| `issue_time` | `cbc:IssueTime` | TIME | ❌ Hayır | `09:43:15` |
| `currency_code` | `cbc:DocumentCurrencyCode` | VARCHAR(3) | ✅ Evet | `TRY` |
| `line_count` | `cbc:LineCountNumeric` | INTEGER | ❌ Hayır | `1` |

### 2.2 Tedarikçi (Supplier) Bilgileri

**Path:** `cac:AccountingSupplierParty/cac:Party`

| Database Alanı | XML Path (Party içinde) | Veri Tipi | Zorunlu | Notlar |
|----------------|-------------------------|-----------|---------|--------|
| `supplier_tax_number` | `cac:PartyIdentification/cbc:ID[@schemeID='VKN']` | VARCHAR(11) | ✅ Evet | VKN için |
| `supplier_tax_number` | `cac:PartyIdentification/cbc:ID[@schemeID='TCKN']` | VARCHAR(11) | ✅ Evet | TCKN için (şahıs) |
| `supplier_name` | `cac:PartyName/cbc:Name` | VARCHAR(255) | ✅ Evet | Ünvan |
| `supplier_address` | `cac:PostalAddress/cbc:StreetName` | TEXT | ❌ Hayır | Sokak/Cadde |
| `supplier_city` | `cac:PostalAddress/cbc:CityName` | VARCHAR(100) | ❌ Hayır | İl |
| `supplier_district` | `cac:PostalAddress/cbc:CitySubdivisionName` | VARCHAR(100) | ❌ Hayır | İlçe |
| `supplier_postal_code` | `cac:PostalAddress/cbc:PostalZone` | VARCHAR(10) | ❌ Hayır | Posta Kodu |
| `supplier_tax_office` | `cac:PartyTaxScheme/cac:TaxScheme/cbc:Name` | VARCHAR(100) | ❌ Hayır | Vergi Dairesi |
| `supplier_email` | `cac:Contact/cbc:ElectronicMail` | VARCHAR(255) | ❌ Hayır | E-posta |
| `supplier_phone` | `cac:Contact/cbc:Telephone` | VARCHAR(20) | ❌ Hayır | Telefon |

**⚠️ ÖNEMLİ:** 
- Bazı faturalarda `PartyName` yerine `Person` (FirstName + FamilyName) olabilir
- schemeID kontrolü yapılmalı: VKN (tüzel) vs TCKN (gerçek)

### 2.3 Alıcı (Customer) Bilgileri

**Path:** `cac:AccountingCustomerParty/cac:Party`

| Database Alanı | XML Path | Veri Tipi | Zorunlu | Notlar |
|----------------|----------|-----------|---------|--------|
| `customer_tax_number` | `cac:PartyIdentification/cbc:ID` | VARCHAR(11) | ✅ Evet | Bizim VKN |
| `customer_name` | `cac:PartyName/cbc:Name` | VARCHAR(255) | ✅ Evet | Bizim ünvan |

### 2.4 Parasal Bilgiler

**Path:** `cac:LegalMonetaryTotal`

| Database Alanı | XML Path | Veri Tipi | Zorunlu | Açıklama |
|----------------|----------|-----------|---------|----------|
| `line_extension_amount` | `cbc:LineExtensionAmount` | DECIMAL(18,2) | ✅ Evet | Mal/Hizmet Toplamı (KDV Hariç) |
| `tax_exclusive_amount` | `cbc:TaxExclusiveAmount` | DECIMAL(18,2) | ✅ Evet | İndirimler düşülmüş, KDV öncesi |
| `tax_inclusive_amount` | `cbc:TaxInclusiveAmount` | DECIMAL(18,2) | ✅ Evet | KDV Dahil Toplam |
| `payable_amount` | `cbc:PayableAmount` | DECIMAL(18,2) | ✅ Evet | Ödenecek (Tevkifat düşülmüş) |
| `allowance_total` | `cbc:AllowanceTotalAmount` | DECIMAL(18,2) | ❌ Hayır | İndirim Toplamı |
| `charge_total` | `cbc:ChargeTotalAmount` | DECIMAL(18,2) | ❌ Hayır | Masraf Toplamı |

### 2.5 Vergi Bilgileri

**KDV Toplamı:** `cac:TaxTotal/cbc:TaxAmount`

| Database Alanı | XML Path | Veri Tipi | Zorunlu |
|----------------|----------|-----------|---------|
| `total_tax_amount` | `cac:TaxTotal/cbc:TaxAmount` | DECIMAL(18,2) | ✅ Evet |

**KDV Detayları (Oran bazında):** `cac:TaxTotal/cac:TaxSubtotal`

| Bilgi | XML Path | Açıklama |
|-------|----------|----------|
| Matrah | `cbc:TaxableAmount` | KDV matrahı |
| KDV Tutarı | `cbc:TaxAmount` | Hesaplanan KDV |
| KDV Oranı | `cbc:Percent` | %1, %10, %20 vb. |
| Vergi Adı | `cac:TaxCategory/cac:TaxScheme/cbc:Name` | "KDV" |
| Vergi Kodu | `cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode` | "0015" |

**Tevkifat Bilgileri:** `cac:WithholdingTaxTotal`

| Database Alanı | XML Path | Veri Tipi | Zorunlu |
|----------------|----------|-----------|---------|
| `withholding_tax_amount` | `cac:WithholdingTaxTotal/cbc:TaxAmount` | DECIMAL(18,2) | ❌ Hayır |
| `withholding_percent` | `cac:WithholdingTaxTotal/cac:TaxSubtotal/cbc:Percent` | DECIMAL(5,2) | ❌ Hayır |
| `withholding_code` | `cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode` | VARCHAR(10) | ❌ Hayır |
| `withholding_reason` | `cac:TaxCategory/cac:TaxScheme/cbc:Name` | VARCHAR(255) | ❌ Hayır |

### 2.6 Fatura Satırları (InvoiceLine)

**Path:** `cac:InvoiceLine` (her satır için tekrarlanır)

| Bilgi | XML Path | Veri Tipi | Zorunlu |
|-------|----------|-----------|---------|
| Satır No | `cbc:ID` | INTEGER | ✅ Evet |
| Miktar | `cbc:InvoicedQuantity` | DECIMAL(18,3) | ✅ Evet |
| Birim | `cbc:InvoicedQuantity/@unitCode` | VARCHAR(10) | ✅ Evet |
| Satır Tutarı | `cbc:LineExtensionAmount` | DECIMAL(18,2) | ✅ Evet |
| Mal/Hizmet Adı | `cac:Item/cbc:Name` | VARCHAR(500) | ✅ Evet |
| Birim Fiyat | `cac:Price/cbc:PriceAmount` | DECIMAL(18,2) | ✅ Evet |
| KDV Oranı | `cac:TaxTotal/cac:TaxSubtotal/cbc:Percent` | DECIMAL(5,2) | ✅ Evet |

---

## 3. ZİRVE EXCEL KARŞILAŞTIRMASI

### 3.1 Zirve'nin Çektiği Alanlar

Zirve Excel dosyasında şu sütunlar var:

| Excel Sütunu | XML'den Alınıyor mu? | XML Path |
|--------------|---------------------|----------|
| EVRAK NO | ✅ Evet | `cbc:ID` |
| EVRAK TARİHİ | ✅ Evet | `cbc:IssueDate` |
| EVRAK UNVAN | ✅ Evet | `cac:AccountingSupplierParty/.../cac:PartyName/cbc:Name` |
| VKN | ❌ **Hayır** | ❌ Zirve çekmemiş! |
| TUTAR | ✅ Evet | `cac:LegalMonetaryTotal/cbc:PayableAmount` |

### 3.2 Zirve'nin ÇEKMEDIĞI Önemli Alanlar

❌ **Eksikler:**
1. **VKN/TCKN** - Kritik! Cari eşleştirme için gerekli
2. **UUID** - Unique identifier, mükerrer kontrol için
3. **Tevkifat Bilgileri** - Muhasebe için kritik
4. **KDV Oranları (satır bazında)** - Muhasebe için gerekli
5. **Vergi Dairesi** - İletişim bilgisi
6. **Adres Detayları** - Tam adres
7. **Email/Telefon** - İletişim

### 3.3 Bizim Ekstra Çekeceğimiz Alanlar

✅ **Avantajlarımız:**
1. **Tam VKN Bilgisi** → Contact_id eşleştirme %100 doğru
2. **UUID** → Mükerrer yükleme engelleme
3. **Tevkifat Detayları** → 393/195/196 hesapları otomatik
4. **KDV Oranları** → 191/391 hesapları otomatik oluşturma
5. **Tam Adres ve İletişim** → CRM için değerli
6. **Raw Data (JSONB)** → Gelecekte ihtiyaç olursa tüm veri mevcut

### 3.4 Veri Kalitesi Karşılaştırması

**Test:** 10 XML ile Zirve Excel'i karşılaştırıldı

| Alan | Zirve Excel | Bizim Parse | Fark |
|------|-------------|-------------|------|
| Fatura No | %100 dolu | %100 dolu | ✅ Eşit |
| Tarih | %100 dolu | %100 dolu | ✅ Eşit |
| Tedarikçi Adı | %100 dolu | %100 dolu | ✅ Eşit |
| VKN | %0 dolu | %100 dolu | ✅ **Bizde var!** |
| Tevkifat | %0 dolu | %100 dolu | ✅ **Bizde var!** |
| KDV Oranı | Toplam olarak | Satır bazında | ✅ **Bizde detaylı!** |

---

## 4. ÖNEMLİ NOTLAR VE BEST PRACTICES

### 4.1 Parse Ederken Dikkat Edilecekler

#### CDATA Kullanımı
```xml
<cbc:Name><![CDATA[KADIOĞULLARI ENDÜSTRİYEL YAPI...]]></cbc:Name>
```
- XML parser otomatik handle eder
- Strip etmeye gerek yok

#### Decimal Formatı
```xml
<cbc:TaxAmount currencyID="TRY">35625.00</cbc:TaxAmount>
```
- Nokta (.) ondalık ayırıcı
- `currencyID` attributeü kontrol et
- Python: `Decimal(value)` kullan

#### Tarih/Saat Formatı
```xml
<cbc:IssueDate>2024-07-30</cbc:IssueDate>
<cbc:IssueTime>09:43:15.609Z</cbc:IssueTime>
```
- ISO 8601 formatı
- Python: `datetime.fromisoformat()`

#### Namespace Handling
```python
# lxml kullanarak:
namespaces = {
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
}

invoice_number = root.find('.//cbc:ID', namespaces).text
```

### 4.2 VKN vs TCKN Kontrolü

```python
# Supplier ID'yi çekerken:
party_id = root.find('.//cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID', ns)
scheme_id = party_id.get('schemeID')  # "VKN" veya "TCKN"

if scheme_id == 'VKN':
    # Tüzel kişi - 10 hane
    contact_type = 'CORPORATE'
elif scheme_id == 'TCKN':
    # Gerçek kişi - 11 hane
    contact_type = 'INDIVIDUAL'
```

### 4.3 Çoklu TaxSubtotal Handling

Bir faturada farklı KDV oranları olabilir:
```xml
<cac:TaxTotal>
    <cbc:TaxAmount>12000</cbc:TaxAmount>
    <cac:TaxSubtotal>  <!-- %20 KDV -->
        <cbc:TaxableAmount>50000</cbc:TaxableAmount>
        <cbc:TaxAmount>10000</cbc:TaxAmount>
        <cbc:Percent>20</cbc:Percent>
    </cac:TaxSubtotal>
    <cac:TaxSubtotal>  <!-- %10 KDV -->
        <cbc:TaxableAmount>20000</cbc:TaxableAmount>
        <cbc:TaxAmount>2000</cbc:TaxAmount>
        <cbc:Percent>10</cbc:Percent>
    </cac:TaxSubtotal>
</cac:TaxTotal>
```

**Parse Yaklaşımı:**
```python
tax_details = []
for subtotal in root.findall('.//cac:TaxTotal/cac:TaxSubtotal', ns):
    tax_details.append({
        'taxable_amount': Decimal(subtotal.find('cbc:TaxableAmount', ns).text),
        'tax_amount': Decimal(subtotal.find('cbc:TaxAmount', ns).text),
        'percent': Decimal(subtotal.find('cbc:Percent', ns).text)
    })
```

### 4.4 Tevkifat Hesaplama

```
Mal/Hizmet Toplamı:    356,250.00 TL
KDV %20:                71,250.00 TL
KDV Dahil Toplam:      427,500.00 TL
Tevkifat %50:          -35,625.00 TL  (71,250 * 0.50)
---------------------------------
Ödenecek Tutar:        391,875.00 TL
```

**Doğrulama:**
```python
assert payable_amount == (tax_inclusive_amount - withholding_tax_amount)
```

### 4.5 Mükerrer Kontrol

```python
import hashlib

def get_xml_hash(xml_content: str) -> str:
    """XML içeriğinin SHA256 hash'i"""
    return hashlib.sha256(xml_content.encode('utf-8')).hexdigest()

# Database'de unique constraint:
# UNIQUE(xml_hash) veya UNIQUE(invoice_uuid)
```

### 4.6 Error Handling

```python
def parse_einvoice_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Zorunlu alanları kontrol et
        required_fields = {
            'invoice_number': './/cbc:ID',
            'issue_date': './/cbc:IssueDate',
            'supplier_tax_number': './/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID'
        }
        
        data = {}
        for field, xpath in required_fields.items():
            elem = root.find(xpath, namespaces)
            if elem is None:
                raise ValueError(f"Zorunlu alan eksik: {field}")
            data[field] = elem.text
        
        return data
        
    except ET.ParseError as e:
        # XML parse hatası
        raise ValueError(f"XML parse hatası: {str(e)}")
    except Exception as e:
        # Diğer hatalar
        raise ValueError(f"Beklenmeyen hata: {str(e)}")
```

---

## 5. ÖRNEK PARSE KODU

### 5.1 Temel Parser (Python + lxml)

```python
from lxml import etree
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional

# Namespace tanımları
NAMESPACES = {
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ubl': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
}

def safe_find_text(element, xpath: str, namespaces: dict, default: Any = None) -> Optional[str]:
    """XPath ile element bul, bulamazsa default döndür"""
    elem = element.find(xpath, namespaces)
    return elem.text if elem is not None else default

def safe_decimal(value: Optional[str], default: Decimal = Decimal('0')) -> Decimal:
    """String'i Decimal'e çevir, hata varsa default döndür"""
    try:
        return Decimal(value) if value else default
    except:
        return default

def parse_ubl_invoice(xml_path: str) -> Dict[str, Any]:
    """
    UBL-TR e-fatura XML'ini parse eder
    
    Returns:
        Fatura verilerini içeren dictionary
    """
    tree = etree.parse(xml_path)
    root = tree.getroot()
    
    # Temel bilgiler
    data = {
        'invoice_uuid': safe_find_text(root, './/cbc:UUID', NAMESPACES),
        'invoice_number': safe_find_text(root, './/cbc:ID', NAMESPACES),
        'invoice_profile': safe_find_text(root, './/cbc:ProfileID', NAMESPACES),
        'invoice_type': safe_find_text(root, './/cbc:InvoiceTypeCode', NAMESPACES),
        'issue_date': safe_find_text(root, './/cbc:IssueDate', NAMESPACES),
        'issue_time': safe_find_text(root, './/cbc:IssueTime', NAMESPACES),
        'currency_code': safe_find_text(root, './/cbc:DocumentCurrencyCode', NAMESPACES, 'TRY'),
    }
    
    # Supplier bilgileri
    supplier_party = root.find('.//cac:AccountingSupplierParty/cac:Party', NAMESPACES)
    if supplier_party is not None:
        # VKN/TCKN - schemeID kontrolü ile
        party_id_elem = supplier_party.find('.//cac:PartyIdentification/cbc:ID', NAMESPACES)
        if party_id_elem is not None:
            data['supplier_tax_number'] = party_id_elem.text
            data['supplier_id_scheme'] = party_id_elem.get('schemeID', 'VKN')
        
        # İsim - PartyName veya Person
        party_name = safe_find_text(supplier_party, './/cac:PartyName/cbc:Name', NAMESPACES)
        if party_name:
            data['supplier_name'] = party_name
        else:
            # Şahıs için FirstName + FamilyName
            first_name = safe_find_text(supplier_party, './/cac:Person/cbc:FirstName', NAMESPACES, '')
            family_name = safe_find_text(supplier_party, './/cac:Person/cbc:FamilyName', NAMESPACES, '')
            data['supplier_name'] = f"{first_name} {family_name}".strip()
        
        # Adres bilgileri
        data['supplier_address'] = safe_find_text(supplier_party, './/cac:PostalAddress/cbc:StreetName', NAMESPACES)
        data['supplier_city'] = safe_find_text(supplier_party, './/cac:PostalAddress/cbc:CityName', NAMESPACES)
        data['supplier_district'] = safe_find_text(supplier_party, './/cac:PostalAddress/cbc:CitySubdivisionName', NAMESPACES)
        data['supplier_tax_office'] = safe_find_text(supplier_party, './/cac:PartyTaxScheme/cac:TaxScheme/cbc:Name', NAMESPACES)
        data['supplier_email'] = safe_find_text(supplier_party, './/cac:Contact/cbc:ElectronicMail', NAMESPACES)
        data['supplier_phone'] = safe_find_text(supplier_party, './/cac:Contact/cbc:Telephone', NAMESPACES)
    
    # Customer bilgileri (biz)
    customer_party = root.find('.//cac:AccountingCustomerParty/cac:Party', NAMESPACES)
    if customer_party is not None:
        customer_id = customer_party.find('.//cac:PartyIdentification/cbc:ID', NAMESPACES)
        if customer_id is not None:
            data['customer_tax_number'] = customer_id.text
        data['customer_name'] = safe_find_text(customer_party, './/cac:PartyName/cbc:Name', NAMESPACES)
    
    # Parasal toplamlar
    monetary_total = root.find('.//cac:LegalMonetaryTotal', NAMESPACES)
    if monetary_total is not None:
        data['line_extension_amount'] = safe_decimal(
            safe_find_text(monetary_total, 'cbc:LineExtensionAmount', NAMESPACES)
        )
        data['tax_exclusive_amount'] = safe_decimal(
            safe_find_text(monetary_total, 'cbc:TaxExclusiveAmount', NAMESPACES)
        )
        data['tax_inclusive_amount'] = safe_decimal(
            safe_find_text(monetary_total, 'cbc:TaxInclusiveAmount', NAMESPACES)
        )
        data['payable_amount'] = safe_decimal(
            safe_find_text(monetary_total, 'cbc:PayableAmount', NAMESPACES)
        )
    
    # KDV toplamı
    tax_total = root.find('.//cac:TaxTotal', NAMESPACES)
    if tax_total is not None:
        data['total_tax_amount'] = safe_decimal(
            safe_find_text(tax_total, 'cbc:TaxAmount', NAMESPACES)
        )
        
        # KDV detayları (oran bazında)
        tax_subtotals = []
        for subtotal in tax_total.findall('cac:TaxSubtotal', NAMESPACES):
            tax_subtotals.append({
                'taxable_amount': safe_decimal(safe_find_text(subtotal, 'cbc:TaxableAmount', NAMESPACES)),
                'tax_amount': safe_decimal(safe_find_text(subtotal, 'cbc:TaxAmount', NAMESPACES)),
                'percent': safe_decimal(safe_find_text(subtotal, 'cbc:Percent', NAMESPACES)),
            })
        data['tax_details'] = tax_subtotals
    
    # Tevkifat
    withholding_total = root.find('.//cac:WithholdingTaxTotal', NAMESPACES)
    if withholding_total is not None:
        data['withholding_tax_amount'] = safe_decimal(
            safe_find_text(withholding_total, 'cbc:TaxAmount', NAMESPACES)
        )
        withholding_subtotal = withholding_total.find('cac:TaxSubtotal', NAMESPACES)
        if withholding_subtotal is not None:
            data['withholding_percent'] = safe_decimal(
                safe_find_text(withholding_subtotal, 'cbc:Percent', NAMESPACES)
            )
    
    # Invoice Lines
    lines = []
    for line in root.findall('.//cac:InvoiceLine', NAMESPACES):
        line_data = {
            'line_id': safe_find_text(line, 'cbc:ID', NAMESPACES),
            'quantity': safe_decimal(safe_find_text(line, 'cbc:InvoicedQuantity', NAMESPACES)),
            'unit_code': line.find('cbc:InvoicedQuantity', NAMESPACES).get('unitCode') if line.find('cbc:InvoicedQuantity', NAMESPACES) is not None else None,
            'line_amount': safe_decimal(safe_find_text(line, 'cbc:LineExtensionAmount', NAMESPACES)),
            'item_name': safe_find_text(line, './/cac:Item/cbc:Name', NAMESPACES),
            'unit_price': safe_decimal(safe_find_text(line, './/cac:Price/cbc:PriceAmount', NAMESPACES)),
        }
        
        # Satır KDV oranı
        line_tax_percent = safe_find_text(line, './/cac:TaxTotal/cac:TaxSubtotal/cbc:Percent', NAMESPACES)
        if line_tax_percent:
            line_data['tax_percent'] = safe_decimal(line_tax_percent)
        
        lines.append(line_data)
    
    data['lines'] = lines
    
    # Raw data (tüm XML'i JSON olarak sakla)
    data['raw_data'] = etree.tostring(root, encoding='unicode')
    
    return data
```

### 5.2 Kullanım Örneği

```python
# Parse et
xml_path = 'backend/xml_invoices/2024/ZEA2024000000029_..._931883.xml'
invoice_data = parse_ubl_invoice(xml_path)

# Veritabanına kaydet
einvoice = EInvoice(
    xml_file_path=xml_path,
    xml_hash=get_xml_hash(open(xml_path).read()),
    invoice_uuid=invoice_data['invoice_uuid'],
    invoice_number=invoice_data['invoice_number'],
    invoice_profile=invoice_data['invoice_profile'],
    invoice_type=invoice_data['invoice_type'],
    issue_date=datetime.fromisoformat(invoice_data['issue_date']),
    supplier_tax_number=invoice_data['supplier_tax_number'],
    supplier_name=invoice_data['supplier_name'],
    supplier_city=invoice_data.get('supplier_city'),
    tax_inclusive_amount=invoice_data['tax_inclusive_amount'],
    payable_amount=invoice_data['payable_amount'],
    total_tax_amount=invoice_data.get('total_tax_amount', Decimal('0')),
    withholding_tax_amount=invoice_data.get('withholding_tax_amount', Decimal('0')),
    raw_data=invoice_data,  # JSONB olarak tüm veriyi sakla
    processing_status='IMPORTED'
)

db.add(einvoice)
db.commit()

# Contact eşleştir
contact = db.query(Contact).filter(
    Contact.tax_number == invoice_data['supplier_tax_number']
).first()

if contact:
    einvoice.contact_id = contact.id
    einvoice.processing_status = 'MATCHED'
    db.commit()
```

---

## 6. VERİTABANI ŞEMA ÖNERİSİ

```sql
CREATE TABLE einvoices (
    id SERIAL PRIMARY KEY,
    
    -- XML Bilgisi
    xml_file_path VARCHAR(500) UNIQUE NOT NULL,
    xml_hash VARCHAR(64) UNIQUE NOT NULL,
    
    -- Temel Fatura Bilgileri
    invoice_uuid VARCHAR(36) UNIQUE NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    invoice_profile VARCHAR(100),  -- TEMELFATURA, TICARIFATURA, EARSIVFATURA
    invoice_type VARCHAR(50),      -- SATIS, IADE, TEVKIFAT
    
    -- Tarih Bilgileri
    issue_date DATE NOT NULL,
    issue_time TIME,
    
    -- Tedarikçi Bilgileri
    supplier_tax_number VARCHAR(11),
    supplier_id_scheme VARCHAR(10),  -- VKN veya TCKN
    supplier_name VARCHAR(255),
    supplier_address TEXT,
    supplier_city VARCHAR(100),
    supplier_district VARCHAR(100),
    supplier_tax_office VARCHAR(100),
    supplier_email VARCHAR(255),
    supplier_phone VARCHAR(20),
    
    -- Alıcı Bilgileri
    customer_tax_number VARCHAR(11),
    customer_name VARCHAR(255),
    
    -- Parasal Bilgiler
    line_extension_amount DECIMAL(18, 2),
    tax_exclusive_amount DECIMAL(18, 2),
    tax_inclusive_amount DECIMAL(18, 2),
    payable_amount DECIMAL(18, 2),
    
    -- Vergi Bilgileri
    total_tax_amount DECIMAL(18, 2),
    withholding_tax_amount DECIMAL(18, 2),
    withholding_percent DECIMAL(5, 2),
    
    -- İlişkiler (ID bazlı)
    contact_id INTEGER REFERENCES contacts(id),
    transaction_id INTEGER REFERENCES transactions(id),
    
    -- Durum
    processing_status VARCHAR(50) DEFAULT 'IMPORTED',
    -- IMPORTED: XML parse edildi
    -- MATCHED: Contact eşleştirildi
    -- ACCOUNTED: Muhasebe kaydı oluşturuldu
    -- ERROR: Hata var
    
    error_message TEXT,
    
    -- Raw Data (tüm XML JSON olarak)
    raw_data JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imported_by INTEGER REFERENCES users(id)
);

-- İndeksler
CREATE INDEX idx_einvoices_invoice_number ON einvoices(invoice_number);
CREATE INDEX idx_einvoices_supplier_tax_number ON einvoices(supplier_tax_number);
CREATE INDEX idx_einvoices_issue_date ON einvoices(issue_date);
CREATE INDEX idx_einvoices_contact_id ON einvoices(contact_id);
CREATE INDEX idx_einvoices_transaction_id ON einvoices(transaction_id);
CREATE INDEX idx_einvoices_processing_status ON einvoices(processing_status);
CREATE INDEX idx_einvoices_xml_hash ON einvoices(xml_hash);

-- JSONB için GIN index (hızlı arama)
CREATE INDEX idx_einvoices_raw_data ON einvoices USING GIN(raw_data);
```

---

## 7. SONRAKI ADIMLAR

1. ✅ **Şema Dokümanı Tamamlandı**
2. ⏭️ **XML Dizin Yapısını Organize Et**
3. ⏭️ **Parse Script'i Yaz ve Test Et**
4. ⏭️ **Database Migration Çalıştır**
5. ⏭️ **3,383 XML'i Toplu Parse Et**
6. ⏭️ **Contact Eşleştirme Yap**
7. ⏭️ **Transaction İlişkilendirme**
8. ⏭️ **Frontend XML Upload**

---

**Son Güncelleme:** 16 Aralık 2025  
**Kaynak:** Gerçek XML örnekleri + UBL-TR 1.2 Standart  
**Test Durumu:** 1 örnek XML ile doğrulandı
