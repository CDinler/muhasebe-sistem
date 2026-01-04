# Domain Mimarisi Tasarımı - Menü Tabanlı

## 📋 Mevcut Menü Yapısı Analizi

```
├── Dashboard (Ana Sayfa)
├── Muhasebe
│   ├── Fişler (Transactions)
│   ├── Muavin Defteri
│   └── Hesap Planı (Accounts)
├── Fatura Yönetimi
│   ├── Fatura Takip (E-Invoices)
│   └── Fatura Eşleştirme (Invoice Matching)
├── Cari Hesaplar (Contacts)
├── Masraf Merkezleri (Cost Centers)
├── Personel
│   ├── Personel Listesi
│   ├── Luca Entegrasyon
│   │   ├── Luca Bordrolar
│   │   └── Luca Personel Sicil Kayıtları
│   ├── Personel Sözleşmeleri
│   ├── Puantaj Takip
│   ├── Bordro Hesaplama
│   └── Sistem Ayarları
├── Raporlar
└── Ayarlar
```

## 🏗️ Önerilen Domain Yapısı

### Backend Structure
```
backend/app/
├── shared/           # Ortak altyapı (mevcut)
│   ├── database.py
│   ├── crud_base.py
│   └── exceptions.py
│
└── domains/
    ├── dashboard/
    │   ├── __init__.py
    │   ├── service.py        # Dashboard metrics
    │   └── router.py         # /api/v2/dashboard
    │
    ├── accounting/           # Muhasebe Domain
    │   ├── __init__.py
    │   ├── accounts/         # ✅ YAPILDI
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── service.py
    │   │   └── router.py
    │   ├── transactions/     # TODO: Fişler
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── service.py
    │   │   └── router.py
    │   └── ledger/          # TODO: Muavin Defteri
    │       ├── service.py
    │       └── router.py
    │
    ├── invoicing/           # Fatura Yönetimi Domain
    │   ├── __init__.py
    │   ├── einvoices/       # TODO: E-Fatura Takip
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── service.py
    │   │   └── router.py
    │   └── matching/        # TODO: Fatura Eşleştirme
    │       ├── models.py
    │       ├── service.py
    │       └── router.py
    │
    ├── partners/            # İş Ortakları Domain
    │   ├── __init__.py
    │   ├── contacts/        # TODO: Cari Hesaplar
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── service.py
    │   │   └── router.py
    │   └── cost_centers/    # TODO: Masraf Merkezleri
    │       ├── models.py
    │       ├── repository.py
    │       ├── service.py
    │       └── router.py
    │
    ├── personnel/           # Personel Domain
    │   ├── __init__.py
    │   ├── employees/       # ✅ YAPILDI (Personel Listesi)
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── service.py
    │   │   └── router.py
    │   ├── contracts/       # TODO: Sözleşmeler
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── service.py
    │   │   └── router.py
    │   ├── attendance/      # ✅ YAPILDI (Puantaj)
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── service.py
    │   │   └── router.py
    │   ├── payroll/         # TODO: Bordro Hesaplama
    │   │   ├── models.py
    │   │   ├── service.py
    │   │   └── router.py
    │   └── luca_integration/ # TODO: Luca Entegrasyon
    │       ├── bordro/
    │       │   ├── models.py
    │       │   ├── repository.py
    │       │   ├── service.py
    │       │   └── router.py
    │       └── sicil/
    │           ├── models.py
    │           ├── repository.py
    │           ├── service.py
    │           └── router.py
    │
    ├── reporting/           # Raporlar Domain
    │   ├── __init__.py
    │   ├── service.py
    │   └── router.py        # /api/v2/reports
    │
    └── settings/            # Ayarlar Domain
        ├── __init__.py
        ├── system/
        │   ├── models.py
        │   ├── repository.py
        │   ├── service.py
        │   └── router.py
        └── user/
            ├── service.py
            └── router.py
```

### Frontend Structure
```
frontend/src/
├── shared/              # Ortak altyapı (mevcut)
│   ├── api/
│   │   └── crud-service.ts
│   ├── hooks/
│   │   └── useCRUD.ts
│   └── types/
│       └── common.types.ts
│
└── domains/
    ├── dashboard/
    │   ├── api/
    │   │   └── dashboard.api.ts
    │   ├── hooks/
    │   │   └── useDashboard.ts
    │   ├── components/
    │   │   ├── MetricsCard.tsx
    │   │   └── RecentActivity.tsx
    │   └── pages/
    │       └── DashboardPage.tsx
    │
    ├── accounting/
    │   ├── accounts/        # ✅ YAPILDI
    │   │   ├── api/
    │   │   ├── hooks/
    │   │   ├── types/
    │   │   ├── components/
    │   │   └── pages/
    │   ├── transactions/    # TODO
    │   │   ├── api/
    │   │   ├── hooks/
    │   │   ├── types/
    │   │   ├── components/
    │   │   └── pages/
    │   └── ledger/         # TODO
    │       ├── api/
    │       ├── hooks/
    │       ├── types/
    │       └── pages/
    │
    ├── invoicing/
    │   ├── einvoices/      # TODO: En öncelikli
    │   │   ├── api/
    │   │   │   └── einvoice.api.ts
    │   │   ├── hooks/
    │   │   │   ├── useEInvoices.ts
    │   │   │   └── useInvoiceMatching.ts
    │   │   ├── types/
    │   │   │   └── einvoice.types.ts
    │   │   ├── components/
    │   │   │   ├── EInvoiceList.tsx
    │   │   │   ├── EInvoiceFilters.tsx
    │   │   │   ├── EInvoiceDetail.tsx
    │   │   │   └── InvoiceMatchingPanel.tsx
    │   │   └── pages/
    │   │       ├── EInvoicesPage.tsx
    │   │       └── InvoiceMatchingPage.tsx
    │   └── matching/
    │       └── ... (aynı yapı)
    │
    ├── partners/
    │   ├── contacts/       # TODO: Cari Hesaplar
    │   └── cost_centers/   # TODO: Masraf Merkezleri
    │
    ├── personnel/
    │   ├── employees/      # ✅ YAPILDI
    │   ├── contracts/      # TODO
    │   ├── attendance/     # ✅ YAPILDI (Puantaj)
    │   ├── payroll/        # TODO
    │   └── luca_integration/
    │       ├── bordro/
    │       └── sicil/
    │
    ├── reporting/
    │   └── pages/
    │       └── ReportsPage.tsx
    │
    └── settings/
        └── pages/
            └── SettingsPage.tsx
```

