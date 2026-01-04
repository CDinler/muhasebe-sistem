# 📅 TAKVİMLİ PUANTAJ SİSTEMİ

**Tarih:** 22 Aralık 2025  
**Durum:** ✅ Aktif  
**Veritabanı:** MySQL - muhasebe_sistem

---

## 📋 GENEL BAKIŞ

Luca Mali Müşavir programı ile uyumlu, günlük bazda detaylı puantaj takip sistemi. Personelin her gün için giriş-çıkış, çalışma saatleri, izin durumları ve kazançları kaydedilir.

### Temel Özellikler

- ✅ Günlük detaylı puantaj kayıtları
- ✅ Giriş-çıkış saat takibi
- ✅ Fazla mesai ve tatil çalışması
- ✅ İzin türleri yönetimi (Yıllık, Rapor, Ücretsiz, vb.)
- ✅ Vardiya tanımları
- ✅ Resmi tatil takvimi
- ✅ Otomatik aylık özetler
- ✅ İzin bakiye takibi

---

## 🗄️ VERİTABANI YAPISI

### 1. `personnel_daily_attendance` (Ana Tablo)

Günlük puantaj kayıtları - Her personel için her gün bir kayıt.

```sql
-- Örnek kayıt
INSERT INTO personnel_daily_attendance (
    personnel_id, tckn, adi_soyadi,
    attendance_date, donem, yil, ay, gun_no, gun_adi,
    gun_tipi, calisma_durumu,
    normal_saat, fazla_mesai_saat,
    gunluk_kazanc, fm_kazanc
) VALUES (
    123, '12345678901', 'Ahmet Yılmaz',
    '2025-12-22', '2025-12', 2025, 12, 22, 'Pazar',
    'PAZAR', 'TATIL',
    0, 0,
    0, 0
);
```

#### Önemli Kolonlar

| Kolon | Tip | Açıklama |
|-------|-----|----------|
| `attendance_date` | DATE | Puantaj tarihi (PK) |
| `calisma_durumu` | ENUM | CALISTI, IZINLI, RAPORLU, GELMEDI, TATIL, HAFTA_TATILI |
| `gun_tipi` | ENUM | NORMAL, CUMARTESI, PAZAR, RESMI_TATIL, DINI_BAYRAM |
| `normal_saat` | DECIMAL(5,2) | Normal mesai saati |
| `fazla_mesai_saat` | DECIMAL(5,2) | Fazla mesai saati |
| `tatil_mesai_saat` | DECIMAL(5,2) | Tatil günü çalışma |
| `yillik_izin` | DECIMAL(3,1) | Yıllık izin (0, 0.5, 1 gün) |
| `rapor` | DECIMAL(3,1) | Sağlık raporu (gün) |
| `gunluk_kazanc` | DECIMAL(10,2) | Günlük kazanç |
| `fm_kazanc` | DECIMAL(10,2) | Fazla mesai kazancı |

---

### 2. `personnel_leave_balance` (İzin Bakiyesi)

Personelin yıllık izin hakları ve kullanımı.

```sql
-- Örnek kayıt
INSERT INTO personnel_leave_balance (
    personnel_id, year,
    annual_leave_entitlement,
    annual_leave_used,
    annual_leave_balance
) VALUES (
    123, 2025,
    14.0,   -- Hak edilen (1-5 yıl arası)
    5.5,    -- Kullanılan
    8.5     -- Kalan
);
```

#### İzin Türleri

- **Yıllık Ücretli İzin**: Kıdem bazlı (14-26 gün)
- **Rapor**: Sağlık raporu günleri
- **Ücretsiz İzin**: Maaş kesilir
- **Mazeret İzni**: Saat bazında
- **Doğum İzni**: 16 hafta (kadın)
- **Babalık İzni**: 5-10 gün

---

### 3. `shift_definitions` (Vardiya Tanımları)

Çalışma vardiyaları.

