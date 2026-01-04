# PostgreSQL Kurulum Rehberi

## Yöntem 1: Otomatik (PowerShell)

```powershell
cd C:\Projects\muhasebe-sistem
.\scripts\setup\setup_postgresql.ps1
```

PostgreSQL şifresi sorulacak, girin.

---

## Yöntem 2: Manuel (pgAdmin)

### Adım 1: Database Oluştur

1. pgAdmin'i aç
2. **Servers** > **PostgreSQL 15** sağ tık
3. **Create** > **Database**
4. **Database:** `muhasebe_db`
5. **Owner:** `postgres`
6. **Encoding:** `UTF8`
7. **Save** tıkla

### Adım 2: Schema Yükle

1. `muhasebe_db` database'ine sağ tık
2. **Query Tool** seç
3. **File** > **Open**
4. `C:\Projects\muhasebe-sistem\database\schema.sql` seç
5. **Execute (F5)** tıkla
6. "Database schema created successfully!" mesajını gör

### Adım 3: Seed Data Yükle

Aynı Query Tool'da:

1. `database/seeds/01_accounts.sql` aç ve çalıştır
2. `database/seeds/02_cost_centers.sql` aç ve çalıştır
3. `database/seeds/03_users.sql` aç ve çalıştır (opsiyonel)

### Adım 4: Kontrol Et

```sql
-- Tabloları listele
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Hesap sayısını kontrol et
SELECT COUNT(*) FROM accounts;
-- Sonuç: 24 hesap olmalı
```

---

## Yöntem 3: Komut Satırı (psql)

```powershell
# PostgreSQL'e bağlan
psql -U postgres

# Database oluştur
CREATE DATABASE muhasebe_db WITH ENCODING='UTF8';
\c muhasebe_db

# Schema yükle
\i C:/Projects/muhasebe-sistem/database/schema.sql

# Seed data yükle
\i C:/Projects/muhasebe-sistem/database/seeds/01_accounts.sql
\i C:/Projects/muhasebe-sistem/database/seeds/02_cost_centers.sql

# Çıkış
\q
```

---

## Backend Bağlantı Ayarları

`backend/.env` dosyasını düzenle:

```bash
DATABASE_URL=postgresql://postgres:ŞİFRENİZ@localhost:5432/muhasebe_db
```

**ŞİFRENİZ** yerine PostgreSQL postgres kullanıcı şifrenizi yazın.

---

## Sorun Giderme

### "psql komutu bulunamadı"

PostgreSQL bin klasörünü PATH'e ekle:

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"
```

### "password authentication failed"

Şifre yanlış. pgAdmin'de şifreyi sıfırla:

1. **postgres** kullanıcısına sağ tık
2. **Properties**
3. **Definition** > **Password**
4. Yeni şifre gir, **Save**

### "database already exists"

```sql
DROP DATABASE muhasebe_db;
CREATE DATABASE muhasebe_db WITH ENCODING='UTF8';
```

---

## Başarı Kontrolü

```sql
-- Tüm tabloları listele
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Beklenen: 6 tablo
-- accounts, contacts, cost_centers, transaction_lines, transactions, users

-- Hesap planı kontrolü
SELECT code, name FROM accounts ORDER BY code LIMIT 5;
```

Çıktı:
```
 code |         name          
------+----------------------
 100  | KASA
 101  | ALINAN ÇEKLER
 102  | BANKALAR
 120  | ALICILAR
 121  | ALACAK SENETLERİ
```

---

## Sonraki Adım

Backend'i başlat ve test et:

```powershell
cd C:\Projects\muhasebe-sistem\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

http://127.0.0.1:8000/docs adresini aç.
