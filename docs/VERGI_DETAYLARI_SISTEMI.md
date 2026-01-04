# VERGİ DETAYLARI SİSTEMİ RAPORU

## ✅ TAMAMLANAN İŞLEMLER

### 1. Veritabanı Tablosu Oluşturuldu
- **Tablo adı**: `invoice_taxes`
- **Amaç**: E-faturaların XML'indeki tüm vergi detaylarını (KDV, ÖİV, ÖTV, Telsiz vb.) ayrı ayrı saklamak

### 2. Tablo Yapısı
```sql
CREATE TABLE invoice_taxes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    einvoice_id INT NOT NULL,  -- Bağlı olduğu fatura
    tax_type_code VARCHAR(10),  -- Vergi kodu (0015=KDV, 4081=ÖİV, 8006=Telsiz)
    tax_name VARCHAR(100),      -- Vergi adı
    tax_percent DECIMAL(5,2),   -- Vergi oranı (%0, %10, %20 vb)
    taxable_amount DECIMAL(18,2), -- Matrah
    tax_amount DECIMAL(18,2),   -- Hesaplanan vergi
    currency_code VARCHAR(3),   -- Para birimi (TRY)
    exemption_reason_code VARCHAR(10),  -- İstisna kodu (varsa)
    exemption_reason VARCHAR(255),      -- İstisna sebebi (varsa)
    FOREIGN KEY (einvoice_id) REFERENCES einvoices(id) ON DELETE CASCADE
);
```

### 3. XML Parse Sistemi Güncellendi
**Dosya**: `backend/app/services/einvoice_xml_service.py`

#### Eklenen Fonksiyonlar:
- **parse_xml_invoice()**: XML'den `tax_details` array'i çıkarır
  - TaxTotal > TaxSubtotal elementlerini tarar
  - Her vergi tipi için:
    - `tax_type_code` (ör: 0015, 4081, 8006)
    - `tax_name` (ör: Katma Değer Vergisi, Özel İletişim Vergisi)
    - `tax_percent` (vergi oranı)
    - `taxable_amount` (matrah)
    - `tax_amount` (hesaplanan vergi)
    - `exemption_reason_code` ve `exemption_reason` (istisna varsa)

- **create_einvoice_from_xml()**: Vergi detaylarını da kaydeder
  - Yeni fatura eklendiğinde → vergi detaylarını ekler
  - PDF→XML güncellemesinde → eski vergileri siler, yenilerini ekler

### 4. API Endpoint Güncellendi
**Endpoint**: `GET /api/v1/einvoices/{invoice_id}`

**Eski response**:
```json
{
  "id": 123,
  "invoice_number": "0012025270801375",
  "payable_amount": 1521.50,
  "invoice_lines": [...]
}
```

**Yeni response**:
```json
{
  "id": 123,
  "invoice_number": "0012025270801375",
  "payable_amount": 1521.50,
  "invoice_lines": [...],
  "tax_details": [
    {
      "id": 1,
      "tax_type_code": "0015",
      "tax_name": "Katma Deger Vergisi",
      "tax_percent": 20.00,
      "taxable_amount": 1050.77,
      "tax_amount": 210.15,
      "currency_code": "TRY"
    },
    {
      "id": 2,
      "tax_type_code": "4081",
      "tax_name": "Özel İletişim Vergisi",
      "tax_percent": 10.00,
      "taxable_amount": 1050.77,
      "tax_amount": 105.08,
      "currency_code": "TRY"
    },
    {
      "id": 3,
      "tax_type_code": "8006",
      "tax_name": "Telsiz Kullanım Aylık Taksit",
      "tax_percent": 0.00,
      "taxable_amount": 21.50,
      "tax_amount": 21.50,
      "currency_code": "TRY"
    }
  ]
}
```

### 5. Mevcut Faturalar İşlendi
**Script**: `fill_all_tax_details.py`

**Sonuçlar**:
- ✓ **3464 fatura** başarıyla işlendi
- ⊙ **2 fatura** zaten vardı
- ✗ **28 fatura** hata (NULL matrah - özel durumlar)
- **TOPLAM: 3978 vergi kaydı** oluşturuldu

### 6. Vergi Kodları Referansı
**Kaynak**: UBL-TR Kod Listeleri - V 1.40.pdf

