-- =====================================================
-- LUCA PERSONEL SİCİL - monthly_personnel_records
-- BASİT VERSİYON (phpMyAdmin için optimize)
-- =====================================================

USE muhasebe;

CREATE TABLE IF NOT EXISTS `monthly_personnel_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Personel ve Dönem
    `personnel_id` INT NOT NULL,
    `donem` VARCHAR(7) NOT NULL COMMENT 'YYYY-MM format',
    
    -- Bölüm Bilgileri
    `bolum_adi` VARCHAR(200) DEFAULT NULL COMMENT 'Luca bölüm adı',
    `cost_center_id` INT DEFAULT NULL,
    `cost_center_code` VARCHAR(50) DEFAULT NULL,
    
    -- Tarihler
    `ise_giris_tarihi` DATE DEFAULT NULL,
    `isten_cikis_tarihi` DATE DEFAULT NULL,
    `calisilan_gun` INT DEFAULT 0,
    
    -- Ücret
    `ucret` DECIMAL(18, 2) DEFAULT NULL,
    `ucret_tipi` VARCHAR(10) DEFAULT NULL COMMENT 'N=Net, B=Brüt',
    
    -- Luca Raw Data
    `luca_sicil_data` JSON DEFAULT NULL,
    
    -- İş Bilgileri
    `isyeri` VARCHAR(200) DEFAULT NULL,
    `unvan` VARCHAR(200) DEFAULT NULL,
    `meslek_adi` VARCHAR(200) DEFAULT NULL,
    
    -- Sistem
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` INT DEFAULT NULL,
    
    -- Indexes
    INDEX `idx_monthly_personnel_donem` (`donem`),
    INDEX `idx_monthly_personnel_personnel_id` (`personnel_id`),
    INDEX `idx_monthly_personnel_cost_center` (`cost_center_id`),
    
    -- Unique Constraint
    UNIQUE KEY `uq_personnel_donem_bolum` (`personnel_id`, `donem`, `bolum_adi`),
    
    -- Foreign Keys
    CONSTRAINT `fk_monthly_personnel_personnel` 
        FOREIGN KEY (`personnel_id`) 
        REFERENCES `personnel` (`id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    
    CONSTRAINT `fk_monthly_personnel_cost_center` 
        FOREIGN KEY (`cost_center_id`) 
        REFERENCES `cost_centers` (`id`) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Başarı mesajı
SELECT '✅ Tablo oluşturuldu!' AS sonuc;
