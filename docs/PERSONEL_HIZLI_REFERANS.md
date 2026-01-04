# 📋 PERSONEL MODÜLÜ - Hızlı Referans

## 🚀 HIZLI BAŞLANGIÇ

### 1. Yeni Personel Ekle
```python
# Backend
personnel = Personnel(
    code="P{:05d}".format(next_id),
    tckn="12345678901",
    first_name="Ahmet",
    last_name="Yılmaz",
    department="İDARİ",
    start_date=date(2025, 1, 1),
    is_active=True
)
db.add(personnel)
db.commit()

# 335.xxx hesabı otomatik oluşturulacak
```

### 2. Luca Bordro Import
```bash
# Frontend: LucaBordroPage
1. Excel dosyasını seç (Luca export)
2. Upload butonuna tıkla
3. Validasyon kontrol et
4. Import et
```

### 3. Bordro Yevmiye Oluştur
```python
# API Call
POST /api/v1/bordro-yevmiye-v2/generate
{
  "donem": "2025-12",
  "force_regenerate": false
}
```

---

## 📊 ÖNEMLİ TABLOLAR

| Tablo | Açıklama | Kayıt Sayısı |
|-------|----------|--------------|
| `personnel` | Personel kartları | 2,172 |
| `personnel_contracts` | Sözleşmeler | ~500 |
| `payroll_calculations` | Bordro kayıtları | ~4,400 (12 ay × 369) |
| `monthly_puantaj` | Puantaj | ~4,400 |
| `accounts` (335.xxx) | Personel hesapları | 2,172 |

---

## 🔑 ÖNEMLİ HESAP KODLARI

### Personel Hesapları
- **335.{tckn}** - Personel Borç/Alacak Hesabı

### Gider Hesapları
- **740.00100** - Personel Giderleri (Kalem kalem borç)

### Vergi ve SGK Hesapları
- **361.00001** - İşçi SSK Primi (Alacak)
- **361.00002** - İşveren SSK Primi (Alacak)
- **361.00003** - İşçi İşsizlik Primi (Alacak)
- **361.00004** - İşveren İşsizlik Primi (Alacak)
- **360.00004** - Gelir Vergisi (Alacak)
- **360.00005** - Damga Vergisi (Alacak)

### Kesinti Hesapları
- **369.00001** - BES Kesintisi (Alacak)
- **369.00002** - İcra Kesintisi (Alacak)
- **196** - Personel Avansları (Alacak)

### Teşvik Hesapları
- **602.00003** - SSK Teşviki (Alacak)

---

## 🔍 SIKÇA KULLANILAN SORGULAR

### Aktif Personel Listesi
```sql
SELECT p.code, p.first_name, p.last_name, p.department, a.code as account_code
FROM personnel p
LEFT JOIN accounts a ON a.id = p.account_id
WHERE p.is_active = TRUE
ORDER BY p.code;
```

### Belirli Dönemde Çalışan Personeller
```sql
SELECT p.*
FROM personnel p
WHERE p.start_date <= '2025-12-31'
  AND (p.end_date >= '2025-12-01' OR p.end_date IS NULL);
```

### Bordro Hesaplaması Olan Personeller
```sql
SELECT 
    p.first_name, 
    p.last_name,
    pc.donem,
    pc.maas1_net_odenen,
    pc.yevmiye_created
FROM personnel p
JOIN payroll_calculations pc ON pc.personnel_id = p.id
WHERE pc.donem = '2025-12'
ORDER BY p.last_name;
```

### Yevmiye Oluşturulmamış Bordrolar
```sql
SELECT donem, COUNT(*) as toplam
FROM payroll_calculations
WHERE yevmiye_created = FALSE
GROUP BY donem
ORDER BY donem DESC;
```

### Account_ID Olmayan Personeller
```sql
SELECT code, first_name, last_name, tckn
FROM personnel
WHERE account_id IS NULL
  AND is_active = TRUE;
```

---

## 🛠️ SIKÇA KULLANILAN API ÇAĞRİLARI

### Personnel API

```javascript
// Tüm personel listesi
GET /api/v1/personnel/
GET /api/v1/personnel/?is_active=true
GET /api/v1/personnel/?period=2025-12
GET /api/v1/personnel/?department=İDARİ

// Departman listesi
GET /api/v1/personnel/filters/departments

// Personel detay
GET /api/v1/personnel/{id}

// Yeni personel
POST /api/v1/personnel/
{
  "code": "P00123",
  "tckn": "12345678901",
  "first_name": "Ahmet",
  "last_name": "Yılmaz",
  "is_active": true
}

// Personel güncelle
PUT /api/v1/personnel/{id}

// Personel sil
DELETE /api/v1/personnel/{id}
```

### Bordro API

```javascript
// Luca bordro upload
POST /api/v1/luca-bordro/upload
Content-Type: multipart/form-data
file: [Excel dosyası]

// Bordro hesaplama listesi
GET /api/v1/payroll-calculations/?donem=2025-12

// Yevmiye oluştur
POST /api/v1/bordro-yevmiye-v2/generate
{
  "donem": "2025-12",
  "personnel_ids": [1, 2, 3],  // Opsiyonel
  "force_regenerate": false
}

// Yevmiye export
GET /api/v1/bordro-yevmiye-v2/export/{donem}
```

---

## 💡 İPUÇLARI VE EN İYİ PRATİKLER

### 1. Account_ID Kullanımı
```python
# ❌ ESKİ YÖNTEM (Yavaş)
account = db.query(Account)\
    .filter(Account.code == f"335.{personnel.tckn}")\
    .first()

# ✅ YENİ YÖNTEM (Hızlı)
if personnel.account_id:
    account = db.query(Account)\
        .filter(Account.id == personnel.account_id)\
        .first()
```