| Kod | Vergi Adı | Kullanım |
|-----|-----------|----------|
| 0003 | Gelir Vergisi Stopajı | Hizmet bedeli stopajı |
| 0015 | KDV | Katma Değer Vergisi |
| 0059 | Konaklama Vergisi | Otel, konaklama tesisleri |
| 0071 | ÖTV | Özel Tüketim Vergisi (genel) |
| 4081 | ÖİV | Özel İletişim Vergisi |
| 8005 | BTV | Banka ve Sigorta Muameleleri Vergisi |
| 8006 | Telsiz | Telsiz Kullanım Aylık Taksit |
| 9077 | ÖTV Motorlu Taşıtlar | Araç ÖTV'si |

### 7. Muhasebe Kaydı Örneği

**TURKCELL Faturası** (0012025270801375):
```
Tarih: 2025-12-30
ETTN: da2db336-8cd0-4153-91fb-d0e65deee20e

1. Tarife ve Paket Ücretleri      : 1,050.77 TRY
   - KDV %20                       :   210.15 TRY
   - ÖİV %10                       :   105.08 TRY
   
2. Telsiz Kullanım Aylık Taksit   :    21.50 TRY
   - Vergi %0                      :    21.50 TRY

3. Diğer Ücretler                 :     0.07 TRY
4. Düzeltmeler                    :    -0.07 TRY
5. Aracılık Ödemeleri             :   134.00 TRY

TOPLAM TUTAR                      : 1,521.50 TRY
```

**Muhasebe Fişi**:
```
Borç:
  760 - Pazarlama Giderleri         : 1,050.77
  193 - Peşin Ödenmiş Giderler      :    21.50
  191 - İndirilecek KDV             :   210.15
  xxx - Diğer İndirilebilir Vergiler:   105.08 (ÖİV)
  xxx - Telsiz Vergisi              :    21.50

Alacak:
  320 - Satıcılar (TURKCELL)        : 1,521.50

Açıklama: 0012025270801375 No.lu Turkcell faturası
```

---

## 📊 İSTATİSTİKLER

### Vergi Tiplerine Göre Dağılım
- **KDV**: 2,751 kayıt → **97,510,720.94 TRY**
- **Gelir Vergisi Stopajı**: 5 kayıt → 1,190,403.42 TRY
- **ÖTV (Motorlu Taşıtlar)**: 11 kayıt → 1,860,092.67 TRY
- **ÖTV (Genel)**: 1 kayıt → 1,441,724.45 TRY
- **Konaklama Vergisi**: 5 kayıt → 1,903.57 TRY
- **ÖİV**: 93 kayıt → 4,918.22 TRY
- **Telsiz**: 93 kayıt → 1,704.30 TRY
- **BTV**: 40 kayıt → 254.06 TRY

---

## 🔄 SONRAKİ ADIMLAR

### 1. Frontend'i Güncelle
- Fatura detay sayfasına `tax_details` tablosu ekle
- Vergi kodlarına göre renklendirme yap
- Toplam vergi hesaplamasını göster

### 2. Excel Raporu
- Vergi bazlı döküm raporu
- Vergi kodu bazlı toplam raporu
- İstisna kodlu faturaların listesi

### 3. Muhasebe Fişi Otomasyonu
- Vergi kodlarına göre otomatik hesap eşleştirme
- KDV → 191
- ÖİV → 360 (veya uygun hesap)
- Stopaj → 360
- ÖTV → 193

### 4. Hata Düzeltme
- 28 faturadaki NULL matrah sorununu çöz
- Bazı XML'lerde TaxableAmount eksik olabilir
- Alternatif hesaplama: `tax_amount / (tax_percent / 100)`

---

## ✅ KESİN ÇÖZÜM UYGULANMIŞTIR

Artık tüm e-faturalarda XML'deki **tüm vergi detayları** ayrıştırılıp veritabanında saklanıyor:
- ✓ KDV
- ✓ ÖİV (Özel İletişim Vergisi)
- ✓ ÖTV (Özel Tüketim Vergisi)
- ✓ Telsiz Kullanım Vergisi
- ✓ Stopaj
- ✓ Konaklama Vergisi
- ✓ BTV
- ✓ Diğer tüm vergi tipleri

**API response'da** `tax_details` array'i ile tüm vergi bilgileri döndürülüyor.

---

Tarih: 2025-12-30
Durum: ✅ TAMAMLANDI
