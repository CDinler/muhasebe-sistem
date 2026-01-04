# YEVMİYE KAYDI ŞABLONU - Kapsamlı Evrak Türleri ve Hesap Yapısı

## 📋 İÇİNDEKİLER
1. [Veritabanı Yapısı](#veritabanı-yapısı)
2. [Evrak Türleri Sistemi](#evrak-türleri-sistemi)
3. [191 Hesap Yapısı](#191-hesap-yapısı)
4. [Fatura Kategorileri](#fatura-kategorileri)
5. [Özel Durumlar](#özel-durumlar)

---

## VERITABANI YAPISI

### transactions Tablosu (7 Kolon)
| Kolon                 | Tür       | Açıklama                                    |
|-----------------------|-----------|---------------------------------------------|
| transaction_number    | VARCHAR   | F00000001 formatında (transaction_counter)  |
| transaction_date      | DATE      | Fiş tarihi                                  |
| document_type_id      | INT (FK)  | document_types.id (YENİ YAPI)              |
| document_subtype_id   | INT (FK)  | document_subtypes.id (YENİ YAPI)           |
| document_number       | VARCHAR   | Evrak numarası (fatura no, dekont no, vb.)  |
| description           | TEXT      | Fiş açıklaması                              |
| cost_center_id        | INT (FK)  | Maliyet merkezi (şantiye, bölüm)           |

### transaction_lines Tablosu (12 Kolon)
| Kolon              | Tür           | Açıklama                                                    |
|--------------------|---------------|-------------------------------------------------------------|
| account_id         | INT (FK)      | accounts.id (hesap planı)                                   |
| contact_id         | INT (FK/NULL) | contacts.id (sadece 320, 335, 120 vb. cari hesaplarda)     |
| description        | TEXT          | Satır açıklaması                                            |
| debit              | DECIMAL(15,2) | Borç tutarı                                                 |
| credit             | DECIMAL(15,2) | Alacak tutarı                                               |
| quantity           | DECIMAL(15,4) | **İKİLİ AMAÇ:** Mal/hizmet miktarı VEYA KDV/tevkifat oranı |
| unit               | VARCHAR       | Birim (adet, kg, m2, vb.) - Sadece mal/hizmet satırlarında |
| vat_rate           | DECIMAL(5,4)  | KDV oranı (0.01=%1, 0.20=%20) - Sadece KDV satırlarında    |
| withholding_rate   | DECIMAL(5,4)  | Tevkifat oranı (0.10=%10) - Sadece tevkifat satırlarında   |
| vat_base           | DECIMAL(15,2) | Matrah (KDV/tevkifat hesap edilen tutar)                   |

**quantity Kolonunun İki Kullanımı:**
- **Mal/Hizmet Satırı (740, 770, 153, vb.):** Miktar (örn: 100 adet)
- **KDV/Tevkifat Satırı (191, 360):** Oran (örn: 0.20 = %20)

---

## EVRAK TÜRLERİ SİSTEMİ

### 🔷 Kategori: FATURA

| Ana Evrak Türü (document_types) | Alt Tür (document_subtypes)     | Kod                         |
|---------------------------------|---------------------------------|-----------------------------|
| ALIS_FATURASI                   | E_FATURA                        | E-Fatura (işletmeden alış)  |
|                                 | E_ARSIV                         | E-Arşiv (perakendeden alış) |
|                                 | KAGIT_MATBU                     | Kağıt/Matbu fatura          |
|                                 | ITHALAT                         | İthalat faturası            |
| SATIS_FATURASI                  | E_FATURA                        | E-Fatura (işletmeye satış)  |
|                                 | E_ARSIV                         | E-Arşiv (perakendeye satış) |
|                                 | KAGIT_MATBU                     | Kağıt/Matbu fatura          |
|                                 | IHRACAT                         | İhracat faturası            |
| IADE_FATURASI                   | ALIS_IADE                       | Alış iade                   |
|                                 | SATIS_IADE                      | Satış iade                  |
| HAKEDIS_FATURASI                | E_FATURA                        | E-Fatura hakediş            |
|                                 | E_ARSIV                         | E-Arşiv hakediş             |
| PROFORMA_FATURA                 | -                               | Ön fatura                   |

### 🔷 Kategori: KASA/BANKA

| Ana Evrak Türü      | Alt Tür           | Açıklama                    |
|---------------------|-------------------|-----------------------------|
| KASA_TAHSILAT       | NAKIT             | Nakit tahsilat              |
|                     | CEK               | Çek ile tahsilat            |
|                     | SENET             | Senet ile tahsilat          |
| KASA_TEDIYE         | NAKIT             | Nakit ödeme                 |
|                     | CEK               | Çek ile ödeme               |
|                     | SENET             | Senet ile ödeme             |
| BANKA_TAHSILAT      | EFT_HAVALE        | EFT/Havale geliri           |
|                     | POS               | Kredi kartı tahsilat        |
|                     | CEK               | Çek tahsili                 |
|                     | SENET             | Senet tahsili               |
| BANKA_TEDIYE        | EFT_HAVALE        | EFT/Havale gideri           |
|                     | KREDI_KARTI       | Kredi kartı ödemesi         |
|                     | CEK               | Çek ödemesi                 |
|                     | SENET             | Senet ödemesi               |
| DEKONT              | BANKA_DEKONT      | Banka dekontu               |
|                     | POS_DEKONT        | POS dekontu                 |
|                     | ATM_DEKONT        | ATM dekontu                 |
| VIRMAN              | KASA_KASA         | Kasalar arası               |
|                     | BANKA_BANKA       | Bankalar arası              |
|                     | KASA_BANKA        | Kasa-Banka arası            |

### 🔷 Kategori: CEK_SENET

| Ana Evrak Türü         | Alt Tür              | Açıklama                   |
|------------------------|----------------------|----------------------------|
| ALINAN_CEK             | MUSTERI_CEKI         | Tahsilat amaçlı            |
|                        | CIRO_CEKI            | Ciro edilmiş               |
|                        | TEMINAT_CEKI         | Teminat amaçlı             |
| VERILEN_CEK            | TEDARIKCI_CEKI       | Ödeme amaçlı               |
|                        | TEMINAT_CEKI         | Teminat amaçlı             |
| CEK_TAHSILAT_ODEME     | CEK_TAHSIL           | Çek tahsil edildi          |
|                        | CEK_ODEME            | Çek ödendi                 |
|                        | CEK_IADE             | Çek iade edildi            |
|                        | CEK_PROTESTO         | Karşılıksız çek            |
| ALINAN_SENET           | MUSTERI_SENEDI       | Tahsilat amaçlı            |
| VERILEN_SENET          | TEDARIKCI_SENEDI     | Ödeme amaçlı               |
| SENET_TAHSILAT_ODEME   | SENET_TAHSIL         | Senet tahsil edildi        |
|                        | SENET_ODEME          | Senet ödendi               |
|                        | SENET_PROTESTO       | Ödenmedi                   |

### 🔷 Kategori: PERSONEL

| Ana Evrak Türü    | Alt Tür           | Açıklama                   |
|-------------------|-------------------|----------------------------|
| MAAS_BORDROSU     | AYLIK_MAAS        | Normal maaş                |
|                   | PRIM              | Prim ödemesi               |
|                   | IKRAMIYE          | İkramiye/Bonus             |
|                   | AGI               | Asgari geçim indirimi      |
|                   | KIDEM_IHBAR       | Kıdem tazminatı            |
| SGK_BILDIRGESI    | AYLIK_BILDIRGE    | SGK prim bildirimi         |
|                   | ISE_GIRIS_CIKIS   | İşe giriş/çıkış bildirimi  |

### 🔷 Kategori: GIDER

| Ana Evrak Türü            | Alt Tür  | Açıklama         |
|---------------------------|----------|------------------|
| GIDER_PUSULASI            | -        | Belgesiz giderler|
| SERBEST_MESLEK_MAKBUZU    | E_SMM    | Elektronik SMM   |
|                           | KAGIT    | Kağıt SMM        |
| MUSTAHSIL_MAKBUZU         | E_MUSTAHSIL | Elektronik     |
|                           | KAGIT    | Kağıt            |

### 🔷 Kategori: VERGI

| Ana Evrak Türü       | Alt Tür               | Açıklama              |
|----------------------|-----------------------|-----------------------|
| VERGI_BEYANNAMESI    | KDV_BEYANI            | KDV beyannamesi       |
|                      | MUHTASAR_BEYANI       | Muhtasar beyanname    |
|                      | GECICI_VERGI          | Geçici vergi          |
|                      | YILLIK_GELIR          | Yıllık gelir vergisi  |
|                      | STOPAJ_BEYANI         | Stopaj beyannamesi    |
| VERGI_ODEME          | KDV_ODEME             | KDV ödemesi           |
|                      | STOPAJ_ODEME          | Stopaj ödemesi        |
|                      | GELIR_VERGISI_ODEME   | Gelir vergisi ödemesi |
|                      | DAMGA_VERGISI         | Damga vergisi         |

### 🔷 Kategori: MUHASEBE

| Ana Evrak Türü   | Alt Tür            | Açıklama                 |
|------------------|--------------------|--------------------------|
| MAHSUP_FISI      | CARI_MAHSUP        | Alacak-Borç mahsubu      |
|                  | CEK_SENET_MAHSUP   | Kıymetli evrak mahsubu   |
| YEVMIYE_FISI     | -                  | Manuel muhasebe kaydı    |
| ACILIS_FISI      | DONEM_ACILIS       | Yıl/Dönem açılışı        |
|                  | ISLETME_ACILIS     | Yeni işletme açılışı     |
| KAPANIS_FISI     | DONEM_KAPANIS      | Yıl/Dönem kapanışı       |
| DUZELTICI_FIS    | -                  | Hata düzeltme            |
| TERS_KAYIT       | -                  | İptal kaydı              |

### 🔷 Kategori: STOK (İsteğe Bağlı)

| Ana Evrak Türü   | Alt Tür            | Açıklama              |
|------------------|--------------------|-----------------------|
| STOK_GIRIS       | SATIN_ALIM         | Satın alım girişi     |
|                  | SATIS_IADESI_GIRIS | Satış iadesi girişi   |
|                  | FIRE_GIRIS         | Fire girişi           |
| STOK_CIKIS       | SATIS_CIKIS        | Satış çıkışı          |
|                  | ALIS_IADESI_CIKIS  | Alış iadesi çıkışı    |
|                  | FIRE_CIKIS         | Fire çıkışı           |
| SAYIM_FISI       | -                  | Stok sayımı           |
| AMORTISMAN_FISI  | -                  | Amortisman ayrılması  |

---

## 191 HESAP YAPISI

### 🔄 YENİ DETAYLI YAPI (ÖNERİLEN)

#### Normal KDV (Tevkifatsız)
```
191.01.001  İndirilecek KDV %1
191.08.001  İndirilecek KDV %8
191.10.001  İndirilecek KDV %10
191.18.001  İndirilecek KDV %18
191.20.001  İndirilecek KDV %20
```

#### Tevkifatlı KDV
```
191.01.002  Sorumlu Sıfatıyla KDV Tevkifatı %1
191.08.002  Sorumlu Sıfatıyla KDV Tevkifatı %8
191.10.002  Sorumlu Sıfatıyla KDV Tevkifatı %10
191.18.002  Sorumlu Sıfatıyla KDV Tevkifatı %18
191.20.002  Sorumlu Sıfatıyla KDV Tevkifatı %20
```

**Hesap Kodu Kuralı:** `191.{KDV_ORAN}.{TEVKIFAT}`
- KDV_ORAN: 01, 08, 10, 18, 20 (KDV oranı)
- TEVKIFAT: 001 (normal), 002 (tevkifatlı)

### ☑️ KARAR: Yeni Yapıyı Kullan
- [☑️] EVET - Detaylı 191 hesap yapısını kullan (önerilen)
- [ ] HAYIR - Mevcut 191.00001/191.00002 yapısını koru

---

## FATURA KATEGORİLERİ

### Kategori 1: Hizmet Üretim Maliyeti
**Hesap:** 740.XXXXX (Hizmet Üretim Maliyeti)

**Örnek Yevmiye Kaydı:**

| # | account_id | contact_id | description | debit | credit | quantity | unit | vat_rate | withholding_rate | vat_base |
|---|------------|------------|-------------|-------|--------|----------|------|----------|------------------|----------|
| 1 | 740.12345  | NULL       | Elektrik gideri | 10,000.00 | 0.00 | 100 | kWh | NULL | NULL | NULL |
| 2 | 191.20.001 | NULL       | İndirilecek KDV %20 | 2,000.00 | 0.00 | 0.20 | NULL | 0.20 | NULL | 10,000.00 |
| 3 | 360.01.001 | NULL       | Ödenecek Vergi Tevk %10 | 0.00 | 1,000.00 | 0.10 | NULL | NULL | 0.10 | 10,000.00 |
| 4 | 320.12345  | contact.id | TEDARIKCI UNVANI | 0.00 | 11,000.00 | NULL | NULL | NULL | NULL | NULL |

**TOPLAM:** BORÇ: 12,000.00 | ALACAK: 12,000.00

**Açıklama:**
- Satır 1: Gider hesabı (matrah)
- Satır 2: KDV %20 (orana göre 191.20.001)
- Satır 3: Tevkifat %10 (varsa)
- Satır 4: Cari hesap (contact_id ile ilişkili)

---

### Kategori 2: Genel Yönetim Gideri
**Hesap:** 770.XXXXX (Genel Yönetim Giderleri)
**Kayıt Mantığı:** Kategori 1 ile aynı, sadece hesap kodu 770.XXXXX

---

### Kategori 3: Ticari Mallar
**Hesap:** 153 (Ticari Mallar)
**Kayıt Mantığı:** Kategori 1 ile aynı, sadece hesap kodu 153

---

### Kategori 4: Diğer Stoklar
**Hesap:** 157 (Diğer Stoklar)
**Kayıt Mantığı:** Kategori 1 ile aynı, sadece hesap kodu 157

---

### Kategori 5: Demirbaş
**Hesap:** 255.01-05.XXX (Demirbaş alt kategorileri)

**Alt Kategoriler:**
- 255.01.XXX: Konteynerler
- 255.02.XXX: Makine ve Teçhizat
- 255.03.XXX: İnşaat Kalıpları
- 255.04.XXX: Şantiye Alet ve Ekipmanları
- 255.05.XXX: İş Makinaları

**Kayıt Mantığı:** Kategori 1 ile aynı, fakat hesap otomatik oluşturulur:
- `255.{ALT_KATEGORI}.{SIRA_NO}` formatında

---

### Kategori 6: Taşıt
**Hesap:** 255.06.XXX (Taşıtlar)

**Kayıt Mantığı:** Kategori 5 ile aynı, alt kategori 255.06

---

## ÖZEL DURUMLAR

### 1. ÇOKLU SATIŞ SATIRI (Tek Faturada Farklı Kategoriler)

**Seçenek A: Ayrı Satırlar (Önerilen)**
```
SATIR 1: 740.12345  10,000.00  Hizmet A
SATIR 2: 191.20.001  2,000.00  KDV %20 Hizmet A
SATIR 3: 770.56789  5,000.00   Hizmet B
SATIR 4: 191.20.001  1,000.00  KDV %20 Hizmet B
SATIR 5: 320.12345  0.00       18,000.00  Toplam Borç
```

**Seçenek B: Toplanmış**
```
SATIR 1: 740.12345  10,000.00  Hizmet A
SATIR 2: 770.56789   5,000.00  Hizmet B
SATIR 3: 191.20.001  3,000.00  Toplam KDV %20
SATIR 4: 320.12345  0.00       18,000.00  Toplam Borç
```

**Sizin Düzenlemeniz:** Hangi yöntemi tercih ediyorsunuz?
- [ ] Seçenek A (Her kategori ayrı KDV satırı)
- [x] Seçenek B (KDV toplu)

---

### 2. TEVKİFAT HESAPLAMA

**Tevkifat Oranları:**
TEVKİFAT KODLARI LİSTESİ KODU ADI ORANI
601
Yapim İşleri İle Bu İşlerle Birlikte İfa Edilen Mühendislik-Mimarlik Ve Etüt-Proje Hizmetleri
4/10
602
Etüt, Plan-Proje, Danişmanlik, Denetim Ve Benzeri Hizmetler
9/10
603
Makine, Teçhizat, Demirbaş Ve Taşitlara Ait Tadil, Bakim Ve Onarim Hizmetleri
7/10
604
Yemek Servis Hizmeti
5/10
605
Organizasyon Hizmeti
5/10
606
İşgücü Temin Hizmetleri
9/10
607
Özel Güvenlik Hizmeti
9/10
608
Yapi Denetim Hizmetleri
9/10
609
Fason Olarak Yaptirilan Tekstil Ve Konfeksiyon İşleri, Çanta Ve Ayakkabi Dikim İşleri Ve Bu İşlere Aracilik Hizmetleri
7/10
610
Turistik Mağazalara Verilen Müşteri Bulma / Götürme Hizmetleri
9/10
611
Spor Kulüplerinin Yayin, Reklâm Ve İsim Hakki Gelirlerine Konu İşlemleri
9/10
612
Temizlik Hizmeti
9/10
613
Çevre Ve Bahçe Bakim Hizmetleri
9/10
614
Servis Taşimaciliği Hizmeti
5/10
615
Her Türlü Baski Ve Basim Hizmetleri
7/10
616
Diğer Hizmetler [Kdvgut-(I/C-2.1.3.2.13)]
5/10
617
Hurda Metalden Elde Edilen Külçe Teslimleri
7/10
618
Hurda Metalden Elde Edilenler Dişindaki Bakir, Çinko Demir ; Çelik Alüminyum Ve Kurşun Külçe Teslimleri [Kdvgut-(I/C-2.1.3.3.1)]
7/10
619
Bakir, Çinko Ve Alüminyum Ürünlerinin Teslimi
7/10
620
İstisnadan Vazgeçenlerin Hurda Ve Atik Teslimi
7/10
621
Metal, Plastik, Lastik, Kauçuk, Kâğit Ve Cam Hurda Ve Atiklardan Elde Edilen Hammadde Teslimi
9/10
622
Pamuk, Tiftik, Yün Ve Yapaği İle Ham Post Ve Deri Teslimleri
9/10
623
Ağaç Ve Orman Ürünleri Teslimi
5/10
624
Yük Taşimaciliği Hizmeti [Kdvgut-(I/C-2.1.3.2.11)]
2/10
625
Ticari Reklam Hizmetleri [Kdvgut-(I/C-2.1.3.2.15)]
3/10
626
Diğer Teslimler [Kdvgut-(I/C-2.1.3.3.7.)]
2/10
627
Demir-Çelik Ürünlerinin Teslimi [Kdvgut-(I/C-2.1.3.3.8)]
5/10
801
Yapım İşleri ile Bu İşlerle Birlikte İfa Edilen Mühendislik-Mimarlık ve Etüt-Proje Hizmetleri[KDVGUT-(I/C-2.1.3.2.1)]
10/10
802
Etüt, Plan-Proje, Danışmanlık, Denetim ve Benzeri Hizmetler[KDVGUT-(I/C-2.1.3.2.2)]
10/10
803
Makine, Teçhizat, Demirbaş ve Taşıtlara Ait Tadil, Bakım ve Onarım Hizmetleri[KDVGUT- (I/C-2.1.3.2.3)]
10/10
804
Yemek Servis Hizmeti[KDVGUT-(I/C-2.1.3.2.4)]
10/10
805
Organizasyon Hizmeti[KDVGUT-(I/C-2.1.3.2.4)]
10/10
806
İşgücü Temin Hizmetleri[KDVGUT-(I/C-2.1.3.2.5)]
10/10
807
Özel Güvenlik Hizmeti[KDVGUT-(I/C-2.1.3.2.5)]
10/10
808
Yapı Denetim Hizmetleri[KDVGUT-(I/C-2.1.3.2.6)]
10/10
809
Fason Olarak Yaptırılan Tekstil ve Konfeksiyon İşleri, Çanta ve
10/10
UBL-TR Kod Listeleri Aralık 2025
Versiyon: 1.40 15/21
Ayakkabı Dikim İşleri ve Bu İşlere Aracılık Hizmetleri[KDVGUT-(I/C-2.1.3.2.7)]
810
Turistik Mağazalara Verilen Müşteri Bulma/ Götürme Hizmetleri[KDVGUT-(I/C-2.1.3.2.8)]
10/10
811
Spor Kulüplerinin Yayın, Reklâm ve İsim Hakkı Gelirlerine Konu İşlemleri[KDVGUT-(I/C-2.1.3.2.9)]
10/10
812
Temizlik Hizmeti[KDVGUT-(I/C-2.1.3.2.10)]
10/10
813
Çevre ve Bahçe Bakım Hizmetleri[KDVGUT-(I/C-2.1.3.2.10)]
10/10
814
Servis Taşımacılığı Hizmeti[KDVGUT-(I/C-2.1.3.2.11)]
10/10
815
Her Türlü Baskı ve Basım Hizmetleri[KDVGUT-(I/C-2.1.3.2.12)]
10/10
816
Hurda Metalden Elde Edilen Külçe Teslimleri[KDVGUT-(I/C-2.1.3.3.1)]
10/10
817
Hurda Metalden Elde Edilenler Dışındaki Bakır, Çinko, Demir Çelik, Alüminyum ve Kurşun Külçe Teslimi [KDVGUT-(I/C-2.1.3.3.1)]
10/10
818
Bakır, Çinko, Alüminyum ve Kurşun Ürünlerinin Teslimi[KDVGUT-(I/C-2.1.3.3.2)]
10/10
819
İstisnadan Vazgeçenlerin Hurda ve Atık Teslimi[KDVGUT-(I/C-2.1.3.3.3)]
10/10
820
Metal, Plastik, Lastik, Kauçuk, Kâğıt ve Cam Hurda ve Atıklardan Elde Edilen Hammadde Teslimi[KDVGUT-(I/C-2.1.3.3.4)]
10/10
821
Pamuk, Tiftik, Yün ve Yapağı İle Ham Post ve Deri Teslimleri[KDVGUT-(I/C-2.1.3.3.5)]
10/10
822
Ağaç ve Orman Ürünleri Teslimi[KDVGUT-(I/C-2.1.3.3.6)]
10/10
823
Yük Taşımacılığı Hizmeti [KDVGUT-(I/C-2.1.3.2.11)]
10/10
824
Ticari Reklam Hizmetleri [KDVGUT-(I/C-2.1.3.2.15)]
10/10
825
Demir-Çelik Ürünlerinin Teslimi [KDVGUT-(I/C-2.1.3.3.8)]
10/10


**Hesaplama:**
```
Matrah: 10,000.00 TL
KDV %20: 2,000.00 TL
Tevkifat %10: 10,000.00 × 0.10 = 1,000.00 TL (360 hesaba ALACAK)
Net Ödeme: 11,000.00 TL
```

**Sizin Düzenlemeniz:** Tevkifat hesaplama formülü doğru mu?
- [x] EVET
- [ ] HAYIR (Açıklayın): _______________________

---

### 3. İADE FATURASI

**Kayıt Mantığı:** Normal fatura ile aynı, fakat BORÇ/ALACAK ters çevrilir

```
SATIR 1: 740.12345  0.00       10,000.00  İade (ALACAK)
SATIR 2: 191.20.001  0.00       2,000.00  İade KDV (ALACAK)
SATIR 3: 320.12345  12,000.00  0.00       İade Borç (BORÇ)
```

**Sizin Düzenlemeniz:** İade mantığı doğru mu?
- [ ] EVET
- [x] HAYIR (Açıklayın): 740 alacak olamaz, onun yerine 602.00002 - Alıştan İade hesabını kullanacağız.kalanı aynı.


---

### 4. İSTİSNA/ÖZEL MATRAH (KDV Yok)

**Örnek:** İhracat, kitap, eğitim hizmetleri

```
SATIR 1: 740.12345  10,000.00  0.00  İstisna hizmet
SATIR 2: 320.12345  0.00       10,000.00  (KDV satırı YOK)
```

**Sizin Düzenlemeniz:** İstisna durumlarda 191 satırı açılmasın mı?
- [x ] EVET - 191 satırı açılmasın
- [ ] HAYIR - İstisna KDV %0 ile kaydet

---

### 5. SGK, KONAKLAMA VERGİSİ

**SGK Tevkifatı (%50):**
```
SATIR 1: 770.12345  10,000.00  Kira bedeli
SATIR 2: 191.20.001  2,000.00  KDV %20
SATIR 3: 360.01.001  0.00       1,000.00  KDV Tevkifat %50
SATIR 4: 320.12345  0.00       11,000.00
```

**Konaklama Vergisi (%2):**
```
SATIR 1: 770.12345  10,000.00  Konaklama
SATIR 2: 191.20.001  2,000.00  KDV %20
SATIR 3: 369.XX.XXX  200.00     Konaklama Vergisi %2
SATIR 4: 320.12345  0.00       12,200.00
```

**Sizin Düzenlemeniz:** SGK/Konaklama kayıt yöntemi doğru mu?
- [ ] EVET
- [x ] HAYIR (Açıklayın): SATIR 3: 740.00209   200.00     Konaklama Vergisi %2

---

### 6. FARKLI KDV ORANLARI TEK FATURADA

**Örnek:** %20 hizmet + %8 yiyecek

```
SATIR 1: 740.12345  10,000.00  Hizmet %20 KDV
SATIR 2: 191.20.001  2,000.00  KDV %20
SATIR 3: 740.56789   5,000.00  Yiyecek %8 KDV
SATIR 4: 191.08.001    400.00  KDV %8
SATIR 5: 320.12345  0.00       17,400.00
```

**Sizin Düzenlemeniz:** Her KDV oranı için ayrı 191 hesabı açılsın mı?
- [X] EVET - 191.20.001, 191.08.001 ayrı ayrı
- [ ] HAYIR - Tek 191 hesabı kullan

---
### 7. ÖZEL İLETİŞİ VERGİSİ (ÖZELLİKLE TURKCELL FATURALARI)

**Örnek:** %20 hizmet + %8 yiyecek



SATIR1: 770.00015 	538,46	Tarife Ve Paket Ücretleri
SATIR2: 191.00001 	107,69	Gerçek Usulde Katma Değer Vergisi %20
SATIR3: 689.00001 	53,85	5035 Sayılı Kanuna Göre Özel İletişim Vergisi
SATIR4: 689.00005 	14,94	Telsiz Kullanım Ücreti
SATIR5: 689.00005 	81,00	Tahsilatına Aracılık Edilen Ödemeleriniz
SATIR6: 679.00001	0,004	Düzeltmeler	( YADA 659.00003 KULLANILACAK EĞER FARK POZİTİF İSE, BORÇ - ALACAK TOPLAMI VERİYOR BU DEĞERİ)
SATIR7: 320.12345 	0,00	795,90	Ödenecek tutar

## ✅ KONTROL LİSTESİ

Aşağıdaki kararları verin ve işaretleyin:

- [DETAYLI] **191 Hesap Yapısı:** Detaylı (191.XX.XXX) mi yoksa basit (191.00001) mi?
- [TOPLU ] **Çoklu Satır:** Ayrı KDV satırları mı yoksa toplu mu?
- [ONAYLANDI] **Tevkifat Hesaplama:** Formül onaylandı mı?
- [HAYIR YAZDIĞIM GİBİ] **İade Faturası:** BORÇ/ALACAK ters çevirme onaylandı mı?
- [AÇILMASIN] **İstisna:** KDV satırı açılmasın mı?
- [770 VEYA 740 LI HESAP Sigorta Kamu ve Finasman Giderleri KULLANILACAK] **SGK/Konaklama:** Kayıt yöntemi onaylandı mı?
- [EVET] **Farklı KDV:** Her oran için ayrı 191 mi?
- [EVET] **Evrak Türleri:** Yeni 3 sütunlu sistem kullanılacak mı?

---

## 📝 NOTLAR

**Bu şablon doldurulduktan sonra:**
1. Backend'de otomatik transaction_lines oluşturma kodu yazılacak
2. Frontend'de kategorilere göre dinamik hesap seçimi geliştirilecek
3. 191 hesapları yeniden yapılandırılacak
4. Evrak türleri database'e migration ile yüklenecek

**Sorular için:** Şablonu doldurup geri gönderin.
