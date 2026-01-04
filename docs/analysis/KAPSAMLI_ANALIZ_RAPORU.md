# KAPSAMLI ANALİZ RAPORU - Evrak Türleri ve 191 Hesap Geçişi

## 📋 ÖZET

Bu rapor, kapsamlı evrak türü sistemi ve 191 hesap yapısı detaylandırması konusunda yapılan analiz ve önerileri içermektedir.

**Tarih:** 30 Aralık 2025  
**Kapsam:**
1. ✅ Mevcut veri analizi
2. ✅ Kapsamlı evrak türü listesi migration'ı
3. ✅ 191 hesap yapısı detaylandırma analizi
4. ✅ Yevmiye kayıt şablonu güncellemesi
5. ✅ Geçiş stratejisi önerileri

---

## 📊 MEVCUT DURUM ANALİZİ

### Veritabanı İstatistikleri
```
Toplam Transaction: 26,294 adet
E-Fatura Sayısı: 3,538 adet
```

### Document Type Dağılımı (İlk 10)
```
BANKA TEDİYE FİŞİ                 11,298 adet (43.0%)
BORDRO                             5,260 adet (20.0%)
KASA TAHSİLAT FİŞİ                 4,097 adet (15.6%)
ALIŞ FATURASI                      3,989 adet (15.2%)
BANKA TAHSİLAT FİŞİ                  739 adet (2.8%)
SATIŞ FATURASI                       309 adet (1.2%)
YEVMİYE FİŞİ                         298 adet (1.1%)
HAKEDİŞ RAPORU                       198 adet (0.8%)
VERİLEN ÇEK                           44 adet (0.2%)
ALINAN ÇEK                             2 adet (0.0%)
```

### Document Subtype Dağılımı (İlk 10)
```
EFT/Havale                        10,954 adet (41.7%)
Personel Ödemesi                   5,260 adet (20.0%)
Nakit                              4,097 adet (15.6%)
E-Fatura                           3,915 adet (14.9%)
Kredi Kartı                        1,082 adet (4.1%)
E-Arşiv                              382 adet (1.5%)
Düzeltme/Mahsup                      298 adet (1.1%)
Tedarikçi Çeki                        44 adet (0.2%)
Kağıt/Matbu                            8 adet (0.0%)
```

### 191 Hesap Kullanımı
```
Hesap Kodu      Hesap Adı                                İşlem      BORÇ             ALACAK          
191.00001       İndirilecek Kdv                          3,830      156,124,908.83   0.00
191.00002       Sorumlu Sıfatıyla Kdv Tevkifatı          194        3,094,888.11     0.00

TOPLAM: 4,024 işlem / 159,219,796.94 TL
```

**❌ SORUNLAR:**
- KDV oranına göre ayrım YOK
- transaction_lines.vat_rate kolonu BOŞ
- withholding_rate kolonu BOŞ
- Tüm KDV oranları (1%, 8%, 10%, 18%, 20%) tek hesapta karışık

---

## ✅ OLUŞTURULAN DOSYALAR

### 1. SQL Migration: Kapsamlı Evrak Türleri
**Dosya:** `database/migrations/20251230_comprehensive_document_types.sql`

**İçerik:**
- 🔷 A. FATURALAR (5 ana tür, 7 alt tür)
- 🔷 B. NAKİT/BANKA İŞLEMLERİ (6 ana tür, 12 alt tür)
- 🔷 C. KIYMETLİ EVRAK (6 ana tür, 13 alt tür)
- 🔷 D. PERSONEL İŞLEMLERİ (2 ana tür, 7 alt tür)
- 🔷 E. GİDER BELGELERİ (3 ana tür, 3 alt tür)
- 🔷 F. VERGİ İŞLEMLERİ (2 ana tür, 9 alt tür)
- 🔷 G. MUHASEBE FİŞLERİ (6 ana tür, 5 alt tür)
- 🔷 H. STOK İŞLEMLERİ (4 ana tür, 6 alt tür)

**TOPLAM:** 34 ana evrak türü, 62 alt evrak türü

**Özellikler:**
✅ Türkçe karakter desteği (utf8mb4_turkish_ci collation)
✅ Otomatik mapping tablosu (document_migration_map)
✅ Mevcut verileri yeni yapıya eşleştirme
✅ Manuel düzeltme için kontrol listeleri

**Kullanım:**
```sql
-- Migration'ı çalıştır
SOURCE database/migrations/20251230_comprehensive_document_types.sql;

-- Mapping sonuçlarını kontrol et
SELECT * FROM document_migration_map WHERE new_document_type_code IS NULL;

-- Manuel düzeltmeler yap
UPDATE document_migration_map 
SET new_document_type_code = 'ALIS_FATURASI', 
    new_document_subtype_code = 'E_FATURA' 
WHERE old_document_type = 'eski değer';
```

---

### 2. Analiz Raporu: 191 Hesap Detaylandırma
**Dosya:** `docs/191_HESAP_DETAYLANDIRMA_ANALIZI.md`

