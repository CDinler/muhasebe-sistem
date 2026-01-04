-- ========================================
-- Migration: Update luca_bordro table
-- Alan isimlerini dokümana göre değiştir
-- Tarih: 2026-01-04
-- ========================================

USE muhasebe_sistem;

-- YEDEKLEME
CREATE TABLE IF NOT EXISTS luca_bordro_backup_20260104 AS SELECT * FROM luca_bordro;

-- Alan isimlerini değiştir
ALTER TABLE luca_bordro CHANGE COLUMN ise_giris_tarihi giris_t DATE;
ALTER TABLE luca_bordro CHANGE COLUMN isten_cikis_tarihi cikis_t DATE;
ALTER TABLE luca_bordro CHANGE COLUMN toplam_gun t_gun INT;
ALTER TABLE luca_bordro CHANGE COLUMN normal_kazanc nor_kazanc DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN diger_kazanc dig_kazanc DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN toplam_kazanc top_kazanc DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN ssk_matrahi ssk_m DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN gelir_vergisi_matrahi g_v_m DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN issizlik_isci iss_p_isci DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN gelir_vergisi gel_ver DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN damga_vergisi damga_v DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN bes_kesintisi oto_kat_bes DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN icra_kesintisi icra DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN avans_kesintisi avans DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN net_odenen n_odenen DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN issizlik_isveren iss_p_isveren DECIMAL(18,2);
ALTER TABLE luca_bordro CHANGE COLUMN kanun_tipi kanun VARCHAR(10);
ALTER TABLE luca_bordro CHANGE COLUMN sgk_sicil_no ssk_sicil_no VARCHAR(20);

-- oz_kesinti kolonunu koru (toplam hesaplama için kullanılabilir)
-- Ama ihtiyaç yoksa silebiliriz
-- ALTER TABLE luca_bordro DROP COLUMN IF EXISTS ozel_kesinti;

-- Timestamps ekle (eğer yoksa)
ALTER TABLE luca_bordro ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
ALTER TABLE luca_bordro ADD COLUMN IF NOT EXISTS created_by INT AFTER updated_at;
ALTER TABLE luca_bordro ADD COLUMN IF NOT EXISTS updated_by INT AFTER created_by;

-- Index güncelle
DROP INDEX IF EXISTS ix_luca_donem_giris ON luca_bordro;
CREATE INDEX ix_luca_donem_giris ON luca_bordro(donem, giris_t);

-- ========================================
-- Tamamlandı
-- ========================================
SELECT 'luca_bordro table updated successfully!' AS status;
