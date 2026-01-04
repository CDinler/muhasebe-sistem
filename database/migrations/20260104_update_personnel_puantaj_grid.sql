-- ========================================
-- Migration: Update personnel_puantaj_grid table
-- 13 yeni alan ekleme
-- Tarih: 2026-01-04
-- ========================================

USE muhasebe_sistem;

-- YEDEKLEME
CREATE TABLE IF NOT EXISTS personnel_puantaj_grid_backup_20260104 AS SELECT * FROM personnel_puantaj_grid;

-- Yeni sütunlar ekle
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS contract_id INT AFTER personnel_id;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS ayin_toplam_gun_sayisi INT DEFAULT 30 AFTER cost_center_id;

-- Çalışma Detayları
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS normal_calismasi DECIMAL(5,2) DEFAULT 0 AFTER toplam_gun_sayisi;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS fazla_calismasi DECIMAL(7,2) DEFAULT 0 AFTER normal_calismasi;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS gece_calismasi DECIMAL(5,2) DEFAULT 0 AFTER fazla_calismasi;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS tatil_calismasi DECIMAL(5,2) DEFAULT 0 AFTER gece_calismasi;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS sigorta_girmedigi INT DEFAULT 0 AFTER tatil_calismasi;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS hafta_tatili INT DEFAULT 0 AFTER sigorta_girmedigi;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS resmi_tatil INT DEFAULT 0 AFTER hafta_tatili;

-- Ek Ödemeler
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS yol DECIMAL(10,2) DEFAULT 0 AFTER resmi_tatil;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS prim DECIMAL(10,2) DEFAULT 0 AFTER yol;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS ikramiye DECIMAL(10,2) DEFAULT 0 AFTER prim;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS bayram DECIMAL(10,2) DEFAULT 0 AFTER ikramiye;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS kira DECIMAL(10,2) DEFAULT 0 AFTER bayram;

-- Timestamps ekle (eğer yoksa)
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS created_by INT AFTER updated_at;
ALTER TABLE personnel_puantaj_grid ADD COLUMN IF NOT EXISTS updated_by INT AFTER created_by;

-- toplam_fm kolonunu fazla_calismasi ile birleştir (veri varsa)
-- UPDATE personnel_puantaj_grid SET fazla_calismasi = toplam_fm WHERE fazla_calismasi = 0 AND toplam_fm > 0;
-- ALTER TABLE personnel_puantaj_grid DROP COLUMN IF EXISTS toplam_fm;

-- Index ekle
CREATE INDEX IF NOT EXISTS idx_ppg_contract_id ON personnel_puantaj_grid(contract_id);

-- Foreign key ekle
ALTER TABLE personnel_puantaj_grid ADD CONSTRAINT fk_ppg_contract
    FOREIGN KEY (contract_id) REFERENCES personnel_contracts(id) ON DELETE SET NULL;

-- ========================================
-- Tamamlandı
-- ========================================
SELECT 'personnel_puantaj_grid table updated successfully!' AS status;
