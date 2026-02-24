# PayrollCalculation Kullanım Haritası

## Dosya Kullanım Özeti

```
PAYROLL_CALCULATION TABLOSU KULLANIM YERLERİ
============================================

📁 Backend (Python)
├─ 📄 app/models/payroll_calculation.py
│  └─ Model tanımı (60 kolon)
│
├─ 📄 app/domains/personnel/bordro_calculation/service.py
│  ├─ calculate() → PayrollCalculation YAZAR
│  │   ├─ MAAŞ1_* ← Luca Bordro
│  │   └─ MAAŞ2_* ← Hesaplama
│  └─ list_calculations() → PayrollCalculation OKUR
│      └─ Tüm kolonları döndürür
│
├─ 📄 app/domains/personnel/bordro_calculation/router.py
│  ├─ GET /list → PayrollCalculation OKUR
│  │   └─ MAAŞ1_* kolonları frontend'e gönderilir
│  ├─ GET /puantaj-data → PayrollCalculation KULLANMAZ ⚠️
│  │   └─ Real-time hesaplama yapar
│  └─ GET /maas-hesabi-data → PayrollCalculation KULLANMAZ ⚠️
│      └─ Real-time hesaplama yapar
│
└─ 📄 app/domains/personnel/bordro_calculation/yevmiye_service_bordro.py
   ├─ create_yevmiye() → PayrollCalculation KULLANMAZ ❌
   │   ├─ Luca'dan DOĞRUDAN okur
   │   ├─ Draft'tan DOĞRUDAN okur
   │   └─ Sadece transaction_id YAZAR
   └─ preview_yevmiye() → PayrollCalculation KULLANMAZ ❌
       └─ Luca + Draft'tan hesaplama yapar

📁 Frontend (TypeScript)
├─ 📄 src/domains/personnel/payroll/types/payroll.types.ts
│  └─ PayrollCalculation interface tanımı
│
└─ 📄 src/domains/personnel/payroll/api/payroll.api.ts
   └─ API çağrıları (backend router'dan veri alır)
```

---

## Kolon Kullanım Detayı

### MAAŞ1 Kolonları (11 adet)

| Kolon | Service.py | Router.py | Yevmiye.py | Kullanım |
|-------|-----------|-----------|-----------|----------|
| `maas1_net_odenen` | ✅ YAZAR | ✅ OKUR | ❌ | Luca'dan |
| `maas1_icra` | ✅ YAZAR | ❌ | ❌ | Luca'dan |
| `maas1_bes` | ✅ YAZAR | ❌ | ❌ | Luca'dan |
| `maas1_avans` | ✅ YAZAR | ❌ | ❌ | Luca'dan |
| `maas1_gelir_vergisi` | ✅ YAZAR | ✅ OKUR | ❌ | Luca'dan |
| `maas1_damga_vergisi` | ✅ YAZAR | ✅ OKUR | ❌ | Luca'dan |
| `maas1_ssk_isci` | ✅ YAZAR | ✅ OKUR | ❌ | Luca'dan |
| `maas1_issizlik_isci` | ✅ YAZAR | ✅ OKUR | ❌ | Luca'dan |
| `maas1_ssk_isveren` | ✅ YAZAR | ✅ OKUR | ❌ | Luca'dan |
| `maas1_issizlik_isveren` | ✅ YAZAR | ✅ OKUR | ❌ | Luca'dan |
| `maas1_ssk_tesviki` | ✅ YAZAR | ❌ | ❌ | Luca'dan |

**SONUÇ:** MAAŞ1 kolonları router'da kullanılıyor (frontend'e gönderiliyor) ama YEVMİYE OLUŞTURMADA KULLANILMIYOR! ❌

---

### MAAŞ2 Kolonları (13 adet)

| Kolon | Service.py | Router.py | Yevmiye.py | Kullanım |
|-------|-----------|-----------|-----------|----------|
| `maas2_anlaşilan` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_normal_calismasi` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_hafta_tatili` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_fm_calismasi` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_resmi_tatil` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_tatil_calismasi` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_yillik_izin` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_yol` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_prim` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_ikramiye` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_bayram` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_kira` | ✅ YAZAR | ❌ | ❌ | Hesaplama |
| `maas2_toplam` | ✅ YAZAR | ❌ | ❌ | Hesaplama |

**SONUÇ:** MAAŞ2 kolonları SADECE YAZILIYOR, HİÇ KULLANILMIYOR! ❌❌❌

---

## Veri Akışı Diyagramı

```
┌─────────────────────────────────────────────────────────────────┐
│                    BORDRO HESAPLAMA AKIŞI                        │
└─────────────────────────────────────────────────────────────────┘