## 🎯 Domain'lerin İş Sorumlulukları

### 1. Dashboard Domain
- **Sorumluluk:** Özet metrikleri ve genel bakış
- **Bağımlılıklar:** Diğer tüm domain'lerden metrik toplar
- **Öncelik:** DÜŞÜK (şimdilik mevcut sayfa yeterli)

### 2. Accounting Domain (Muhasebe)
- **Sorumluluk:** Finansal kayıt ve raporlama
- **Alt Domain'ler:**
  - `accounts`: Hesap planı yönetimi ✅
  - `transactions`: Muhasebe fişleri (borç/alacak kayıtları)
  - `ledger`: Muavin defteri (hesap hareketleri raporu)
- **Öncelik:** YÜKSEK

### 3. Invoicing Domain (Fatura Yönetimi)
- **Sorumluluk:** Fatura işlemleri ve entegrasyonlar
- **Alt Domain'ler:**
  - `einvoices`: E-Fatura/E-Arşiv takip ve yönetim
  - `matching`: PDF-XML eşleştirme ve otomatik kodlama
- **Öncelik:** ÇOK YÜKSEK (en çok kullanılan özellik)

### 4. Partners Domain (İş Ortakları)
- **Sorumluluk:** Üçüncü taraf ilişkiler
- **Alt Domain'ler:**
  - `contacts`: Cari hesap (müşteri/tedarikçi) yönetimi
  - `cost_centers`: Masraf merkezi yönetimi
- **Öncelik:** ORTA

### 5. Personnel Domain (Personel)
- **Sorumluluk:** İnsan kaynakları ve bordro
- **Alt Domain'ler:**
  - `employees`: Personel listesi ✅
  - `contracts`: Sözleşme yönetimi
  - `attendance`: Puantaj takip ✅
  - `payroll`: Bordro hesaplama
  - `luca_integration/bordro`: Luca bordro entegrasyonu
  - `luca_integration/sicil`: Luca sicil entegrasyonu
- **Öncelik:** YÜKSEK

### 6. Reporting Domain (Raporlar)
- **Sorumluluk:** Çapraz domain raporlama
- **Öncelik:** DÜŞÜK (şimdilik ertelenebilir)

### 7. Settings Domain (Ayarlar)
- **Sorumluluk:** Sistem ve kullanıcı ayarları
- **Öncelik:** DÜŞÜK

## 📊 Migration Öncelik Sırası

### ⚡ Faz 1: CRITICAL (Şimdi)
1. **Invoicing/EInvoices** (2-3 saat)
   - Sebep: En çok kullanılan, açık olan sayfa
   - Dosya: `EInvoicesPage.tsx` → domain yapısına

2. **Accounting/Transactions** (2-3 saat)
   - Sebep: Muhasebe core işlem
   - Dosya: Fişler sayfası

### 🔥 Faz 2: HIGH (Yarın)
3. **Personnel/Payroll** (2 saat)
   - Sebep: Bordro hesaplama kritik
   
4. **Personnel/Luca Integration** (2 saat)
   - Sebep: Luca Bordro/Sicil mevcut sayfalarda

### 🟡 Faz 3: MEDIUM (Gelecek)
5. **Partners/Contacts** (1-2 saat)
6. **Partners/CostCenters** (1 saat)
7. **Accounting/Ledger** (1 saat)

### 🟢 Faz 4: LOW (İhtiyaç Olunca)
8. **Dashboard**
9. **Reporting**
10. **Settings**

## ✅ Şu An Yapılacak: Invoicing/EInvoices

**Adımlar:**
1. Backend: `domains/invoicing/einvoices/` oluştur
2. Frontend: `domains/invoicing/einvoices/` oluştur
3. Mevcut `EInvoicesPage.tsx` → domain yapısına taşı
4. Test et
5. Git commit

**Tahmini Süre:** 2-3 saat
**Beklenen Sonuç:** E-Fatura sayfası yeni yapıda çalışacak, kod %60 daha temiz olacak
