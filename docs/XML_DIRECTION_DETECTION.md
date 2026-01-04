# XML E-Fatura Direction ve Category Tespiti

## 📋 XML'de Bilgi Alanları

### 1️⃣ E-Fatura vs E-Arşiv Tespiti

**XML Alanı:** `<cbc:ProfileID>`

```xml
<!-- E-FATURA ÖRNEKLERİ -->
<cbc:ProfileID>TICARIFATURA</cbc:ProfileID>
<cbc:ProfileID>TEMELFATURA</cbc:ProfileID>
<cbc:ProfileID>IHRACAT</cbc:ProfileID>

<!-- E-ARŞİV ÖRNEĞİ -->
<cbc:ProfileID>EARSIVFATURA</cbc:ProfileID>
```

**Tespit Kodu:**
```python
profile = invoice_data.get('invoice_scenario', '').upper()
is_archive = 'EARSIV' in profile or 'ARSIV' in profile

if is_archive:
    category = f'{direction}-archive'  # incoming-archive veya outgoing-archive
else:
    category = direction  # incoming veya outgoing
```

---

### 2️⃣ Gelen vs Giden Tespiti

**⚠️ XML'de direkt "gelen/giden" alanı YOK!**

XML'de sadece **SATICI** (Supplier) ve **ALICI** (Customer) bilgileri var:

```xml
<!-- SATICI (Faturayı Kesen) -->
<cac:AccountingSupplierParty>
  <cac:Party>
    <cac:PartyTaxScheme>
      <cac:TaxScheme>
        <cbc:TaxTypeCode>1234567890</cbc:TaxTypeCode> <!-- Satıcı VKN -->
      </cac:TaxScheme>
    </cac:PartyTaxScheme>
    <cac:PartyName>
      <cbc:Name>ABC Şirketi</cbc:Name>
    </cac:PartyName>
  </cac:Party>
</cac:AccountingSupplierParty>

<!-- ALICI (Faturayı Alan) -->
<cac:AccountingCustomerParty>
  <cac:Party>
    <cac:PartyTaxScheme>
      <cac:TaxScheme>
        <cbc:TaxTypeCode>0987654321</cbc:TaxTypeCode> <!-- Alıcı VKN -->
      </cac:TaxScheme>
    </cac:PartyTaxScheme>
    <cac:PartyName>
      <cbc:Name>XYZ A.Ş.</cbc:Name>
    </cac:PartyName>
  </cac:Party>
</cac:AccountingCustomerParty>
```

**Tespit Mantığı:**

1. **Bizim VKN'mizi** `.env` dosyasından oku (`COMPANY_TAX_NUMBER`)
2. **Customer VKN** ile karşılaştır:
   - Eşleşiyorsa → **GELEN** (biz alıcıyız, faturayı bize kestiler)
3. **Supplier VKN** ile karşılaştır:
   - Eşleşiyorsa → **GİDEN** (biz satıcıyız, müşteriye fatura kestik)

**Tespit Kodu:**
```python
# .env'den şirket VKN'sini oku
company_vkn = settings.COMPANY_TAX_NUMBER  # Örn: "1234567890"

# XML'den VKN'leri oku
customer_vkn = invoice_data.get('customer_tax_number')  # Alıcı VKN
supplier_vkn = invoice_data.get('supplier_tax_number')  # Satıcı VKN

# Karşılaştır
if customer_vkn == company_vkn:
    direction = 'incoming'  # GELEN
elif supplier_vkn == company_vkn:
    direction = 'outgoing'  # GİDEN
else:
    direction = 'incoming'  # Fallback (varsayılan)
```

---

## 📊 Kategori Tablosu

| ProfileID | Bizim Rolümüz | Direction | Category |
|-----------|---------------|-----------|----------|
| TICARIFATURA | Alıcı (Customer) | incoming | `incoming` |
| TICARIFATURA | Satıcı (Supplier) | outgoing | `outgoing` |
| EARSIVFATURA | Alıcı | incoming | `incoming-archive` |
| EARSIVFATURA | Satıcı | outgoing | `outgoing-archive` |

---

## 📁 Dizin Organizasyonu

```
data/einvoices/
├── incoming/              # Gelen e-faturalar
│   ├── 2024/
│   │   ├── 01-ocak/
│   │   ├── 02-subat/
│   │   └── ...
│   └── 2025/
│       └── 03-mart/
│           └── ABC2025000123.xml
│
├── outgoing/              # Giden e-faturalar
│   └── 2025/
│       └── 03-mart/
│           └── XYZ2025000456.xml
│
├── incoming-archive/      # Gelen e-arşiv faturalar
│   └── ...
│
└── outgoing-archive/      # Giden e-arşiv faturalar
    └── ...
```

---

