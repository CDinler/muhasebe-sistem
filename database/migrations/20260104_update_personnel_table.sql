-- ========================================
-- Migration: Update personnel table
-- Basitleştirme: Sadece gerekli alanlar kalacak
-- Tarih: 2026-01-04
-- ========================================

USE muhasebe_sistem;

-- YEDEKLEME (önce yedek al)
CREATE TABLE IF NOT EXISTS personnel_backup_20260104 AS SELECT * FROM personnel;

-- ADIM 1: Foreign key constraint'lerini kaldır
ALTER TABLE personnel DROP FOREIGN KEY IF EXISTS personnel_ibfk_1;
ALTER TABLE personnel DROP FOREIGN KEY IF EXISTS fk_personnel_account;

-- ADIM 2: Index'leri kaldır
ALTER TABLE personnel DROP INDEX IF EXISTS idx_personnel_contact_id;
ALTER TABLE personnel DROP INDEX IF EXISTS idx_personnel_account_id;

-- ADIM 3: Gereksiz kolonları sil
ALTER TABLE personnel DROP COLUMN IF EXISTS contact_id;
ALTER TABLE personnel DROP COLUMN IF EXISTS account_id;

-- ADIM 4: NOT NULL ayarları (zaten var olan kolonlar için)
ALTER TABLE personnel MODIFY COLUMN tc_kimlik_no VARCHAR(11) NOT NULL;
ALTER TABLE personnel MODIFY COLUMN ad VARCHAR(100) NOT NULL;
ALTER TABLE personnel MODIFY COLUMN soyad VARCHAR(100) NOT NULL;

-- ADIM 5: Index ekle
CREATE INDEX IF NOT EXISTS idx_personnel_tc_kimlik_no ON personnel(tc_kimlik_no);
CREATE INDEX IF NOT EXISTS idx_personnel_accounts_id ON personnel(accounts_id);

-- ADIM 6: Foreign key ekle
ALTER TABLE personnel ADD CONSTRAINT fk_personnel_accounts 
    FOREIGN KEY (accounts_id) REFERENCES accounts(id) ON DELETE SET NULL;

-- ========================================
-- Tamamlandı
-- ========================================
SELECT 'personnel table updated successfully!' AS status;
