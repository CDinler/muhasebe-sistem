-- =====================================================
-- LUCA BÖLÜM - COST CENTER EŞLEŞTİRME TABLOSU
-- Luca sicil'deki bölüm isimlerini sistemdeki maliyet merkezleri ile eşleştirir
-- =====================================================

CREATE TABLE IF NOT EXISTS `luca_bolum_cost_center_mapping` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Luca Bölüm Bilgisi
    `luca_bolum_pattern` VARCHAR(200) NOT NULL COMMENT 'Luca bölüm adı veya pattern (% ile wildcard)',
    `luca_bolum_prefix` VARCHAR(10) DEFAULT NULL COMMENT 'Bölüm kodu (örn: 34, 29)',
    
    -- Cost Center Eşleştirme
    `cost_center_id` INT NOT NULL COMMENT 'Eşleşen maliyet merkezi ID',
    
    -- Açıklama
    `description` VARCHAR(500) DEFAULT NULL COMMENT 'Eşleştirme açıklaması',
    
    -- Durum
    `is_active` TINYINT(1) DEFAULT 1 COMMENT 'Aktif mi?',
    `priority` INT DEFAULT 100 COMMENT 'Öncelik (düşük değer = yüksek öncelik)',
    
    -- Sistem
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX `idx_luca_bolum_pattern` (`luca_bolum_pattern`),
    INDEX `idx_luca_bolum_prefix` (`luca_bolum_prefix`),
    INDEX `idx_cost_center` (`cost_center_id`),
    INDEX `idx_active_priority` (`is_active`, `priority`),
    
    -- Foreign Key
    CONSTRAINT `fk_luca_mapping_cost_center` 
        FOREIGN KEY (`cost_center_id`) 
        REFERENCES `cost_centers` (`id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Luca bölüm - Cost center eşleştirme tablosu';

-- =====================================================
-- EŞLEŞTİRMELERİ EKLE
-- =====================================================

-- Önce cost_center ID'lerini bulalım
SET @merkez_id = (SELECT id FROM cost_centers WHERE code = 'MERKEZ');
SET @habas_aliaga_id = (SELECT id FROM cost_centers WHERE code = 'HABAŞ_ALIAĞA');
SET @alkatas_id = (SELECT id FROM cost_centers WHERE code = 'ALKATAŞ_CUMHURIYET');
SET @gubretas_aliaga_id = (SELECT id FROM cost_centers WHERE code = 'GÜBRETAŞ_ALIAĞA');
SET @habas_uzunbey_id = (SELECT id FROM cost_centers WHERE code = 'HABAŞ_UZUNBEY');
SET @habas_bilecik_id = (SELECT id FROM cost_centers WHERE code = 'HABAŞ_BILECIK');
SET @habas_manisa_id = (SELECT id FROM cost_centers WHERE code = 'HABAŞ_MANISA');

-- Eşleştirmeleri ekle
INSERT INTO luca_bolum_cost_center_mapping 
    (luca_bolum_pattern, luca_bolum_prefix, cost_center_id, description, priority) 
VALUES
    -- HABAŞ 9 ALİAĞA (34) → Habaş Aliağa
    ('34-HABAŞ 9 ALİAĞA', '34', @habas_aliaga_id, 'Habaş 9 Aliağa şantiyesi', 10),
    ('%HABAŞ%ALİAĞA%', '34', @habas_aliaga_id, 'Habaş Aliağa wildcard (fallback)', 50),
    
    -- ALKATAŞ (29) → Alkataş Cumhuriyet  
    ('29-ALKATAŞ AŞ.- NUROL İNŞAAT', '29', @alkatas_id, 'Alkataş - Nurol İnşaat', 10),
    ('%ALKATAŞ%', '29', @alkatas_id, 'Alkataş wildcard (fallback)', 50),
    
    -- MERKEZ OFİS → Merkez
    ('MERKEZ OFİS', NULL, @merkez_id, 'Merkez ofis', 10),
    ('%MERKEZ%', NULL, @merkez_id, 'Merkez wildcard (fallback)', 50),
    
    -- GÜBRETAŞ ALİAĞA (36) → Gübretaş Aliağa
    ('36-GÜBRETAŞ ALİAĞA TESİSLERİ', '36', @gubretas_aliaga_id, 'Gübretaş Aliağa tesisleri', 10),
    ('%GÜBRETAŞ%ALİAĞA%', '36', @gubretas_aliaga_id, 'Gübretaş Aliağa wildcard', 50),
    
    -- HABAŞ 7 UZUNBEY (28) → Habaş Uzunbey
    ('28-TAŞERON 23 UZUNBEY-HABAŞ 7', '28', @habas_uzunbey_id, 'Habaş 7 Uzunbey (Taşeron 23)', 10),
    ('%UZUNBEY%HABAŞ%', '28', @habas_uzunbey_id, 'Habaş Uzunbey wildcard', 50),
    
    -- HABAŞ 6 ALİAĞA (26) → Habaş Aliağa (fallback)
    ('26-TAŞERON 21 ALİAĞA-HABAŞ 6', '26', @habas_aliaga_id, 'Habaş 6 Aliağa (Taşeron 21)', 10),
    
    -- HABAŞ 10 BİLECİK (35) → Habaş Bilecik
    ('35-HABAŞ 10 BİLECİK', '35', @habas_bilecik_id, 'Habaş 10 Bilecik', 10),
    ('%HABAŞ%BİLECİK%', '35', @habas_bilecik_id, 'Habaş Bilecik wildcard', 50),
    
    -- HABAŞ 8 MANİSA (31) → Habaş Manisa
    ('31-HABAŞ 8 MANİSA', '31', @habas_manisa_id, 'Habaş 8 Manisa', 10),
    ('%HABAŞ%MANİSA%', '31', @habas_manisa_id, 'Habaş Manisa wildcard', 50);

-- Kontrol sorgusu
SELECT 
    lm.id,
    lm.luca_bolum_pattern,
    lm.luca_bolum_prefix,
    cc.code as cost_center_code,
    cc.name as cost_center_name,
    lm.priority,
    lm.description
FROM luca_bolum_cost_center_mapping lm
JOIN cost_centers cc ON cc.id = lm.cost_center_id
WHERE lm.is_active = 1
ORDER BY lm.priority, lm.luca_bolum_pattern;
