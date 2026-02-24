# Database Setup Guide

## MySQL Muhasebe Sistem - Kurulum Rehberi

### Gereksinimler
- XAMPP (MySQL 8.0+)
- Python 3.14+

---

## Kurulum Adımları

### 1. Database Oluştur

XAMPP Control Panel'den MySQL'i başlat, sonra:

```bash
# MySQL'e bağlan
C:\xampp\mysql\bin\mysql.exe -u root

# Database oluştur
CREATE DATABASE muhasebe_sistem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE muhasebe_sistem;
EXIT;
```

### 2. Schema Yükle

```bash
# Migrations klasöründen schema'yı import et
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < database/migrations/001_initial_schema.sql
```

Bu komut **25 tablo** oluşturacak:
- accounts, contacts, cost_centers
- personnel, personnel_contracts, personnel_draft_contracts
- transactions, transaction_lines
- einvoices, luca_bordro
- payroll_calculations, personnel_puantaj_grid
- ve diğerleri...

### 3. Seed Data Yükle

```bash
# Temel verileri yükle
cd C:\Projects\muhasebe-sistem\database\seeds

# Sırayla yükle
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < 01_calendar_holidays.sql
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < 02_system_config.sql
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < 03_tax_bracket.sql
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < 04_users.sql
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < 05_cost_centers.sql
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < 06_document_types.sql
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem < 07_tax_codes.sql
```

Seed dosyaları (159 satır):
- **01_calendar_holidays.sql** - 2026 resmi tatiller (29 satır)
- **02_system_config.sql** - Sistem konfigürasyonu (30 satır)
- **03_tax_bracket.sql** - Gelir vergisi dilimleri (5 satır)
- **04_users.sql** - Test kullanıcıları (3 satır)
- **05_cost_centers.sql** - Maliyet merkezleri (23 satır)
- **06_document_types.sql** - Belge tipleri (39 satır)
- **07_tax_codes.sql** - KDV/vergi kodları (30 satır)

### 4. Kurulumu Doğrula

```bash
# MySQL'e bağlan
C:\xampp\mysql\bin\mysql.exe -u root muhasebe_sistem

# Tabloları kontrol et
SHOW TABLES;
# 25 tablo görmelisin

# Seed verilerini kontrol et
SELECT COUNT(*) FROM calendar_holidays;  -- 29
SELECT COUNT(*) FROM system_config;      -- 30
SELECT COUNT(*) FROM tax_bracket;        -- 5
SELECT COUNT(*) FROM users;              -- 3
SELECT COUNT(*) FROM cost_centers;       -- 23
SELECT COUNT(*) FROM document_types;     -- 39
SELECT COUNT(*) FROM tax_codes;          -- 30
```

---

## Backend Konfigürasyonu

`.env` dosyasını kontrol et:

```env
DATABASE_URL=mysql+pymysql://root@localhost/muhasebe_sistem
```

---

## Notlar

- ⚠️ **Üretim ortamında** MySQL root kullanıcısı yerine özel kullanıcı oluşturun
- 🔐 **Şifre** belirlemek için: `mysqladmin -u root password "yeni_sifre"`
- 📦 **Yedekleme**: `mysqldump -u root muhasebe_sistem > backup_$(date +%Y%m%d).sql`
- 🔄 **Migration**: Gelecekteki schema değişiklikleri için `backend/alembic/` kullanın

---

## Sorun Giderme

### "Access denied" hatası
```bash
# MySQL root şifresini sıfırla (XAMPP)
# 1. XAMPP'den MySQL'i durdur
# 2. my.ini dosyasına ekle: skip-grant-tables
# 3. MySQL'i başlat ve şifreyi değiştir
```

### "Unknown database" hatası
```bash
# Database'in oluşturulduğundan emin ol
SHOW DATABASES;
```

### Tablo oluşturma hatası
```bash
# Foreign key kontrolünü kapat
SET FOREIGN_KEY_CHECKS=0;
# Schema'yı yükle
# Foreign key kontrolünü aç
SET FOREIGN_KEY_CHECKS=1;
```

---

## İletişim

Sorun bildirmek için: GitHub Issues
