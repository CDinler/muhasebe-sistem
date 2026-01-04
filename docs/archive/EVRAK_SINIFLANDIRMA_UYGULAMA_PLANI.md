# MUHASEBE SİSTEMİ - EVRAK SINIFLANDIRMA STANDARTLAŞTIRMA RAPORU
## Mevcut Durum Analizi ve Geliştirme Önerileri
**Tarih:** 25 Aralık 2025

---

## 📊 1. MEVCUT VERİTABANI YAPILANMASI

### 1.1. Transactions Tablosu - Document Type Alanları

Şu anda `transactions` tablosunda:
```sql
document_type VARCHAR(100)
document_subtype VARCHAR(100)
```

**✅ GÜÇLÜ YÖNLERİ:**
- İki seviyeli hiyerarşi zaten var
- Esnek yapı (VARCHAR 100)
- NULL olabiliyor (zorunlu değil)

**❌ ZAYIF YÖNLERİ:**
- Standart değerler yok (free text)
- Kontrol mekanizması yok
- Tutarsız veri girişi riski
- Raporlama için standart terimler yok

### 1.2. E-Invoice Entegrasyonu

`einvoices` tablosunda:
```sql
invoice_scenario VARCHAR(50)   -- TEMEL, TİCARİ
invoice_type VARCHAR(50)        -- SATIS, IADE
```

**✅ İYİ:** E-Fatura standartları takip ediliyor

---

## 📋 2. RAPOR ANALİZİ - DEĞERLENDİRME

### 2.1. Raporun Önerisi (3 Sütunlu Sistem)

```
Ana Evrak Türü: ALIŞ FATURASI / SATIŞ FATURASI
Alt Tür: E-Fatura / E-Arşiv / Kağıt
```

**Sizin sistemde nasıl eşleşir?**

```sql
document_type = 'ALIŞ FATURASI' / 'SATIŞ FATURASI'
document_subtype = 'E-Fatura' / 'E-Arşiv' / 'Kağıt/Matbu'
```

### 2.2. Raporun Doğruluğu ✅

- **SAP/Oracle standartları:** ✅ Doğru referanslar
- **GİB e-dönüşüm:** ✅ Türkiye'ye uygun
- **Logo/Zirve uyumluluk:** ✅ Piyasa standartlarına uygun
- **IAS/IFRS referansları:** ✅ Muhasebe standartlarına uygun

**SONUÇ:** Rapor muhasebe standartlarına uygun ve uygulanabilir.

---

## 🎯 3. SİZİN SİSTEME UYARLAMA ÖNERİLERİ

### 3.1. VERİTABANI TASARIMI

#### YAKLAŞIM 1: ENUM/CHECK Constraint (Katı Kontrol) ⭐ ÖNERİLEN

```sql
-- Yeni migration dosyası oluştur
-- 20251225_standardize_document_types.sql

-- 1. Önce mevcut verileri temizle/standartlaştır
UPDATE transactions 
SET document_type = 'ALIŞ FATURASI'
WHERE document_type IN ('Gelen Fatura', 'Gelen E-Fatura', 'Alım Faturası');

UPDATE transactions 
SET document_type = 'SATIŞ FATURASI'
WHERE document_type IN ('Giden Fatura', 'Giden E-Fatura', 'Satış Faturası');

-- 2. Standart değerleri içeren lookup table oluştur
CREATE TABLE document_types (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- FATURA, NAKİT, KIYMETLİ_EVRAK, PERSONEL, VERGİ, MUHASEBE
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    affects_vat BOOLEAN DEFAULT FALSE,  -- KDV'ye etkisi var mı?
    affects_income BOOLEAN DEFAULT FALSE, -- Gelir/gider etkisi var mı?
    
    CONSTRAINT chk_category CHECK (category IN (
        'FATURA', 'NAKİT', 'KIYMETLİ_EVRAK', 'PERSONEL', 'VERGİ', 'MUHASEBE', 'STOK'
    ))
);

CREATE TABLE document_subtypes (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    document_type_code VARCHAR(50) REFERENCES document_types(code),
    e_document BOOLEAN DEFAULT FALSE,  -- E-dönüşüm belgesi mi?
    gib_integrated BOOLEAN DEFAULT FALSE, -- GİB entegre mi?
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. transactions tablosuna foreign key ekle
ALTER TABLE transactions 
ADD CONSTRAINT fk_document_type 
FOREIGN KEY (document_type) REFERENCES document_types(code);

ALTER TABLE transactions 
ADD CONSTRAINT fk_document_subtype 
FOREIGN KEY (document_subtype) REFERENCES document_subtypes(code);
```

