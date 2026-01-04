-- ========================================
-- Migration: Update cost_centers table
-- bolum_adi ve timestamps ekle
-- Tarih: 2026-01-04
-- ========================================

USE muhasebe_sistem;

-- YEDEKLEME
CREATE TABLE IF NOT EXISTS cost_centers_backup_20260104 AS SELECT * FROM cost_centers;

-- Yeni sütun ekle
ALTER TABLE cost_centers ADD COLUMN IF NOT EXISTS bolum_adi VARCHAR(200) AFTER is_active;

-- Timestamps ekle (eğer yoksa)
ALTER TABLE cost_centers ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER bolum_adi;
ALTER TABLE cost_centers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
ALTER TABLE cost_centers ADD COLUMN IF NOT EXISTS created_by INT AFTER updated_at;
ALTER TABLE cost_centers ADD COLUMN IF NOT EXISTS updated_by INT AFTER created_by;

-- ========================================
-- Tamamlandı
-- ========================================
SELECT 'cost_centers table updated successfully!' AS status;