**İçerik:**
- ✅ Mevcut durum analizi
- ✅ Önerilen yeni hesap yapısı (191.XX.00X)
- ✅ 3 farklı geçiş stratejisi (Hibrit yaklaşım önerildi)
- ✅ Uygulama planı (5 aşama)
- ✅ Risk analizi ve öneriler
- ✅ Gelecekteki e-fatura import'ları için kod örnekleri

**Önerilen Hesap Yapısı:**
```
NORMAL KDV (Tevkifatsız):
191.01.001  İndirilecek KDV %1
191.08.001  İndirilecek KDV %8
191.10.001  İndirilecek KDV %10
191.18.001  İndirilecek KDV %18
191.20.001  İndirilecek KDV %20

TEVKİFATLI KDV:
191.01.002  Sorumlu Sıfatıyla KDV Tevkifatı %1
191.08.002  Sorumlu Sıfatıyla KDV Tevkifatı %8
191.10.002  Sorumlu Sıfatıyla KDV Tevkifatı %10
191.18.002  Sorumlu Sıfatıyla KDV Tevkifatı %18
191.20.002  Sorumlu Sıfatıyla KDV Tevkifatı %20
```

**Geçiş Stratejisi: Hibrit Yaklaşım ⭐**
1. **E-Faturalar (3,538 adet):** XML'den KDV oranı ve tevkifat otomatik parse edilecek
2. **Diğer İşlemler (22,756 adet):** %20 KDV default atanacak
3. **Manuel Kontrol:** Kontrol listesi ile doğrulama yapılacak

**Avantajlar:**
- E-faturalar için %100 otomatik ve doğru
- Diğer işlemler için hızlı geçiş
- Manuel kontrol imkanı

---

### 3. Yevmiye Kayıt Şablonu
**Dosya:** `YEVMIYE_KAYDI_SABLONU.md`

**İçerik:**
- ✅ Veritabanı yapısı (transactions, transaction_lines)
- ✅ Kapsamlı evrak türleri listesi (8 kategori)
- ✅ Yeni 191 hesap yapısı açıklaması
- ✅ 6 fatura kategorisi kayıt örnekleri
- ✅ 6 özel durum senaryosu (iade, istisna, SGK, vb.)
- ✅ Karar kontrol listesi

**Özellikler:**
- quantity kolonunun ikili kullanımı açıklandı (miktar/oran)
- vat_rate, withholding_rate, vat_base amaçları belirtildi
- Her kategori için detaylı transaction_lines örneği
- Çoklu satır işlemleri için 2 seçenek sunuldu

**Kullanım:**
Şablonu doldurun ve şu kararları verin:
- [ ] 191 hesap yapısı (detaylı/basit)
- [ ] Çoklu satır yöntemi (ayrı/toplu)
- [ ] İade faturası mantığı (ters kayıt)
- [ ] İstisna durum yöntemi (191 yok/var)
- [ ] Farklı KDV oranları (ayrı/tek)

---

## 🔄 MEVCUT YEVMİYE KAYITLARINA ETKİ

### Soru: 191 değişikliği mevcut kayıtlara uygulanabilir mi?

**CEVAP: EVET, ama kısmen otomatik olabilir.**

### Otomatik Geçiş Yapılabilecekler:
✅ **E-Faturalar (3,538 adet / %13.5):**
- XML'de KDV oranı (`invoice_tax.tax_percent`) mevcut
- XML'de tevkifat bilgisi (`withheld_tax_category`) mevcut
- %100 otomatik geçiş mümkün

### Manuel Müdahale Gerekecekler:
❌ **Bordro, Kasa, Banka İşlemleri (22,756 adet / %86.5):**
- KDV oranı bilinmiyor
- Tevkifat bilgisi yok
- %20 KDV default atanabilir (çoğunlukla doğru)
- Manuel kontrol listesi ile doğrulama önerilir

### Önerilen Strateji:
```sql
-- AŞAMA 1: Yeni hesapları oluştur
INSERT INTO accounts (...) VALUES ('191.01.001', ...), ('191.01.002', ...);

-- AŞAMA 2: E-faturaları otomatik güncelle
UPDATE transaction_lines tl
JOIN transactions t ON tl.transaction_id = t.id
JOIN einvoices e ON t.document_number = e.document_number
SET 
    tl.account_id = (SELECT id FROM accounts WHERE code = CONCAT('191.', LPAD(...), '.001')),
    tl.vat_rate = JSON_EXTRACT(e.raw_data, '$.invoice_tax[0].tax_percent') / 100
WHERE old_account.code = '191.00001';

-- AŞAMA 3: Diğer işlemler için %20 varsay
UPDATE transaction_lines tl
SET 
    tl.account_id = (SELECT id FROM accounts WHERE code = '191.20.001'),
    tl.vat_rate = 0.20
WHERE tl.account_id = (SELECT id FROM accounts WHERE code = '191.00001')
  AND NOT EXISTS (SELECT 1 FROM einvoices WHERE ...);

-- AŞAMA 4: Manuel kontrol listesi oluştur
SELECT ... FOR REVIEW;
```

