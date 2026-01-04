# 191 HESAP YAPISINI DETAYLANDIRMA ANALİZİ VE GEÇİŞ PLANI

## 📊 MEVCUT DURUM

### 191 Hesapları Kullanım İstatistikleri
```
Hesap Kodu      Hesap Adı                                İşlem      BORÇ             ALACAK          
191.00001       İndirilecek Kdv                          3,830      156,124,908.83   0.00
191.00002       Sorumlu Sıfatıyla Kdv Tevkifatı          194        3,094,888.11     0.00
```

**Önemli Bulgular:**
- Toplam 4,024 işlemde 191 hesabı kullanılmış
- Toplam KDV tutarı: 159,219,796.94 TL
- KDV oranına göre ayrım YOK - tüm oranlar 191.00001 ve 191.00002'de karışık
- transaction_lines.vat_rate kolonunda KDV oranı KAYITLI DEĞİL (boş)
- withholding_rate kolonunda tevkifat oranı KAYITLI DEĞİL (boş)

### E-Fatura Verileri
- Toplam 3,538 adet e-fatura XML'i mevcut
- XML'lerde invoice_tax tablosunda KDV oranları (`tax_percent`) mevcut
- XML'lerde withholding yapısı (`withheld_tax_category`) mevcut

---

## 🎯 ÖNERİLEN 191 HESAP YAPISI

### YENİ HESAP PLANI

#### A. Normal KDV (Tevkifatsız)
```
191.01.001  İndirilecek KDV %1
191.08.001  İndirilecek KDV %8
191.10.001  İndirilecek KDV %10
191.18.001  İndirilecek KDV %18
191.20.001  İndirilecek KDV %20
```

#### B. Tevkifatlı KDV
```
191.01.002  Sorumlu Sıfatıyla KDV Tevkifatı %1
191.08.002  Sorumlu Sıfatıyla KDV Tevkifatı %8
191.10.002  Sorumlu Sıfatıyla KDV Tevkifatı %10
191.18.002  Sorumlu Sıfatıyla KDV Tevkifatı %18
191.20.002  Sorumlu Sıfatıyla KDV Tevkifatı %20
```

### HESAP KODU KURALI
```
191.{KDV_ORAN}.{TEVKIFAT}

KDV_ORAN:
- 01 = %1
- 08 = %8
- 10 = %10
- 18 = %18
- 20 = %20

TEVKIFAT:
- 001 = Tevkifatsız (Normal)
- 002 = Tevkifatlı (Sorumlu Sıfatıyla)
```

---

## 🔄 GEÇİŞ STRATEJİSİ

### SEÇENEK 1: E-FATURA XML'DEN GERİYE DÖNÜK GÜNCELLEMEEREKLİ KOŞULLAR:**
✅ E-fatura işlemleri için XML mevcut (3,538 adet)
✅ XML'de KDV oranı (`invoice_tax.tax_percent`) var
✅ XML'de tevkifat bilgisi (`withheld_tax_category`) var
❌ E-fatura olmayan işlemler için veri YOK (bordro, kasa, banka: 22,756 işlem)

**İŞLEYİŞ:**
1. einvoices tablosundan XML parse et
2. Her fatura için KDV oranını bul
3. Tevkifat varsa tespit et (1/2, 3/10, 5/10, 7/10, 9/10)
4. transaction_lines'daki 191.00001/191.00002 kayıtlarını yeni hesaplara böl
5. vat_rate ve withholding_rate kolonlarını doldur

**AVANTAJLAR:**
- E-faturalar için %100 doğru veri
- Otomatik geçiş mümkün

**DEZAVANTAJLAR:**
- E-fatura olmayan 22,756 işlem için manuel müdahale gerekli
- Bu işlemler için KDV oranı bilinmiyor

---

### SEÇENEK 2: YENİDEN GİRİŞ (SADECEİLERİ İÇİN)

**GEREKLİ KOŞULLAR:**
✅ Sadece 2025 yılı ve sonrası işlemler yeniden girilecek