| Kod | Ad | Başlangıç | Bitiş | Mola | Gece? |
|-----|-----|-----------|-------|------|-------|
| SABAH | Sabah Vardiyası | 08:00 | 17:00 | 60 dk | ❌ |
| AKSAM | Akşam Vardiyası | 16:00 | 00:00 | 60 dk | ❌ |
| GECE | Gece Vardiyası | 00:00 | 08:00 | 60 dk | ✅ |
| NORMAL | Normal Mesai | 09:00 | 18:00 | 60 dk | ❌ |
| ESNEK | Esnek Çalışma | 09:00 | 17:00 | 0 dk | ❌ |

---

### 4. `calendar_holidays` (Resmi Tatiller)

2025 yılı resmi tatil günleri (14 gün).

```
01 Ocak    - Yılbaşı
31 Mart    - Ramazan Bayramı 1. Gün
01 Nisan   - Ramazan Bayramı 2. Gün
02 Nisan   - Ramazan Bayramı 3. Gün
23 Nisan   - 23 Nisan Ulusal Egemenlik ve Çocuk Bayramı
01 Mayıs   - İşçi Bayramı
19 Mayıs   - Gençlik ve Spor Bayramı
07 Haziran - Kurban Bayramı 1. Gün
08 Haziran - Kurban Bayramı 2. Gün
09 Haziran - Kurban Bayramı 3. Gün
10 Haziran - Kurban Bayramı 4. Gün
15 Temmuz  - Demokrasi ve Milli Birlik Günü
30 Ağustos - Zafer Bayramı
29 Ekim    - Cumhuriyet Bayramı
```

---

## 📊 VIEW'LER

### `v_monthly_attendance_summary`

Aylık özet - Performans için.

```sql
SELECT * FROM v_monthly_attendance_summary 
WHERE donem = '2025-12' 
ORDER BY adi_soyadi;
```

**Dönen Kolonlar:**
- `calisan_gun` - Çalışılan gün sayısı
- `toplam_normal_saat` - Toplam normal mesai
- `toplam_fm_saat` - Toplam fazla mesai
- `toplam_yillik_izin` - Kullanılan yıllık izin
- `toplam_kazanc` - Toplam kazanç (normal + FM + tatil)

---

### `v_personnel_calendar`

Takvim görünümü - Günlük detay.

```sql
SELECT * FROM v_personnel_calendar 
WHERE donem = '2025-12' 
AND personnel_id = 123
ORDER BY attendance_date;
```

**Dönen Kolonlar:**
- `attendance_date` - Tarih
- `gun_adi` - Pazartesi, Salı, ...
- `calisma_durumu` - Çalıştı, İzinli, Rapor, ...
- `toplam_saat` - Gün içi toplam çalışma
- `izin_turu` - İzin türü (varsa)
- `gunluk_toplam_kazanc` - Günlük kazanç

---

## 🔄 LUCA ENTEGRASYONU

### Beklenen Excel Formatı

Luca'dan günlük puantaj export:

```
TC Kimlik No | Adı Soyadı  | Tarih      | Gün | Durum   | Giriş | Çıkış | Normal Saat | FM Saat | İzin Türü
11111111111  | Ahmet Yılmaz| 01.12.2025 | Pzt | Çalıştı | 08:00 | 17:00 | 8.0         | 0       | -
11111111111  | Ahmet Yılmaz| 02.12.2025 | Sal | Çalıştı | 08:00 | 19:00 | 8.0         | 2.0     | -
11111111111  | Ahmet Yılmaz| 03.12.2025 | Çar | İzinli  | -     | -     | -           | -       | Yıllık
```

### Import Akışı

1. Excel yüklenir
2. TC Kimlik ile personel bulunur (`personnel` tablosu)
3. Her satır için `personnel_daily_attendance` kaydı oluşturulur
4. Kazanç hesaplaması yapılır (sözleşme + puantaj)
5. İzin bakiyeleri otomatik güncellenir (trigger)

---

## 🎯 KULLANIM ÖRNEKLERİ

### 1. Personelin Aylık Çalışma Raporu