1️⃣  HESAPLAMA AŞAMASI
    
    [Luca Bordro]    [Contract]    [Puantaj Grid]
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
          ┌──────────────────────────┐
          │ BordroCalculationService │
          │   calculate()            │
          └──────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────┐
          │  PayrollCalculation      │
          │  ├─ MAAŞ1_* ✅          │
          │  └─ MAAŞ2_* ✅          │
          └──────────────────────────┘

2️⃣  LİSTELEME AŞAMASI
    
    [GET /list]
         │
         ▼
    ┌──────────────────────────┐
    │ BordroRouter             │
    │ list_calculations()      │
    └──────────────────────────┘
         │
         ▼
    [PayrollCalculation OKUR]
         │
         ├─ MAAŞ1_* → Frontend ✅
         └─ MAAŞ2_* → UNUSED ❌

3️⃣  YEVMİYE OLUŞTURMA AŞAMASI
    
    [POST /yevmiye]
         │
         ▼
    ┌──────────────────────────┐
    │ BordroYevmiyeService     │
    │ create_yevmiye()         │
    └──────────────────────────┘
         │
         ├─────────────────┬──────────────┐
         │                 │              │
         ▼                 ▼              ▼
    [Luca Bordro]   [Draft Contract]  [PayrollCalculation]
    DOĞRUDAN OKUR   DOĞRUDAN OKUR     SADECE transaction_id
         ✅              ✅            YAZAR ❌
                                      
    ❌ MAAŞ1_* KULLANILMIYOR!
    ❌ MAAŞ2_* KULLANILMIYOR!
    
    SORUN: PayrollCalculation'daki hesaplanmış 
           tutarlar yevmiye oluştururken kullanılmıyor!
```

---

## Kritik Bulgular

### ❌ SORUN 1: Çift Hesaplama
```python
# HESAPLAMA 1: Bordro Calculate
service.calculate()
├─ Puantaj'dan normal_gun = 30
├─ Hesapla: 30 × gunluk_ucret = 170,000 TL
└─ PayrollCalculation.maas2_toplam = 170,000 TL YAZAR ✅

# HESAPLAMA 2: Yevmiye Oluşturma
yevmiye_service.create_yevmiye()
├─ PayrollCalculation.maas2_toplam OKUMAZ ❌
├─ Draft Contract'tan YENİDEN hesaplar:
│   └─ Puantaj'dan normal_gun = 23 (ESKI VERİ!)
│   └─ 23 × gunluk_ucret = 130,000 TL ❌
└─ Yanlış tutar yevmiyeye gider!
```

### ❌ SORUN 2: Veri Senkronizasyonu Yok
```python
# Senaryo:
1. Bordro hesapla → PayrollCalculation güncellendi ✅
2. Puantaj değişti → PayrollCalculation GÜNCELLENMEDİ ❌
3. Yevmiye oluştur → PayrollCalculation'dan OKUMAZ ❌
4. Sonuç: ESKİ verilerle yevmiye oluşturulur!
```

### ❌ SORUN 3: Gereksiz Kolonlar
```
60 kolon var, sadece 35 tanesi kullanılıyor
24 kolon (MAAŞ1_* + MAAŞ2_*) YAZILIYOR ama OKUNMUYOR!
```

---

## Çözüm Önerisi Özeti

### HIZLI ÇÖZÜM (1 gün) - ÖNERİLEN
```python
# yevmiye_service_bordro.py değişikliği

def _create_taslak_kayit_preview_combined(...):
    # ŞU AN:
    # draft_contract'tan hesaplama yapıyor
    
    # YENİ KOD:
    calc = db.query(PayrollCalculation).filter(
        PayrollCalculation.personnel_id == personnel.id,
        PayrollCalculation.yil == yil,
        PayrollCalculation.ay == ay,
        PayrollCalculation.yevmiye_tipi == "TASLAK"
    ).first()
    
    if calc:
        # HESAPLANMIŞ TUTARLARI KULLAN!
        elden_ucret = calc.elden_ucret_yuvarlanmis
        maas2_toplam = calc.maas2_toplam
    else:
        # Fallback: calculate()
```

### UZUN VADELİ ÇÖZÜM (6 gün)
1. Tablo yapısını refactor et
2. MAAŞ1/MAAŞ2 kolonlarını kaldır
3. Yeni kolon yapısı:
   - `luca_*` (Luca Bordro verileri)
   - `hesap_335_*` (Hesaplanan tutarlar)
   - `draft_*` (Draft contract bilgileri)

---

**SONUÇ:** PayrollCalculation tablosu hesaplama yapıyor ama yevmiye oluştururken kullanılmıyor. Bu yüzden Kenan Çalışkan'ın yevmiyesi güncellenmiyor!