**AVANTAJLAR:**
- ✅ Veri bütünlüğü garanti
- ✅ Standartlaştırma zorunlu
- ✅ Dropdown menüler için hazır liste
- ✅ Yanlış veri girişi imkansız

**DEZAVANTAJLAR:**
- ⚠️ Yeni tür eklemek için migration gerekir
- ⚠️ Mevcut verileri dönüştürmek gerekir

#### YAKLAŞIM 2: Referans Tablo (Esnek) - Alternatif

```sql
-- Sadece referans amaçlı tablo, zorunlu değil
CREATE TABLE document_type_reference (
    id SERIAL PRIMARY KEY,
    type_code VARCHAR(50) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    subtype_code VARCHAR(50),
    subtype_name VARCHAR(100),
    category VARCHAR(50),
    is_recommended BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,  -- Kaç kez kullanıldı?
    last_used TIMESTAMP,
    notes TEXT
);

-- transactions tablosu değişmez, ama frontend bu tablodan seçenekleri çeker
```

**AVANTAJLAR:**
- ✅ Esnek (yeni tür kolayca eklenir)
- ✅ Geriye dönük uyumlu
- ✅ Mevcut verilere dokunmadan çalışır

**DEZAVANTAJLAR:**
- ❌ Zorunlu değil, tutarsızlık riski var
- ❌ Free text girişi hala mümkün

---

### 3.2. STANDART EVRAK TÜRLERİ LİSTESİ

#### A. FATURALAR

```sql
INSERT INTO document_types VALUES
('ALIS_FATURASI', 'Alış Faturası', 'FATURA', 'Satın alınan mal/hizmet faturası', true, true, true),
('SATIS_FATURASI', 'Satış Faturası', 'FATURA', 'Satılan mal/hizmet faturası', true, true, true),
('IADE_FATURASI', 'İade Faturası', 'FATURA', 'Mal/hizmet iadesi faturası', true, true, true),
('HAKEDIS_FATURASI', 'Hakediş Faturası', 'FATURA', 'İnşaat hakediş faturası', true, true, true),
('PROFORMA_FATURA', 'Proforma Fatura', 'FATURA', 'Ön fatura', true, false, false);

INSERT INTO document_subtypes VALUES
('E_FATURA', 'E-Fatura', 'ALIS_FATURASI', true, true, 'GİB E-Fatura'),
('E_FATURA', 'E-Fatura', 'SATIS_FATURASI', true, true, 'GİB E-Fatura'),
('E_ARSIV', 'E-Arşiv Fatura', 'ALIS_FATURASI', true, true, 'GİB E-Arşiv'),
('E_ARSIV', 'E-Arşiv Fatura', 'SATIS_FATURASI', true, true, 'GİB E-Arşiv'),
('KAGIT_MATBU', 'Kağıt/Matbu Fatura', 'ALIS_FATURASI', false, false, 'Geleneksel fatura'),
('KAGIT_MATBU', 'Kağıt/Matbu Fatura', 'SATIS_FATURASI', false, false, 'Geleneksel fatura'),
('ITHALAT', 'İthalat Faturası', 'ALIS_FATURASI', false, false, 'Yurtdışı alım'),
('IHRACAT', 'İhracat Faturası', 'SATIS_FATURASI', false, false, 'Yurtdışı satış');
```

#### B. NAKİT İŞLEMLERİ

```sql
INSERT INTO document_types VALUES
('KASA_TAHSILAT', 'Kasa Tahsilat Fişi', 'NAKİT', 'Kasaya gelen para', true, false, true),
('KASA_TEDIYE', 'Kasa Tediye Fişi', 'NAKİT', 'Kasadan çıkan para', true, false, true),
('BANKA_TAHSILAT', 'Banka Tahsilat Fişi', 'NAKİT', 'Bankaya gelen para', true, false, true),
('BANKA_TEDIYE', 'Banka Tediye Fişi', 'NAKİT', 'Bankadan çıkan para', true, false, true),
('DEKONT', 'Dekont', 'NAKİT', 'Banka işlem belgesi', true, false, false),
('VIRMAN', 'Virman Fişi', 'NAKİT', 'Hesaplar arası transfer', true, false, false);

INSERT INTO document_subtypes VALUES
('NAKIT', 'Nakit', 'KASA_TAHSILAT', false, false, NULL),
('NAKIT', 'Nakit', 'KASA_TEDIYE', false, false, NULL),
('EFT_HAVALE', 'EFT/Havale', 'BANKA_TAHSILAT', false, false, NULL),
('EFT_HAVALE', 'EFT/Havale', 'BANKA_TEDIYE', false, false, NULL),
('POS', 'POS (Kredi Kartı)', 'BANKA_TAHSILAT', false, false, NULL),
('KREDI_KARTI', 'Kredi Kartı Ödemesi', 'BANKA_TEDIYE', false, false, NULL),
('CEK', 'Çek', 'BANKA_TAHSILAT', false, false, NULL),
('CEK', 'Çek', 'BANKA_TEDIYE', false, false, NULL);
```