## 🔄 Tam İşlem Akışı

### Adım 1: XML Upload
Kullanıcı XML/ZIP dosyasını yükler, direction seçer (incoming/outgoing)

### Adım 2: Parse
XML parse edilir, VKN'ler ve ProfileID çıkarılır

### Adım 3: Otomatik Direction Tespiti
```python
# 1. Bizim VKN'mizi al
company_vkn = "1234567890"  # .env'den

# 2. XML'den VKN'leri al
customer_vkn = "0987654321"  # Alıcı
supplier_vkn = "1234567890"  # Satıcı

# 3. Karşılaştır
if customer_vkn == company_vkn:
    direction = 'incoming'  # ✅ BİZ ALICIYIZ → GELEN
elif supplier_vkn == company_vkn:
    direction = 'outgoing'  # BİZ SATICIYIZ → GİDEN
```

### Adım 4: Category Tespiti
```python
profile = "TICARIFATURA"  # XML'den

if 'EARSIV' in profile:
    category = f'{direction}-archive'  # incoming-archive
else:
    category = direction  # incoming
```

### Adım 5: Dizin Oluştur ve Kaydet
```python
# Dizin: data/einvoices/incoming/2025/03-mart/
base_dir = Path('data/einvoices') / category / '2025' / '03-mart'
base_dir.mkdir(parents=True, exist_ok=True)

# XML'i kaydet
xml_path = base_dir / 'ABC2025000123.xml'
with open(xml_path, 'wb') as f:
    f.write(xml_content)
```

### Adım 6: Database'e Kaydet
```python
einvoice = EInvoice(
    invoice_uuid='ABC-123-UUID',
    invoice_category='incoming',  # incoming, outgoing, incoming-archive, outgoing-archive
    xml_file_path='data/einvoices/incoming/2025/03-mart/ABC2025000123.xml',
    xml_hash='sha256...',
    supplier_tax_number='1234567890',
    customer_tax_number='0987654321',
    ...
)
```

---

## ⚙️ Yapılandırma

### .env Dosyası
```bash
# Şirketinizin VKN'sini buraya yazın
COMPANY_TAX_NUMBER=1234567890
```

**ÖNEMLİ:** Bu VKN'yi doğru yazmazsanız, direction otomatik tespit edilemez!

---

## 🧪 Test Senaryoları

### Test 1: Gelen E-Fatura
**XML İçeriği:**
- `<cbc:ProfileID>TICARIFATURA</cbc:ProfileID>`
- `<AccountingCustomerParty>` → VKN: 1234567890 (bizim VKN)
- `<AccountingSupplierParty>` → VKN: 9999999999

**Beklenen Sonuç:**
- Direction: `incoming` (bizim VKN customer'da)
- Category: `incoming` (ProfileID'de EARSIV yok)
- Dizin: `data/einvoices/incoming/2025/03-mart/`

### Test 2: Giden E-Arşiv
**XML İçeriği:**
- `<cbc:ProfileID>EARSIVFATURA</cbc:ProfileID>`
- `<AccountingSupplierParty>` → VKN: 1234567890 (bizim VKN)
- `<AccountingCustomerParty>` → VKN: 8888888888

**Beklenen Sonuç:**
- Direction: `outgoing` (bizim VKN supplier'da)
- Category: `outgoing-archive` (ProfileID'de EARSIV var)
- Dizin: `data/einvoices/outgoing-archive/2025/03-mart/`

---

## ❓ Sık Sorulan Sorular

**S: XML'de direction alanı neden yok?**
A: UBL-TR standardı "gelen/giden" kavramını kullanmaz. Sadece "satıcı/alıcı" bilgileri var. Direction, VKN'ye bakarak belirlenir.

**S: Otomatik tespit başarısız olursa ne olur?**
A: Kullanıcının seçtiği direction kullanılır (fallback). Hata mesajı döner.

**S: Birden fazla şirket VKN'si olabilir mi?**
A: Şu an tek VKN destekleniyor. Çoklu şirket için config genişletilebilir.

**S: ZIP dosyasında farklı direction'lar olabilir mi?**
A: Evet! Her XML kendi VKN'sine göre otomatik kategorize edilir.

---

## 📈 İstatistikler

Upload sonucunda dönen response:

```json
{
  "message": "25 e-fatura yüklendi",
  "imported_count": 25,
  "categorized": {
    "incoming": 15,          // Gelen e-fatura
    "outgoing": 5,           // Giden e-fatura
    "incoming-archive": 3,   // Gelen e-arşiv
    "outgoing-archive": 2    // Giden e-arşiv
  },
  "direction_detection": {
    "auto_detected": 23,     // Otomatik tespit edildi
    "fallback_used": 2       // Fallback kullanıldı
  }
}
```