```sql
SELECT 
    adi_soyadi,
    calisan_gun,
    toplam_normal_saat,
    toplam_fm_saat,
    toplam_yillik_izin,
    toplam_rapor,
    toplam_kazanc
FROM v_monthly_attendance_summary
WHERE donem = '2025-12'
AND personnel_id = 123;
```

---

### 2. Gün Bazında Detay

```sql
SELECT 
    attendance_date,
    gun_adi,
    calisma_durumu,
    giris_saati,
    cikis_saati,
    normal_saat,
    fazla_mesai_saat,
    izin_turu
FROM v_personnel_calendar
WHERE personnel_id = 123
AND donem = '2025-12'
ORDER BY attendance_date;
```

---

### 3. Fazla Mesai Yapan Personeller

```sql
SELECT 
    personnel_id,
    adi_soyadi,
    SUM(fazla_mesai_saat) as toplam_fm,
    SUM(fm_kazanc) as toplam_fm_kazanc
FROM personnel_daily_attendance
WHERE donem = '2025-12'
GROUP BY personnel_id, adi_soyadi
HAVING toplam_fm > 0
ORDER BY toplam_fm DESC;
```

---

### 4. İzin Bakiyeleri

```sql
SELECT 
    p.first_name,
    p.last_name,
    plb.annual_leave_entitlement as hak,
    plb.annual_leave_used as kullanilan,
    plb.annual_leave_balance as kalan
FROM personnel_leave_balance plb
JOIN personnel p ON plb.personnel_id = p.id
WHERE plb.year = 2025
ORDER BY plb.annual_leave_balance;
```

---

### 5. Resmi Tatilde Çalışanlar

```sql
SELECT 
    pda.adi_soyadi,
    pda.attendance_date,
    ch.name as tatil_adi,
    pda.tatil_mesai_saat,
    pda.tatil_kazanc
FROM personnel_daily_attendance pda
JOIN calendar_holidays ch ON pda.attendance_date = ch.holiday_date
WHERE pda.calisma_durumu = 'CALISTI'
AND pda.donem = '2025-12'
ORDER BY pda.attendance_date;
```

---

## 🔧 TRİGGER'LAR

### `trg_attendance_after_insert`

Günlük puantaj kaydedildiğinde:
- İzin bakiyelerini otomatik günceller
- Yıllık izin, rapor, ücretsiz izin günlerini toplar
- Kalan bakiyeyi hesaplar

```sql
-- Trigger otomatik çalışır, manuel müdahale gerektirmez
INSERT INTO personnel_daily_attendance (...) VALUES (...);
-- ↓ Trigger tetiklenir
-- ↓ personnel_leave_balance tablosu güncellenir
```

---

## 📝 SONRAKİ ADIMLAR

### Backend (API)

1. **Endpoint**: `/api/v1/daily-attendance`
   - `GET /list` - Takvim listesi
   - `POST /upload` - Excel import
   - `GET /summary` - Aylık özet
   - `GET /calendar` - Takvim görünümü

2. **Excel Parser**: Luca formatı okuma
3. **Hesaplama Modülü**: Kazanç hesaplama
4. **Validation**: Puantaj doğrulama

### Frontend

1. **Takvim Bileşeni**: Aylık görünüm
2. **Giriş-Çıkış Form**: Manuel kayıt
3. **İzin Yönetimi**: İzin talep/onay
4. **Raporlar**: Özet raporlar

---

## 📞 DESTEK

**Migration Dosyası:** `database/migrations/20251222_add_personnel_daily_attendance.sql`  
**Kontrol Script:** `backend/check_daily_attendance.py`  

---

## ✅ KURULUM DURUMU

- [x] Veritabanı tabloları oluşturuldu
- [x] View'ler tanımlandı
- [x] Vardiya tanımları eklendi
- [x] 2025 resmi tatiller yüklendi
- [x] Trigger'lar aktif
- [ ] API endpoint (Yapılacak)
- [ ] Frontend bileşen (Yapılacak)
- [ ] Excel import (Yapılacak)

**Son Güncelleme:** 22 Aralık 2025