#### C. KIYMETLİ EVRAK

```sql
INSERT INTO document_types VALUES
('ALINAN_CEK', 'Alınan Çek', 'KIYMETLİ_EVRAK', 'Müşteriden alınan çek', true, false, false),
('VERILEN_CEK', 'Verilen Çek', 'KIYMETLİ_EVRAK', 'Tedarikçiye verilen çek', true, false, false),
('ALINAN_SENET', 'Alınan Senet', 'KIYMETLİ_EVRAK', 'Müşteriden alınan senet', true, false, false),
('VERILEN_SENET', 'Verilen Senet', 'KIYMETLİ_EVRAK', 'Tedarikçiye verilen senet', true, false, false);
```

#### D. PERSONEL İŞLEMLERİ

```sql
INSERT INTO document_types VALUES
('MAAS_BORDRO', 'Maaş Bordrosu', 'PERSONEL', 'Aylık maaş bordrosu', true, false, true),
('SGK_BILDIRGE', 'SGK Bildirge', 'PERSONEL', 'SGK prim bildirimi', true, false, false);

INSERT INTO document_subtypes VALUES
('AYLIK_MAAS', 'Aylık Maaş', 'MAAS_BORDRO', false, false, NULL),
('PRIM', 'Prim Ödemesi', 'MAAS_BORDRO', false, false, NULL),
('IKRAMIYE', 'İkramiye/Bonus', 'MAAS_BORDRO', false, false, NULL),
('KIDEM_IHBAR', 'Kıdem/İhbar Tazminatı', 'MAAS_BORDRO', false, false, NULL);
```

#### E. MUHASEBE FİŞLERİ

```sql
INSERT INTO document_types VALUES
('YEVMIYE_FISI', 'Yevmiye Fişi', 'MUHASEBE', 'Manuel muhasebe kaydı', true, false, false),
('MAHSUP_FISI', 'Mahsup Fişi', 'MUHASEBE', 'Alacak-borç mahsubu', true, false, false),
('ACILIS_FISI', 'Açılış Fişi', 'MUHASEBE', 'Dönem açılış kaydı', true, false, false),
('KAPANIS_FISI', 'Kapanış Fişi', 'MUHASEBE', 'Dönem kapanış kaydı', true, false, false),
('DUZELTICI_FIS', 'Düzeltici Fiş', 'MUHASEBE', 'Hata düzeltme kaydı', true, false, false),
('TERS_KAYIT', 'Ters Kayıt', 'MUHASEBE', 'İptal kaydı', true, false, false);
```

---

### 3.3. MEVCUT VERİLERİ DÖNÜŞTÜRME

```sql
-- Analiz: Mevcut document_type'lar ne durumda?
SELECT 
    document_type,
    document_subtype,
    COUNT(*) as kayit_sayisi,
    MIN(transaction_date) as ilk_kullanim,
    MAX(transaction_date) as son_kullanim
FROM transactions
WHERE document_type IS NOT NULL
GROUP BY document_type, document_subtype
ORDER BY kayit_sayisi DESC;
```

**Dönüşüm Script Örneği:**

```sql
-- E-Invoice'dan gelen kayıtları standartlaştır
UPDATE transactions t
JOIN einvoices e ON t.id = e.transaction_id
SET 
    t.document_type = CASE 
        WHEN e.invoice_type = 'SATIS' THEN 'SATIS_FATURASI'
        WHEN e.invoice_type = 'IADE' AND e.invoice_scenario = 'TEMEL' THEN 'IADE_FATURASI'
        ELSE 'ALIS_FATURASI'
    END,
    t.document_subtype = CASE
        WHEN e.invoice_scenario IN ('TEMEL', 'TICARI') THEN 'E_FATURA'
        WHEN e.invoice_scenario = 'EARSIVFATURA' THEN 'E_ARSIV'
        ELSE 'E_FATURA'
    END
WHERE e.id IS NOT NULL;

-- Manuel girişleri standartlaştır (description alanına göre)
UPDATE transactions
SET 
    document_type = 'BANKA_TAHSILAT',
    document_subtype = 'EFT_HAVALE'
WHERE (description LIKE '%havale%' OR description LIKE '%eft%')
  AND document_type IS NULL;

-- Bordro kayıtları
UPDATE transactions
SET 
    document_type = 'MAAS_BORDRO',
    document_subtype = 'AYLIK_MAAS'
WHERE description LIKE '%bordro%' OR description LIKE '%maaş%';
```

