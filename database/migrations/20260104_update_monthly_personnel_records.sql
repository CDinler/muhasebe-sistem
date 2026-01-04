-- ========================================
-- Migration: Update monthly_personnel_records table
-- 23 yeni alan ekleme + detaylandırma
-- Tarih: 2026-01-04
-- ========================================

USE muhasebe_sistem;

-- YEDEKLEME
CREATE TABLE IF NOT EXISTS monthly_personnel_records_backup_20260104 AS SELECT * FROM monthly_personnel_records;

-- Yeni sütunlar ekle
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS contract_id INT AFTER personnel_id;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS yil INT AFTER donem;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS ay INT AFTER yil;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS adi VARCHAR(100) AFTER ay;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS soyadi VARCHAR(100) AFTER adi;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS tc_kimlik_no VARCHAR(11) AFTER soyadi;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS cinsiyeti VARCHAR(10) AFTER tc_kimlik_no;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS unvan VARCHAR(200) AFTER cinsiyeti;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS isyeri VARCHAR(200) AFTER unvan;

-- Bolum alanı
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS bolum VARCHAR(200) AFTER unvan;

-- SSK ve Meslek
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS ssk_no VARCHAR(50) AFTER bolum;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS meslek_adi VARCHAR(200) AFTER ssk_no;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS meslek_kodu VARCHAR(20) AFTER meslek_adi;

-- Aile Bilgileri
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS baba_adi VARCHAR(100) AFTER meslek_kodu;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS anne_adi VARCHAR(100) AFTER baba_adi;

-- Doğum Bilgileri
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS dogum_yeri VARCHAR(100) AFTER anne_adi;
-- dogum_tarihi zaten var

-- Nüfus Bilgileri
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS nufus_cuzdani_no VARCHAR(20) AFTER dogum_tarihi;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS nufusa_kayitli_oldugu_il VARCHAR(100) AFTER nufus_cuzdani_no;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS nufusa_kayitli_oldugu_ilce VARCHAR(100) AFTER nufusa_kayitli_oldugu_il;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS nufusa_kayitli_oldugu_mah VARCHAR(200) AFTER nufusa_kayitli_oldugu_ilce;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS cilt_no VARCHAR(20) AFTER nufusa_kayitli_oldugu_mah;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS sira_no VARCHAR(20) AFTER cilt_no;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS kutuk_no VARCHAR(20) AFTER sira_no;

-- Çalışma Tarihleri ve Ayrılış
-- ise_giris_tarihi ve isten_cikis_tarihi zaten var
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS isten_ayrilis_kodu VARCHAR(20) AFTER isten_cikis_tarihi;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS isten_ayrilis_nedeni VARCHAR(200) AFTER isten_ayrilis_kodu;

-- İletişim ve Adres
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS adres TEXT AFTER isten_ayrilis_nedeni;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS telefon VARCHAR(50) AFTER adres;

-- Banka Bilgileri
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS banka_sube_adi VARCHAR(100) AFTER telefon;
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS hesap_no VARCHAR(34) AFTER banka_sube_adi;

-- Ücret Bilgileri
-- ucret zaten var
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS net_brut VARCHAR(10) AFTER hesap_no;

-- Diğer
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS kan_grubu VARCHAR(5) AFTER net_brut;

-- Timestamps ekle (eğer yoksa)
ALTER TABLE monthly_personnel_records ADD COLUMN IF NOT EXISTS updated_by INT AFTER created_by;

-- JSON kolonunu sil (artık gereksiz)
ALTER TABLE monthly_personnel_records DROP COLUMN IF EXISTS luca_sicil_data;
ALTER TABLE monthly_personnel_records DROP COLUMN IF EXISTS cost_center_code;

-- Index ekle
CREATE INDEX IF NOT EXISTS idx_mpr_contract_id ON monthly_personnel_records(contract_id);
CREATE INDEX IF NOT EXISTS idx_mpr_yil ON monthly_personnel_records(yil);
CREATE INDEX IF NOT EXISTS idx_mpr_ay ON monthly_personnel_records(ay);
CREATE INDEX IF NOT EXISTS idx_mpr_tc_kimlik_no ON monthly_personnel_records(tc_kimlik_no);
CREATE INDEX IF NOT EXISTS idx_mpr_meslek_kodu ON monthly_personnel_records(meslek_kodu);

-- Foreign key ekle (eğer yoksa)
ALTER TABLE monthly_personnel_records DROP FOREIGN KEY IF EXISTS fk_mpr_contract;
ALTER TABLE monthly_personnel_records ADD CONSTRAINT fk_mpr_contract
    FOREIGN KEY (contract_id) REFERENCES personnel_contracts(id) ON DELETE SET NULL;

-- Duplicate kayıtları temizle (en son kaydı tut)
DELETE t1 FROM monthly_personnel_records t1
INNER JOIN monthly_personnel_records t2 
WHERE t1.id < t2.id 
  AND t1.personnel_id = t2.personnel_id 
  AND t1.donem = t2.donem 
  AND t1.bolum = t2.bolum;

-- Unique constraint güncelle
ALTER TABLE monthly_personnel_records DROP INDEX IF EXISTS uq_personnel_donem_bolum;
ALTER TABLE monthly_personnel_records ADD UNIQUE INDEX uq_personnel_donem_bolum (personnel_id, donem, bolum);

-- ========================================
-- Tamamlandı
-- ========================================
SELECT 'monthly_personnel_records table updated successfully!' AS status;