**İŞLEYİŞ:**
1. Eski 191.00001/191.00002 hesaplarını pasif yap
2. Yeni 191.XX.00X hesaplarını oluştur
3. 2025-01-01 sonrası işlemlerde yeni hesapları kullan
4. Eski veriler olduğu gibi kalır (arşiv amaçlı)

**AVANTAJLAR:**
- Geçmiş veri bozulmaz
- Yeni işlemler için temiz başlangıç

**DEZAVANTAJLAR:**
- Raporlamada eski/yeni karışık olur
- Geçmiş veriler detaylı analiz edilemez

---

### SEÇENEK 3: HİBRİT YAKLAŞIM ⭐ ÖNERİLEN

**İŞLEYİŞ:**
1. **Yeni Hesapları Oluştur**
   - 191.01.001, 191.01.002, 191.08.001, 191.08.002, vb.

2. **E-Faturaları Otomatik Güncelle**
   ```sql
   -- XML'den KDV oranını çek ve transaction_lines güncelle
   UPDATE transaction_lines tl
   JOIN transactions t ON tl.transaction_id = t.id
   JOIN einvoices e ON t.document_number = e.document_number
   JOIN accounts old_acc ON tl.account_id = old_acc.id
   JOIN accounts new_acc ON new_acc.code = CONCAT('191.', 
       LPAD(JSON_EXTRACT(e.raw_data, '$.invoice_tax[0].tax_percent'), 2, '0'), 
       '.', 
       CASE 
           WHEN JSON_EXTRACT(e.raw_data, '$.withheld_tax_category') IS NOT NULL THEN '002'
           ELSE '001'
       END
   )
   SET 
       tl.account_id = new_acc.id,
       tl.vat_rate = JSON_EXTRACT(e.raw_data, '$.invoice_tax[0].tax_percent') / 100,
       tl.withholding_rate = CASE 
           WHEN JSON_EXTRACT(e.raw_data, '$.withheld_tax_category') = 'RATE_1_2' THEN 0.50
           WHEN JSON_EXTRACT(e.raw_data, '$.withheld_tax_category') = 'RATE_3_10' THEN 0.30
           WHEN JSON_EXTRACT(e.raw_data, '$.withheld_tax_category') = 'RATE_5_10' THEN 0.50
           WHEN JSON_EXTRACT(e.raw_data, '$.withheld_tax_category') = 'RATE_7_10' THEN 0.70
           WHEN JSON_EXTRACT(e.raw_data, '$.withheld_tax_category') = 'RATE_9_10' THEN 0.90
           ELSE NULL
       END
   WHERE old_acc.code LIKE '191%'
   ```

3. **E-Fatura Olmayan İşlemler İçin Default Atama**
   ```sql
   -- E-fatura olmayan bordro, kasa, banka işlemleri için %20 varsay
   UPDATE transaction_lines tl
   JOIN transactions t ON tl.transaction_id = t.id
   JOIN accounts old_acc ON tl.account_id = old_acc.id
   JOIN accounts new_acc ON new_acc.code = '191.20.001'
   SET 
       tl.account_id = new_acc.id,
       tl.vat_rate = 0.20
   WHERE old_acc.code = '191.00001'
     AND NOT EXISTS (SELECT 1 FROM einvoices e WHERE e.document_number = t.document_number)
   ```

4. **Manuel Kontrol Listesi Oluştur**
   ```sql
   -- Gözden geçirilmesi gereken kayıtlar
   SELECT 
       t.transaction_number,
       t.transaction_date,
       t.document_type,
       t.description,
       tl.debit,
       'Manuel Kontrol Gerekli' as durum
   FROM transaction_lines tl
   JOIN transactions t ON tl.transaction_id = t.id
   JOIN accounts a ON tl.account_id = a.id
   WHERE a.code LIKE '191%'
     AND tl.vat_rate IS NULL
   ORDER BY t.transaction_date DESC
   ```

**AVANTAJLAR:**
- E-faturalar için %100 otomatik (%15 veri)
- Diğer işlemler için mantıklı default (%85 veri)
- Manuel kontrol listesi ile doğrulama imkanı

**DEZAVANTAJLAR:**
- Default atamalar %100 doğru olmayabilir (ama %20 çoğunlukla doğru)

---

