-- ========================================
-- Migration: Update personnel_contracts table
-- 7 yeni alan ekleme + enum güncelleme
-- Tarih: 2026-01-04
-- ========================================

USE muhasebe_sistem;

-- YEDEKLEME
CREATE TABLE IF NOT EXISTS personnel_contracts_backup_20260104 AS SELECT * FROM personnel_contracts;

-- Yeni sütunlar ekle
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS tc_kimlik_no VARCHAR(11) AFTER personnel_id;
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS bolum VARCHAR(200) AFTER tc_kimlik_no;
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS monthly_personnel_records_id INT AFTER bolum;
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS maas_hesabi ENUM('tipa', 'tipb', 'tipc') AFTER maas2_tutar;
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS taseron INT DEFAULT 0 AFTER tatil_orani;
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS taseron_id INT AFTER taseron;
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS departman ENUM(
    'Ankraj Ekibi', 'Asfaltlama Ekibi', 'Bekçi Ekibi',
    'Beton Kesim Ekibi', 'Demirci Ekibi', 'Döşeme Ekibi',
    'Elektrikçi Ekibi', 'Fore Kazık Ekibi', 'İdare Ekibi',
    'Kalıpçı Ekibi', 'Kalıpçı Kolon Ekibi', 'Kaynakçı Ekibi',
    'Merkez Ekibi', 'Operatör Ekibi', 'Saha Beton Ekibi',
    'Stajyer Ekibi', 'Şöför Ekibi', 'Yıkım Ekibi'
) AFTER taseron_id;

-- Timestamps ekle (eğer yoksa)
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS created_by INT AFTER updated_at;
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS updated_by INT AFTER created_by;

-- ucret_nevi enum değerlerini güncelle
ALTER TABLE personnel_contracts MODIFY COLUMN ucret_nevi ENUM('aylik', 'sabit aylik', 'gunluk') NOT NULL;

-- calisma_takvimi'ni JSON'dan ENUM'a çevir
ALTER TABLE personnel_contracts ADD COLUMN IF NOT EXISTS calisma_takvimi_new ENUM('atipi', 'btipi', 'ctipi') AFTER kanun_tipi;
-- JSON değerleri varsa manuel map edilmeli (şimdilik NULL)
ALTER TABLE personnel_contracts DROP COLUMN IF EXISTS calisma_takvimi;
ALTER TABLE personnel_contracts CHANGE COLUMN calisma_takvimi_new calisma_takvimi ENUM('atipi', 'btipi', 'ctipi');

-- fm_orani ve tatil_orani default değerlerini güncelle
ALTER TABLE personnel_contracts MODIFY COLUMN fm_orani DECIMAL(5,2) DEFAULT 1;
ALTER TABLE personnel_contracts MODIFY COLUMN tatil_orani DECIMAL(5,2) DEFAULT 1;

-- Gereksiz kolonları sil
ALTER TABLE personnel_contracts DROP COLUMN IF EXISTS cost_center_name;
ALTER TABLE personnel_contracts DROP COLUMN IF EXISTS account_code;

-- Index ekle
CREATE INDEX IF NOT EXISTS idx_pc_tc_kimlik_no ON personnel_contracts(tc_kimlik_no);
CREATE INDEX IF NOT EXISTS idx_pc_monthly_records ON personnel_contracts(monthly_personnel_records_id);
CREATE INDEX IF NOT EXISTS idx_pc_taseron_id ON personnel_contracts(taseron_id);

-- Foreign key ekle
ALTER TABLE personnel_contracts ADD CONSTRAINT fk_pc_monthly_records
    FOREIGN KEY (monthly_personnel_records_id) REFERENCES monthly_personnel_records(id) ON DELETE SET NULL;
ALTER TABLE personnel_contracts ADD CONSTRAINT fk_pc_taseron
    FOREIGN KEY (taseron_id) REFERENCES contacts(id) ON DELETE SET NULL;

-- ========================================
-- Tamamlandı
-- ========================================
SELECT 'personnel_contracts table updated successfully!' AS status;
