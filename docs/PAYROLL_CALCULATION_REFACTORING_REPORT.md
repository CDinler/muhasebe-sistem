# PayrollCalculation Tablosu Refactoring Raporu

**Tarih:** 20 Ocak 2026  
**Analiz Eden:** AI Agent  
**Konu:** PayrollCalculation tablosu yapısı ve kullanımı analizi

---

## 1. PROBLEM TESPİTİ

### 1.1. Ana Sorun
PayrollCalculation tablosu **ESKİ SİSTEM** yapısında tasarlanmış:
- **MAAŞ1**: Luca Bordro'dan gelen veriler (brüt, kesintiler, net)
- **MAAŞ2**: Sözleşmede anlaşılan ücret hesaplamaları (normal çalışma, FM, tatil vs.)

Ancak **YENİ SİSTEM**de:
- **RESMİ KAYIT** (Luca Bordro): Brüt maaş, SSK, vergiler → Tüm personel için
- **TASLAK KAYIT** (Draft Contract): Elden ödeme → SADECE draft sözleşmesi olanlar için

### 1.2. Neden Sorunlu?

```
ESKİ SİSTEM MİMARİSİ:
┌─────────────────────────┐
│ PayrollCalculation      │
├─────────────────────────┤
│ maas1_* (11 kolon)      │ ← Luca Bordro
│ maas2_* (13 kolon)      │ ← Sözleşme Hesaplama
│ yevmiye_tipi: A/B/C     │ ← 3 tip kayıt
└─────────────────────────┘

YENİ SİSTEM İHTİYACI:
┌─────────────────────────┐
│ PayrollCalculation      │
├─────────────────────────┤
│ LUCA VERİLERİ           │ ← Brüt, kesintiler, net
│ PUANTAJ VERİLERİ        │ ← Normal gün, FM saat, tatil
│ HESAPLANAN TUTARLAR     │ ← 335 hesapları
│ yevmiye_tipi:           │
│   - RESMİ (tüm personel)│
│   - TASLAK (draft olanlar)│
└─────────────────────────┘
```

---

## 2. TABLO YAPISI ANALİZİ

### 2.1. Mevcut Kolonlar (60 adet)

#### A. KULLANILAN KOLONLAR ✅

**Dönem Bilgileri (3)**
- `yil`, `ay`, `donem` → Aktif kullanımda

**Personel Bilgileri (6)**
- `personnel_id`, `contract_id`, `luca_bordro_id`, `puantaj_id`, `tckn`, `adi_soyadi` → Aktif

**Ücret Tipi (4)**
- `cost_center_id`, `santiye_adi`, `ucret_nevi`, `kanun_tipi` → Aktif

**Puantaj Detayları (5)**
- `normal_gun`, `hafta_tatili_gun`, `fazla_mesai_saat`, `tatil_mesai_gun`, `yillik_izin_gun` → Aktif

**Elden Ödeme (4)**
- `elden_ucret_ham`, `elden_ucret_yuvarlanmis`, `elden_yuvarlama`, `elden_yuvarlama_yon` → Aktif

**Yevmiye Bilgileri (4)**
- `account_code_335`, `yevmiye_tipi`, `transaction_id`, `fis_no` → Aktif

**Durum Bilgileri (9)**
- `is_approved`, `is_exported`, `has_error`, `error_message`, `notes`, `created_at`, `updated_at`, `calculated_by`, `approved_by` → Aktif

**TOPLAM KULLANILAN: 35 kolon**

---

#### B. ESKİ SİSTEM KOLONLARI (Refactor Gerekli) ⚠️

**MAAŞ1 (Luca Bordro) - 11 kolon**
```python
maas1_net_odenen        # Luca'dan gelen net ödenen
maas1_icra              # İcra kesintisi
maas1_bes               # BES kesintisi
maas1_avans             # Avans kesintisi
maas1_gelir_vergisi     # Gelir vergisi
maas1_damga_vergisi     # Damga vergisi
maas1_ssk_isci          # SSK işçi payı
maas1_issizlik_isci     # İşsizlik işçi payı
maas1_ssk_isveren       # SSK işveren payı
maas1_issizlik_isveren  # İşsizlik işveren payı
maas1_ssk_tesviki       # SSK teşviki
```