### 2. Dönem Filtresi
```python
# Frontend: DatePicker ile ay/yıl seç
selectedPeriod = "2025-12"

# Backend: Doğru date range hesaplama
period_start = f"{year}-{month}-01"
period_end = f"{year}-{month+1}-01"  # Dikkat: Ay sınırı

# Sorgu
query.filter(
    Personnel.start_date <= period_end,
    or_(
        Personnel.end_date >= period_start,
        Personnel.end_date.is_(None)
    )
)
```

### 3. Bordro Import Checklist
- [ ] Excel'de TC sütunu var mı?
- [ ] Tüm personeller veritabanında kayıtlı mı?
- [ ] Dönem formatı doğru mu? (YYYY-MM)
- [ ] Tutarlar numeric mi?
- [ ] Duplicate kayıt var mı?

### 4. Yevmiye Oluşturma Checklist
- [ ] Bordro hesaplamaları var mı?
- [ ] Personnel.account_id dolu mu?
- [ ] Gerekli hesap kodları mevcut mu? (740, 361, 360, 369, 196, 602)
- [ ] Yevmiye daha önce oluşturulmamış mı? (yevmiye_created=FALSE)
- [ ] Borç-Alacak dengesi tutuyor mu?

### 5. Performans İpuçları
- Büyük listelerde pagination kullan (limit=1000)
- Eager loading ile N+1 problemini önle
- Filtrelerde index'li kolonları kullan (tckn, code, donem)
- Batch işlemler için bulk_save_objects kullan

---

## ⚠️ SIKÇA KARŞILAŞILAN HATALAR

### 1. Account Bulunamadı
```
Hata: Hesap kodu bulunamadı: 335.12345678901
Çözüm: Personnel için 335.xxx hesabı oluşturulmamış
       → get_or_create_personnel_account() çalıştır
```

### 2. Duplicate Personnel
```
Hata: UNIQUE constraint failed: personnel.tckn
Çözüm: TC ile aynı personel zaten var
       → Önce kontrol et: query(Personnel).filter(tckn==...).first()
```

### 3. Yevmiye Dengesi Tutmuyor
```
Hata: Borç-Alacak dengesi tutmuyor: 25000 != 25350
Çözüm: Bordro hesaplamalarında eksik/fazla değer var
       → Luca bordro verilerini kontrol et
       → SSK, vergi, kesinti tutarlarını gözden geçir
```

### 4. Period Filter Çalışmıyor
```
Hata: Aralık ayında çalışan gösterilmiyor
Çözüm: Date range logic hatası
       → period_end = next_month 01. günü olmalı
       → end_date NULL kontrolü eklenmeli (OR end_date IS NULL)
```

### 5. Performance Problem
```
Hata: 2000+ personel listesi yavaş
Çözüm: 
  1. Pagination ekle (skip, limit)
  2. Eager loading kullan (.options(joinedload(...)))
  3. Index'leri kontrol et
  4. Frontend'de virtual scrolling
```

---

## 📝 ÖNEMLİ NOTLAR

### Ücret Nevleri
- **MAKTU_AYLIK**: Sabit aylık, puantaja bakmaz (30 gün)
- **AYLIK**: Puantaja göre aylık (çalışılan gün / 30)
- **GUNLUK**: Günlük ücret × çalışılan gün

### Kanun Tipleri
- **05510**: 4/a (SSK'lı işçi)
- **00000**: SSK'ya tabi değil
- **EMEKLI**: Emekli çalışan (farklı SSK oranları)

### Yevmiye Türleri
1. **BORDRO_LUCA**: Luca brüt bordrosu (kalem kalem borç)
2. **BORDRO_NET**: Net ücret bordrosu (BES, avans kesintisi)
3. **BORDRO_FULL**: Tam bordro (LUCA + NET birleşik)

### CSV Export Formatı
- Delimiter: `,` (virgül)
- Encoding: UTF-8
- Decimal: `.` (nokta)
- Date format: YYYY-MM-DD

---

## 🔧 BAKIM VE DESTEK

### Düzenli Kontroller (Aylık)
```sql
-- 1. Account_ID boş personel var mı?
SELECT COUNT(*) FROM personnel 
WHERE account_id IS NULL AND is_active = TRUE;

-- 2. Orphan 335 hesapları
SELECT a.* FROM accounts a
LEFT JOIN personnel p ON p.account_id = a.id
WHERE a.code LIKE '335.%' AND p.id IS NULL;

-- 3. Yevmiye oluşturulmamış bordrolar
SELECT donem, COUNT(*) FROM payroll_calculations
WHERE yevmiye_created = FALSE
GROUP BY donem;

-- 4. Duplicate TC kontrolü
SELECT tckn, COUNT(*) FROM personnel
GROUP BY tckn HAVING COUNT(*) > 1;
```

### Backup Stratejisi
```bash
# Personel tablosu backup (günlük)
mysqldump muhasebe personnel > personnel_$(date +%Y%m%d).sql

# Bordro tabloları backup (aylık)
mysqldump muhasebe \
  personnel_contracts \
  payroll_calculations \
  monthly_puantaj \
  > bordro_backup_$(date +%Y%m).sql
```

---

## 📚 DİĞER REFERANSLAR

- **Detaylı Dokümantasyon**: [PERSONEL_MODULU.md](./PERSONEL_MODULU.md)
- **Sistem Mimarisi**: [PERSONEL_SISTEM_MIMARİSİ.md](./PERSONEL_SISTEM_MIMARİSİ.md)
- **API Docs**: http://localhost:8000/docs
- **Database Schema**: [../database/schema.sql](../database/schema.sql)

---

**Son Güncelleme:** 18 Aralık 2025  
**Versiyon:** 2.0  
**Durum:** ✅ Production Ready