## 📋 UYGULAMA PLANI

### AŞAMA 1: HAZIRLIK
```sql
-- 1. Yeni hesapları oluştur
INSERT INTO accounts (code, name, account_type, is_active) VALUES
('191.01.001', 'İndirilecek KDV %1', 'ASSET', true),
('191.01.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %1', 'ASSET', true),
('191.08.001', 'İndirilecek KDV %8', 'ASSET', true),
('191.08.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %8', 'ASSET', true),
('191.10.001', 'İndirilecek KDV %10', 'ASSET', true),
('191.10.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %10', 'ASSET', true),
('191.18.001', 'İndirilecek KDV %18', 'ASSET', true),
('191.18.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %18', 'ASSET', true),
('191.20.001', 'İndirilecek KDV %20', 'ASSET', true),
('191.20.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %20', 'ASSET', true);

-- 2. Yedek al
CREATE TABLE transaction_lines_backup_191 AS SELECT * FROM transaction_lines;
```

### AŞAMA 2: E-FATURA OTOMATİK GÜNCELLEMEarı yaz)
-- Migration script: 20251230_update_191_from_einvoices.sql
```

### AŞAMA 3: DEFAULT ATAMA
```sql
-- Bordro, Kasa, Banka işlemleri için %20 varsay
```

### AŞAMA 4: MANUEL KONTROL
```sql
-- Kontrol listesi çıkar
-- Excel'e aktar
-- Muhasebeci ile gözden geçir
```

### AŞAMA 5: ESKİ HESAPLARI PASİFLEŞTİR
```sql
UPDATE accounts SET is_active = false WHERE code IN ('191.00001', '191.00002');
```

---

## ⚠️ RİSKLER VE ÖNERİLER

### Riskler:
1. **Veri Kaybı:** Yedekleme zorunlu
2. **Yanlış Atama:** Default %20 her zaman doğru olmayabilir
3. **Raporlama:** Eski raporlar yeni hesap yapısını görmeyebilir

### Öneriler:
1. **Test Ortamında Dene:** Production'a geçmeden önce test
2. **Yedekle:** transaction_lines ve transactions tablolarını yedekle
3. **Aşamalı Geç:** Önce 1 ay veriyle test et
4. **Muhasebeci Onayı:** Manuel kontrol listesini muhasebeci ile gözden geçir

---

## 🔧 GELECEKTEKİ E-FATURA İMPORT'LARI

### Otomatik Hesap Seçimi
```python
# backend/app/services/einvoice_accounting_service.py

def get_191_account_code(vat_rate: Decimal, has_withholding: bool) -> str:
    """
    KDV oranı ve tevkifat durumuna göre 191 hesap kodunu döndürür.
    
    Args:
        vat_rate: KDV oranı (0.01, 0.08, 0.10, 0.18, 0.20)
        has_withholding: Tevkifat var mı?
    
    Returns:
        str: Hesap kodu (örn: '191.20.001')
    """
    # KDV oranını 2 haneli stringe çevir
    vat_pct = int(vat_rate * 100)
    vat_str = str(vat_pct).zfill(2)  # '20' -> '20', '1' -> '01'
    
    # Tevkifat durumuna göre son 3 hane
    suffix = '002' if has_withholding else '001'
    
    return f"191.{vat_str}.{suffix}"

# Kullanım:
account_code = get_191_account_code(Decimal('0.20'), False)  # '191.20.001'
account_code = get_191_account_code(Decimal('0.01'), True)   # '191.01.002'
```

---

## ✅ KARAR

**Önerilen Yöntem:** SEÇENİK 3 - HİBRİT YAKLAŞIM

**Gerekçe:**
- E-faturalar için otomatik ve doğru (%15 veri)
- Diğer işlemler için hızlı geçiş (%85 veri)
- Manuel kontrol ile doğrulama imkanı
- Gelecekte temiz veri girişi

**Aksiyonlar:**
1. ✅ Analiz raporu hazırlandı
2. ⏳ Migration script yazılacak
3. ⏳ Test ortamında denenecek
4. ⏳ Kullanıcı onayı alınacak
5. ⏳ Production'a uygulanacak