**MAAŞ2 (Sözleşme Hesaplama) - 13 kolon**
```python
maas2_anlaşilan         # Sözleşmedeki ücret
maas2_normal_calismasi  # Normal çalışma ücreti
maas2_hafta_tatili      # Hafta tatili ücreti
maas2_fm_calismasi      # Fazla mesai ücreti
maas2_resmi_tatil       # Resmi tatil ücreti
maas2_tatil_calismasi   # Tatil çalışması ücreti
maas2_yillik_izin       # Yıllık izin ücreti
maas2_yol               # Yol parası
maas2_prim              # Prim
maas2_ikramiye          # İkramiye
maas2_bayram            # Bayram harçlığı
maas2_kira              # Kira yardımı
maas2_toplam            # TOPLAM
```

**TOPLAM ESKİ SİSTEM: 24 kolon**

---

### 2.2. VERİ KULLANIM DURUMU (2025-11)

```
Toplam Kayıt: 370
├─ RESMİ KAYIT: 205 (Luca Bordro)
└─ TASLAK KAYIT: 165 (Draft Contract)

Kullanım İstatistikleri:
├─ MAAŞ1 (Luca) kullanımı: 293 kayıt
├─ MAAŞ2 (Sözleşme) kullanımı: 164 kayıt  
└─ ELDEN ödeme kullanımı: 152 kayıt
```