---

## 🚀 4. UYGULAMA PLANI

### FAZA 1: HAZIRLIK (1 gün)

1. **Mevcut Durum Analizi**
```bash
python backend/analyze_document_types.py
```

2. **Test Migration Oluştur**
```sql
-- database/migrations/20251225_standardize_document_types.sql
```

3. **Dönüşüm Mapping Oluştur**
- Hangi eski değer → Hangi yeni değer?
- Excel'de mapping tablosu hazırla

### FAZA 2: VERITABANI (2 gün)

1. **Lookup Tablolarını Oluştur**
```sql
CREATE TABLE document_types...
CREATE TABLE document_subtypes...
```

2. **Seed Data Ekle**
```sql
INSERT INTO document_types VALUES...
```

3. **Mevcut Verileri Temizle**
```sql
UPDATE transactions SET...
```

4. **Foreign Key Ekle** (opsiyonel - önce test edin)
```sql
ALTER TABLE transactions ADD CONSTRAINT...
```

### FAZA 3: BACKEND (1 gün)

1. **Model Güncellemeleri**
```python
# app/models/document_type.py
class DocumentType(Base):
    __tablename__ = "document_types"
    code = Column(String(50), primary_key=True)
    name = Column(String(100))
    category = Column(String(50))
    ...
```

2. **API Endpoints**
```python
# app/api/v1/endpoints/document_types.py
@router.get("/document-types")
def get_document_types():
    # Dropdown için liste döndür
    pass

@router.get("/document-subtypes/{type_code}")
def get_subtypes(type_code):
    # Ana türe göre alt türleri döndür
    pass
```

3. **CRUD Fonksiyonları**
```python
# app/crud/document_types.py
def get_all_document_types(db):
    pass

def get_subtypes_for_type(db, type_code):
    pass
```

### FAZA 4: FRONTEND (2 gün)

1. **Dropdown Component**
```typescript
// Cascading dropdown: Önce Ana Tür seç → Alt Tür seç
<Select 
    options={documentTypes}
    onChange={handleTypeChange}
/>

<Select 
    options={documentSubtypes}
    disabled={!selectedType}
/>
```

2. **Form Validasyonu**
```typescript
// Ana tür seçilmediyse kayıt yapma
if (!documentType || !documentSubtype) {
    notification.error('Evrak türü ve alt türü zorunludur');
}
```

3. **Raporlama Filtreleri**
```typescript
// Rapor sayfasında kategori bazlı filtreleme
<Select>
    <Option value="FATURA">Faturalar</Option>
    <Option value="NAKİT">Nakit İşlemleri</Option>
    <Option value="PERSONEL">Personel</Option>
</Select>
```

### FAZA 5: TEST & DOĞRULAMA (1 gün)

1. **Veri Doğrulama**
```sql
-- Tüm kayıtlar standart mı?
SELECT COUNT(*) FROM transactions 
WHERE document_type NOT IN (SELECT code FROM document_types);

-- KDV toplamları doğru mu?
SELECT document_type, SUM(vat_amount) 
FROM transaction_lines 
GROUP BY document_type;
```

2. **Raporlar Kontrol**
- KDV beyanname raporu çalışıyor mu?
- Gelir-gider raporu doğru mu?
- E-Fatura raporları çalışıyor mu?

### FAZA 6: DEPLOYMENT (0.5 gün)

1. Backup al
2. Migration çalıştır
3. Verileri dönüştür
4. Frontend deploy et
5. Kullanıcı eğitimi

**TOPLAM SÜRE: ~7.5 gün**

---

## 📊 5. BEKLENEN FAYDALAR

### 5.1. RAPORLAMA

**ÖNCE (Mevcut):**
```sql
-- KDV raporu için karmaşık query
SELECT * FROM transactions
WHERE (document_type LIKE '%Fatura%' 
   OR document_type LIKE '%FATURA%'
   OR document_type LIKE '%invoice%')
  AND document_type NOT LIKE '%Proforma%';
```