---

## ⚠️ RİSKLER VE ÖNEMLİ NOTLAR

### Riskler:
1. **Veri Kaybı:** Migration sırasında yedekleme zorunlu
2. **Yanlış Atama:** Default %20 her zaman doğru olmayabilir
3. **Raporlama:** Eski raporlar yeni hesap yapısını görmeyebilir
4. **Performans:** 26,294 kayıt güncellenecek (yavaş olabilir)

### Önemli Notlar:
⚠️ **Evrak Türleri Migration'ı Önce Test Edilmeli**
- Migration script şu an sadece mapping tablosu oluşturuyor
- Transactions tablosunu henüz güncellemez
- Önce mapping'leri kontrol edin, sonra transactions güncelleyin

⚠️ **191 Geçişi Geriye Dönüşsüz**
- Eski 191.00001/191.00002 hesapları pasifleştirilecek
- İşlem öncesi mutlaka yedek alın
- Test ortamında deneyin

⚠️ **Frontend Değişiklikleri Gerekli**
- document_type/document_subtype dropdown'ları güncellenmeli
- document_type_id/document_subtype_id kullanılmalı
- 191 hesap seçimi dinamik olmalı (KDV oranına göre)

---

## 📝 SONRAKI ADIMLAR

### 1. KARAR AŞAMASI (SİZDEN BEKLENEN)
- [ ] YEVMIYE_KAYDI_SABLONU.md dosyasını doldurun
- [ ] 191 hesap yapısı kararını verin (detaylı/basit)
- [ ] Çoklu satır yöntemini belirleyin
- [ ] Özel durumlar için tercihlerinizi belirtin

### 2. MIGRATION HAZIRLIĞI (ONAY SONRASI)
- [ ] Test veritabanı oluştur
- [ ] Evrak türleri migration'ını test et
- [ ] Mapping sonuçlarını kontrol et
- [ ] Manuel düzeltmeleri yap

### 3. 191 HESAP GEÇİŞİ (KARAR SONRASI)
- [ ] Yeni hesapları oluştur (191.XX.00X)
- [ ] E-fatura otomatik geçiş script'i yaz
- [ ] Default atama script'i yaz
- [ ] Manuel kontrol listesi oluştur

### 4. FRONTEND GÜNCELLEMELERİ
- [ ] document_types API endpoints'lerini kullan
- [ ] Dropdown'ları yeni yapıya adapte et
- [ ] 191 hesap seçimini KDV oranına göre otomatikleştir
- [ ] Import modal'ını yeni yapıya göre güncelle

### 5. TEST VE DOĞRULAMA
- [ ] Test ortamında migration'ı çalıştır
- [ ] 10 farklı evrak türüyle test et
- [ ] Raporları kontrol et (KDV beyannamesi, mizan, vb.)
- [ ] Muhasebeci onayı al

### 6. PRODUCTION GEÇİŞİ
- [ ] Tüm verileri yedekle
- [ ] Migration'ları çalıştır
- [ ] Kontrol listelerini gözden geçir
- [ ] Kullanıcıları bilgilendir

---

## 📊 ÖZET İSTATİSTİKLER

### Oluşturulan Dosyalar:
```
✅ database/migrations/20251230_comprehensive_document_types.sql (380 satır)
✅ docs/191_HESAP_DETAYLANDIRMA_ANALIZI.md (450 satır)
✅ YEVMIYE_KAYDI_SABLONU.md (520 satır)
✅ backend/analyze_current_state.py (120 satır)
✅ docs/KAPSAMLI_ANALIZ_RAPORU.md (bu dosya)
```

### Kapsanan Konular:
- ✅ 34 ana evrak türü
- ✅ 62 alt evrak türü
- ✅ 10 yeni 191 hesabı (5 normal + 5 tevkifatlı)
- ✅ 6 fatura kategorisi
- ✅ 6 özel durum senaryosu
- ✅ 3 farklı geçiş stratejisi

### Etkilenen Kayıtlar:
- 📊 26,294 transaction
- 📊 4,024 transaction_line (191 hesaplı)
- 📊 3,538 e-fatura (XML mevcut)
- 📊 22,756 diğer işlem (manuel kontrol)

---

## ✅ SONUÇ

**Tüm analiz ve planlamalar tamamlandı. Artık uygulama aşamasına hazırız.**

**Sizden beklenen:**
1. YEVMIYE_KAYDI_SABLONU.md dosyasını inceleyin ve checkbox'ları işaretleyin
2. 191 hesap yapısı kararını verin (detaylı/basit)
3. Evrak türleri migration'ını onaylayın

**Onay sonrası:**
- Migration script'leri çalıştırılacak
- Frontend güncellemeleri yapılacak
- Test süreçleri başlatılacak

**Sorularınız için hazırım!** 🚀