**Analiz:**
- ✅ MAAŞ1 kolonları hala kullanılıyor (Luca'dan gelen veriler)
- ✅ MAAŞ2 kolonları kullanılıyor (sözleşme hesaplamaları)
- ⚠️ Ancak yevmiye servisi bu verileri KULLANMIYOR!

---

## 3. PAYROLL_CALCULATION KULLANIM YERLERİ

### 3.1. Backend Kullanımları

#### A. Bordro Calculation Service (`service.py`)
```python
KULLANIM: PayrollCalculation kaydı oluşturma/güncelleme
NE YAPIYOR:
- Luca Bordro + Contract + Puantaj → PayrollCalculation
- MAAŞ1 alanlarını Luca'dan doldurur
- MAAŞ2 alanlarını sözleşme hesaplamalarından doldurur
- Elden ödeme hesaplar (draft contract varsa)

KRİTİK: Bu servis hesaplama yapar ve tabloya yazar
```

**Dosya:** `backend/app/domains/personnel/bordro_calculation/service.py`
- Satır 184-201: PayrollCalculation oluşturma
- Satır 233-267: Liste gösterimi (tüm MAAŞ1/MAAŞ2 alanları döndürülür)

---

#### B. Bordro Router (`router.py`)
```python
KULLANIM: Bordro listesi döndürme
NE YAPIYOR:
- PayrollCalculation tablosundan tüm kayıtları okur
- MAAŞ1 alanlarını API'ye döndürür
- Frontend'de gösterilir

ENDPOINTLER:
- GET /list → Tüm bordro kayıtları
- GET /puantaj-data → Puantaj preview (MAAŞ2 kullanmıyor!)
- GET /maas-hesabi-data → Maaş hesabı preview (MAAŞ2 kullanmıyor!)
```

**Dosya:** `backend/app/domains/personnel/bordro_calculation/router.py`
- Satır 134-196: Bordro listesi (MAAŞ1 alanları kullanılır)
- Satır 510-527: Puantaj data (real-time hesaplama, tablo okumuyor)
- Satır 660-677: Maaş hesabı (real-time hesaplama, tablo okumuyor)

**ÖNEMLİ:** Router'daki preview endpoint'leri PayrollCalculation'ı KULLANMIYOR!

---

#### C. Yevmiye Service (`yevmiye_service_bordro.py`)
```python
⚠️ KRİTİK: MAAŞ1/MAAŞ2 KOLONLARINI KULLANMIYOR!

KULLANIM: PayrollCalculation transaction_id güncellemesi
NE YAPIYOR:
- RESMİ KAYIT oluştururken Luca Bordro'dan okur
- TASLAK KAYIT oluştururken Draft Contract'tan okur
- PayrollCalculation'a SADECE transaction_id yazar
- MAAŞ1/MAAŞ2 tutarlarını KULLANMIYOR!

KÖK SORUN: Bu yüzden yevmiye güncellenmiyor!
```

**Dosya:** `backend/app/domains/personnel/bordro_calculation/yevmiye_service_bordro.py`
- Satır 207-229: PayrollCalculation.transaction_id güncelleme (sadece)
- Satır 516-519: PayrollCalculation.luca_bordro_id ile query
- Satır 740-745: Draft contract'tan hesaplama (MAAŞ2 değil!)
- Satır 842-846: PayrollCalculation.yevmiye_tipi query

---

### 3.2. Veri Akışı Analizi

```
MEVCUT AKIŞ (SORUNLU):

1. BORDRO HESAPLAMA
   ↓
   BordroCalculationService.calculate()
   ├─ Luca Bordro okur
   ├─ Contract okur
   ├─ Puantaj Grid okur
   └─ PayrollCalculation tablosuna YAZAR
       ├─ MAAŞ1_* ← Luca'dan
       └─ MAAŞ2_* ← Hesaplamadan

2. YEVMİYE OLUŞTURMA
   ↓
   BordroYevmiyeService.create_yevmiye()
   ├─ Luca Bordro okur (DOĞRUDAN) ✅
   ├─ Draft Contract okur (DOĞRUDAN) ✅
   ├─ PayrollCalculation OKUMAZ ❌
   └─ Transaction oluşturur
       └─ PayrollCalculation.transaction_id YAZAR

SORUN: Yevmiye servisi PayrollCalculation'daki
       MAAŞ2_* verilerini kullanmıyor!
```

---

## 4. YENİ SİSTEM MİMARİSİ ÖNERİSİ

### 4.1. PayrollCalculation Yeniden Yapılandırma

#### AMAÇ
1. Tablo yapısını yeni sisteme uyarla
2. MAAŞ1/MAAŞ2 ayrımını kaldır
3. Draft sözleşme mantığına göre yeniden düzenle

#### ÖNERİLEN TABLO YAPISI

```sql
-- ESKİ KOLONLAR (Kaldırılacak veya yeniden adlandırılacak)
DROP COLUMN maas1_net_odenen;
DROP COLUMN maas1_icra;
DROP COLUMN maas1_bes;
DROP COLUMN maas1_avans;
DROP COLUMN maas1_gelir_vergisi;
DROP COLUMN maas1_damga_vergisi;
DROP COLUMN maas1_ssk_isci;
DROP COLUMN maas1_issizlik_isci;
DROP COLUMN maas1_ssk_isveren;
DROP COLUMN maas1_issizlik_isveren;
DROP COLUMN maas1_ssk_tesviki;

DROP COLUMN maas2_anlaşilan;
DROP COLUMN maas2_normal_calismasi;
DROP COLUMN maas2_hafta_tatili;
DROP COLUMN maas2_fm_calismasi;
DROP COLUMN maas2_resmi_tatil;
DROP COLUMN maas2_tatil_calismasi;
DROP COLUMN maas2_yillik_izin;
DROP COLUMN maas2_yol;
DROP COLUMN maas2_prim;
DROP COLUMN maas2_ikramiye;
DROP COLUMN maas2_bayram;
DROP COLUMN maas2_kira;
DROP COLUMN maas2_toplam;

-- YENİ KOLONLAR (Eklenecek)

-- LUCA BORDRO VERİLERİ (Tüm personel için)
luca_brut_ucret          DECIMAL(18,2)  -- Brüt ücret
luca_gelir_vergisi       DECIMAL(18,2)  -- Gelir vergisi
luca_damga_vergisi       DECIMAL(18,2)  -- Damga vergisi
luca_ssk_isci            DECIMAL(18,2)  -- SSK işçi
luca_issizlik_isci       DECIMAL(18,2)  -- İşsizlik işçi
luca_ssk_isveren         DECIMAL(18,2)  -- SSK işveren
luca_issizlik_isveren    DECIMAL(18,2)  -- İşsizlik işveren
luca_ssk_tesviki         DECIMAL(18,2)  -- SSK teşviki
luca_icra                DECIMAL(18,2)  -- İcra kesintisi
luca_bes                 DECIMAL(18,2)  -- BES
luca_avans               DECIMAL(18,2)  -- Avans
luca_net_odenen          DECIMAL(18,2)  -- Net ödenen

-- HESAPLANAN TUTARLAR (335.xxxxx hesapları)
hesap_335_normal         DECIMAL(18,2)  -- 335.1305 Normal Çalışma
hesap_335_hafta_tatil    DECIMAL(18,2)  -- 335.1310 Hafta Tatili
hesap_335_fm             DECIMAL(18,2)  -- 335.1320 Fazla Mesai
hesap_335_resmi_tatil    DECIMAL(18,2)  -- 335.1330 Resmi Tatil
hesap_335_tatil          DECIMAL(18,2)  -- 335.1340 Tatil Çalışması
hesap_335_yillik_izin    DECIMAL(18,2)  -- 335.1350 Yıllık İzin
hesap_335_yol            DECIMAL(18,2)  -- 335.1360 Yol
hesap_335_prim           DECIMAL(18,2)  -- 335.1370 Prim
hesap_335_ikramiye       DECIMAL(18,2)  -- 335.1380 İkramiye
hesap_335_bayram         DECIMAL(18,2)  -- 335.1390 Bayram
hesap_335_kira           DECIMAL(18,2)  -- 335.1400 Kira
hesap_335_toplam         DECIMAL(18,2)  -- TOPLAM 335 hesapları

-- DRAFT CONTRACT BİLGİLERİ (Sadece draft olanlar için)
draft_contract_id        INT            -- Draft sözleşme ID
draft_net_ucret          DECIMAL(18,2)  -- Draft'taki net ücret
draft_gunluk_ucret       DECIMAL(18,2)  -- Günlük ücret (hesaplanan)

-- YEVMİYE TİPİ (Sadece 2 tip!)
yevmiye_tipi             VARCHAR(10)    -- RESMİ / TASLAK
```

---

### 4.2. Veri Dönüşüm Stratejisi

#### ADIM 1: Yeni Kolonları Ekle
```sql
ALTER TABLE payroll_calculations
ADD COLUMN luca_brut_ucret DECIMAL(18,2),
ADD COLUMN luca_gelir_vergisi DECIMAL(18,2),
-- ... (tüm yeni kolonlar)
ADD COLUMN hesap_335_normal DECIMAL(18,2),
-- ... (tüm 335 hesapları)
ADD COLUMN draft_contract_id INT,
ADD COLUMN draft_net_ucret DECIMAL(18,2);
```

#### ADIM 2: Mevcut Verileri Taşı
```sql
-- MAAŞ1 → LUCA kolonlarına
UPDATE payroll_calculations SET
    luca_brut_ucret = maas1_net_odenen + maas1_gelir_vergisi + 
                      maas1_damga_vergisi + maas1_ssk_isci + 
                      maas1_issizlik_isci,
    luca_gelir_vergisi = maas1_gelir_vergisi,
    luca_damga_vergisi = maas1_damga_vergisi,
    luca_ssk_isci = maas1_ssk_isci,
    luca_issizlik_isci = maas1_issizlik_isci,
    luca_ssk_isveren = maas1_ssk_isveren,
    luca_issizlik_isveren = maas1_issizlik_isveren,
    luca_ssk_tesviki = maas1_ssk_tesviki,
    luca_icra = maas1_icra,
    luca_bes = maas1_bes,
    luca_avans = maas1_avans,
    luca_net_odenen = maas1_net_odenen;

-- MAAŞ2 → HESAP_335 kolonlarına
UPDATE payroll_calculations SET
    hesap_335_normal = maas2_normal_calismasi,
    hesap_335_hafta_tatil = maas2_hafta_tatili,
    hesap_335_fm = maas2_fm_calismasi,
    hesap_335_resmi_tatil = maas2_resmi_tatil,
    hesap_335_tatil = maas2_tatil_calismasi,
    hesap_335_yillik_izin = maas2_yillik_izin,
    hesap_335_yol = maas2_yol,
    hesap_335_prim = maas2_prim,
    hesap_335_ikramiye = maas2_ikramiye,
    hesap_335_bayram = maas2_bayram,
    hesap_335_kira = maas2_kira,
    hesap_335_toplam = maas2_toplam;

-- Draft Contract bilgilerini doldur
UPDATE payroll_calculations pc
JOIN personnel_draft_contracts pdc ON pc.personnel_id = pdc.personnel_id
SET 
    pc.draft_contract_id = pdc.id,
    pc.draft_net_ucret = pdc.net_ucret,
    pc.draft_gunluk_ucret = CASE 
        WHEN pdc.odeme_sekli = 'aylik' THEN pdc.net_ucret / 30
        ELSE pdc.net_ucret
    END
WHERE pdc.is_active = 1;
```

#### ADIM 3: Eski Kolonları Kaldır
```sql
ALTER TABLE payroll_calculations
DROP COLUMN maas1_net_odenen,
DROP COLUMN maas1_icra,
-- ... (tüm MAAŞ1 kolonları)
DROP COLUMN maas2_anlaşilan,
DROP COLUMN maas2_normal_calismasi,
-- ... (tüm MAAŞ2 kolonları)
```

---

### 4.3. Kod Değişiklikleri

#### A. BordroCalculationService Güncelleme

**service.py değişiklik:**
```python
def _calculate_bordro(...):
    return {
        # Dönem
        "yil": yil,
        "ay": ay,
        "donem": donem,
        
        # Personel
        "personnel_id": personnel.id,
        "tckn": personnel.tc_kimlik_no,
        "adi_soyadi": personnel.ad_soyad,
        "contract_id": contract.id if contract else None,
        "luca_bordro_id": luca.id,
        
        # LUCA VERİLERİ (eski maas1_*)
        "luca_brut_ucret": luca.brut,
        "luca_gelir_vergisi": luca.gelir_vergisi,
        "luca_damga_vergisi": luca.damga_vergisi,
        "luca_ssk_isci": luca.ssk_isci,
        "luca_issizlik_isci": luca.issizlik_isci,
        "luca_ssk_isveren": luca.ssk_isveren,
        "luca_issizlik_isveren": luca.issizlik_isveren,
        "luca_net_odenen": luca.net_odenen,
        
        # 335 HESAPLARI (eski maas2_*)
        "hesap_335_normal": ppg_normal_calismasi * tr_gunluk_ucret,
        "hesap_335_hafta_tatil": ppg_hafta_tatili * tr_gunluk_ucret,
        "hesap_335_fm": ppg_fm_saat * tr_fm_ucret,
        "hesap_335_toplam": maas2_toplam,
        
        # DRAFT CONTRACT
        "draft_contract_id": draft_contract.id if draft_contract else None,
        "draft_net_ucret": draft_contract.net_ucret if draft_contract else None,
        "draft_gunluk_ucret": gunluk_ucret if draft_contract else None,
        
        # ELDEN ÖDEME (sadece draft olanlar)
        "elden_ucret_ham": elden_ham if draft_contract else 0,
        "elden_ucret_yuvarlanmis": elden_yuv if draft_contract else 0,
        
        # YEVMİYE TİPİ
        "yevmiye_tipi": "TASLAK" if draft_contract else "RESMİ"
    }
```

---

#### B. Yevmiye Service Güncelleme

**yevmiye_service_bordro.py değişiklik:**

**ŞU ANKİ KOD (SORUNLU):**
```python
# Yevmiye servisi PayrollCalculation'dan SADECE transaction_id alıyor
# Tutarları Luca ve Draft'tan tekrar hesaplıyor
def create_yevmiye(...):
    # Luca'dan oku
    luca = get_luca_bordro(...)
    brut = luca.brut
    
    # Draft'tan oku
    draft = get_draft_contract(...)
    elden = calculate_elden(draft, ...)
    
    # Transaction oluştur
    # PayrollCalculation'daki hesaplanmış tutarları KULLANMIYOR!
```

**YENİ KOD (ÇÖZÜM):**
```python
def create_yevmiye(personnel_id, yil, ay):
    """
    PayrollCalculation'dan hesaplanmış tutarları AL!
    Tekrar hesaplama YAPMA!
    """
    # PayrollCalculation kayıtlarını getir
    payroll_calcs = db.query(PayrollCalculation).filter(
        PayrollCalculation.personnel_id == personnel_id,
        PayrollCalculation.yil == yil,
        PayrollCalculation.ay == ay
    ).all()
    
    for calc in payroll_calcs:
        if calc.yevmiye_tipi == "RESMİ":
            # RESMİ KAYIT (Luca Bordro)
            lines = []
            
            # BORÇ: 335 Hesapları (hesaplanmış tutarlar)
            if calc.hesap_335_normal > 0:
                lines.append({
                    "account_code": "335.1305",
                    "debit": calc.hesap_335_normal,
                    "credit": 0
                })
            
            if calc.hesap_335_hafta_tatil > 0:
                lines.append({
                    "account_code": "335.1310",
                    "debit": calc.hesap_335_hafta_tatil,
                    "credit": 0
                })
            
            # ... (diğer 335 hesapları)
            
            # ALACAK: Kesintiler ve Net Ödeme
            lines.append({
                "account_code": "360.xx.xx",  # Gelir Vergisi
                "debit": 0,
                "credit": calc.luca_gelir_vergisi
            })
            
            lines.append({
                "account_code": "361.xx.xx",  # Damga Vergisi
                "debit": 0,
                "credit": calc.luca_damga_vergisi
            })
            
            lines.append({
                "account_code": "335.xx.xx",  # Net Ödenen
                "debit": 0,
                "credit": calc.luca_net_odenen
            })
            
            # Transaction oluştur
            transaction = create_transaction(lines)
            
            # PayrollCalculation'ı güncelle
            calc.transaction_id = transaction.id
            calc.fis_no = transaction.transaction_number
            
        elif calc.yevmiye_tipi == "TASLAK":
            # TASLAK KAYIT (Draft Contract - Elden Ödeme)
            lines = []
            
            # BORÇ: 335 Maliyet (elden ödenen kısım)
            lines.append({
                "account_code": calc.account_code_335,
                "debit": calc.elden_ucret_yuvarlanmis,
                "credit": 0
            })
            
            # ALACAK: Kasa (elden ödenen)
            lines.append({
                "account_code": "100.01.01",  # Kasa
                "debit": 0,
                "credit": calc.elden_ucret_yuvarlanmis
            })
            
            # Transaction oluştur
            transaction = create_transaction(lines)
            
            # PayrollCalculation'ı güncelle
            calc.transaction_id = transaction.id
            calc.fis_no = transaction.transaction_number
    
    db.commit()
```

---

## 5. UYGULAMA PLANI

### PHASE 1: Analiz ve Hazırlık (1 gün)
- [x] Mevcut tablo yapısını analiz et
- [x] Kullanım yerlerini tespit et
- [x] Veri akışını haritalandır
- [ ] Migration scripti hazırla
- [ ] Test verisi oluştur

### PHASE 2: Veritabanı Değişiklikleri (1 gün)
- [ ] Yeni kolonları ekle
- [ ] Mevcut verileri taşı
- [ ] Eski kolonları yedekle (DROP ETME!)
- [ ] Index'leri güncelle

### PHASE 3: Backend Kod Güncellemeleri (2 gün)
- [ ] PayrollCalculation modeli güncelle
- [ ] BordroCalculationService güncelle
- [ ] BordroYevmiyeService güncelle
- [ ] Router endpoint'lerini güncelle
- [ ] Unit testler yaz

### PHASE 4: Frontend Güncellemeleri (1 gün)
- [ ] TypeScript type'ları güncelle
- [ ] API çağrılarını güncelle
- [ ] UI'da kolon isimlerini güncelle

### PHASE 5: Test ve Deployment (1 gün)
- [ ] Test ortamında çalıştır
- [ ] 2025-11 dönemini yeniden hesapla
- [ ] Yevmiye kayıtlarını kontrol et
- [ ] Production'a deploy

---

## 6. RİSK ANALİZİ

### Yüksek Riskler 🔴
1. **Veri Kaybı**: Eski kolonları DROP etmeden önce yedek al
2. **Frontend Bağımlılıkları**: Tüm frontend componentleri güncellemek gerekebilir
3. **Mevcut Yevmiye Kayıtları**: Geçmiş dönem yevmiyeleri bozulabilir

### Orta Riskler 🟡
1. **Excel Export**: Bordro Excel export'ları güncellenmeli
2. **API Bağımlılıkları**: Diğer sistemler MAAŞ1/MAAŞ2 kullanıyor olabilir
3. **Raporlar**: Mevcut bordro raporları eski kolonları kullanıyor olabilir

### Düşük Riskler 🟢
1. **Performance**: Kolon sayısı azalacağı için performans artabilir
2. **Backward Compatibility**: Migration yaparsak eski sistem çalışmaya devam eder

---

## 7. ALTERNATİF ÇÖZÜMLER

### ÇÖZÜM 1: TAM REFACTORING (Önerilen)
**Açıklama:** Tablo yapısını tamamen yeniden tasarla  
**Artıları:** Temiz mimari, bakımı kolay  
**Eksileri:** Riskli, çok iş gerektirir  
**Süre:** 6 gün

### ÇÖZÜM 2: HYBRID YAKLAŞIM (Hızlı Çözüm)
**Açıklama:** Eski kolonları koru, YevmiyeService'i düzelt  
**Artıları:** Düşük risk, hızlı  
**Eksileri:** Teknik borç kalır  
**Süre:** 1 gün

```python
# YevmiyeService değişikliği (Hybrid)
def create_yevmiye(...):
    # PayrollCalculation'dan oku
    calc = get_payroll_calculation(...)
    
    # Hesaplanmış tutarları kullan
    brut = calc.maas2_toplam  # Mevcut kolon
    elden = calc.elden_ucret_yuvarlanmis
    
    # Transaction oluştur
    # ...
```

### ÇÖZÜM 3: YENİ TABLO (En Güvenli)
**Açıklama:** Yeni tablo oluştur, eski tabloyu koru  
**Artıları:** Sıfır risk, rollback kolay  
**Eksileri:** İki tablo yönetimi  
**Süre:** 4 gün

```sql
CREATE TABLE payroll_calculations_v2 (
    -- Sadece gerekli kolonlar
    id INT PRIMARY KEY,
    personnel_id INT,
    donem VARCHAR(7),
    yevmiye_tipi VARCHAR(10),
    luca_brut DECIMAL(18,2),
    hesap_335_total DECIMAL(18,2),
    ...
);
```

---

## 8. SONUÇ VE ÖNERİ

### Ana Bulgular
1. ✅ PayrollCalculation tablosu 60 kolon, **sadece 35'i aktif kullanımda**
2. ❌ MAAŞ1/MAAŞ2 ayrımı **ESKİ SİSTEM** kalıntısı
3. ⚠️ YevmiyeService hesaplanmış tutarları **KULLANMIYOR**
4. 🔧 Tablo yapısı **yeni sisteme** uygun değil

### Öneri
**ÇÖZÜM 2: HYBRID YAKLAŞIM** ile başla:
1. YevmiyeService'i düzelt (PayrollCalculation'dan oku)
2. Kenan Çalışkan problemini çöz
3. Sistem stabil olduktan sonra TAM REFACTORING planla

### İlk Adım (Bugün)
```python
# backend/app/domains/personnel/bordro_calculation/yevmiye_service_bordro.py

def _create_taslak_kayit_preview_combined(...):
    # Şu anki kod: Draft contract'tan hesaplama yapıyor
    # Yeni kod: PayrollCalculation'dan oku!
    
    calc = db.query(PayrollCalculation).filter(
        PayrollCalculation.personnel_id == personnel.id,
        PayrollCalculation.yil == yil,
        PayrollCalculation.ay == ay,
        PayrollCalculation.yevmiye_tipi == "TASLAK"
    ).first()
    
    if calc:
        # Hesaplanmış tutarları kullan
        elden_ucret = calc.elden_ucret_yuvarlanmis
        hesap_335_toplam = calc.hesap_335_toplam
    else:
        # Fallback: Draft contract'tan hesapla
        ...
```

---

**SON NOT:** Bu refactoring **ZORUNLU** değil ama sistem büyüdükçe teknik borç artacak. En iyisi kademeli geçiş planlamak.