**SONRA (Standart):**
```sql
-- Basit ve güvenilir
SELECT * FROM transactions t
JOIN document_types dt ON t.document_type = dt.code
WHERE dt.affects_vat = true
  AND dt.category = 'FATURA';
```

### 5.2. YAZILIM ENTEGRASYONU

- ✅ Luca/Zirve/Logo uyumlu export
- ✅ GİB e-dönüşüm standartlarına uygun
- ✅ API client'lar için net enum'lar

### 5.3. VERİ KALİTESİ

- ✅ Yanlış veri girişi imkansız
- ✅ Tutarlı terminoloji
- ✅ Otomatik sınıflandırma mümkün

---

## ⚠️ 6. RİSKLER & ÇÖZÜMLER

### Risk 1: Mevcut Veriler Uyumsuz

**Çözüm:**
```sql
-- Geçici "DİĞER" kategorisi oluştur
INSERT INTO document_types VALUES
('DIGER', 'Diğer', 'MUHASEBE', 'Sınıflandırılmamış', true, false, false);

-- Uyumsuz kayıtları buraya ata
UPDATE transactions 
SET document_type = 'DIGER'
WHERE document_type NOT IN (SELECT code FROM document_types);

-- Sonra manuel incele ve düzelt
```

### Risk 2: E-Invoice Entegrasyonu Bozulabilir

**Çözüm:**
```sql
-- E-Invoice mapping tablosu oluştur
CREATE TABLE einvoice_document_type_mapping (
    invoice_type VARCHAR(50),
    invoice_scenario VARCHAR(50),
    document_type_code VARCHAR(50),
    document_subtype_code VARCHAR(50)
);

-- Her e-invoice türü için mapping
INSERT INTO einvoice_document_type_mapping VALUES
('SATIS', 'TEMEL', 'SATIS_FATURASI', 'E_FATURA'),
('SATIS', 'TICARI', 'SATIS_FATURASI', 'E_FATURA'),
('SATIS', 'EARSIVFATURA', 'SATIS_FATURASI', 'E_ARSIV');
```

### Risk 3: Kullanıcılar Yeni Sisteme Alışamaz

**Çözüm:**
- Frontend'de eski-yeni eşleştirme göster
- Tooltip'lerde "eski: Gelen E-Fatura → yeni: Alış Faturası - E-Fatura"
- İlk 1 ay eski isimler de gösterilsin

---

## 🎯 7. SONUÇ & TAVSİYE

### Rapor Değerlendirmesi

**RAPOR NOTUM: 9/10** ⭐⭐⭐⭐⭐

**GÜÇLÜ YÖNLER:**
- ✅ SAP/Oracle best practices doğru
- ✅ Türkiye'ye özgü (GİB/VUK) uyumlu
- ✅ Pratik uygulama örnekleri var
- ✅ Excel dönüşüm formülleri mevcut

**GELİŞTİRİLEBİLİR YÖNLER:**
- Personel işlemleri daha detaylı olabilir (puantaj, izin vs.)
- E-İrsaliye, E-Müstahsil entegrasyonu eksik
- API standartları (REST best practices) eklenebilir

### Sizin İçin Önerim

**✅ UYGULAYALIM!**

Ancak şu değişikliklerle:

1. **İlk aşama:** Lookup tablo + referans (Yaklaşım 2)
   - Esnek, hızlı uygulama
   - Mevcut sistemi bozmaz

2. **İkinci aşama:** Foreign key constraint (Yaklaşım 1)
   - Veriler temizlendikten sonra
   - Veri kalitesi artınca

3. **Özel eklentiler:**
   - İnşaat hakediş raporları için özel kategoriler
   - Personel puantaj entegrasyonu
   - Maliyet merkezi bazlı analiz

---

## 📝 8. SONRAKI ADIMLAR

1. **Karar:** Hangi yaklaşımı uygulayalım?
   - [ ] Yaklaşım 1 (Katı kontrol - Foreign Key)
   - [ ] Yaklaşım 2 (Esnek referans)
   - [ ] Hibrit (Önce 2, sonra 1)

2. **Analiz Scripti Çalıştır:**
```bash
python backend/analyze_document_types.py
```

3. **Prototip Migration Hazırla:**
```bash
# Seed data ile test ortamında dene
mysql muhasebe_db < database/migrations/20251225_standardize_document_types.sql
```

4. **Frontend Mockup Hazırla:**
- Cascading dropdown tasarımı
- Form validasyonu

**Devam edelim mi? Hangi adımla başlamak istersiniz?**
