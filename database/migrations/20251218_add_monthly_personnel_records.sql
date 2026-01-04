-- =====================================================
-- LUCA PERSONEL SİCİL SİSTEMİ - monthly_personnel_records
-- Tarih: 2025-12-18
-- Açıklama: Aylık personel sicil kayıtları tablosu
-- =====================================================

-- Tablo oluştur
CREATE TABLE IF NOT EXISTS `monthly_personnel_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Personel ve Dönem
    `personnel_id` INT NOT NULL,
    `donem` VARCHAR(7) NOT NULL COMMENT 'YYYY-MM format (örn: 2025-10)',
    
    -- Şantiye/Bölüm Bilgileri
    `bolum_adi` VARCHAR(200) DEFAULT NULL COMMENT 'Luca bölüm adı (örn: 34-HABAŞ 9 ALİAĞA)',
    `cost_center_id` INT DEFAULT NULL COMMENT 'Maliyet merkezi ID',
    `cost_center_code` VARCHAR(50) DEFAULT NULL COMMENT 'Maliyet merkezi kodu',
    
    -- Çalışma Tarihleri
    `ise_giris_tarihi` DATE DEFAULT NULL COMMENT 'Dönem içi giriş tarihi',
    `isten_cikis_tarihi` DATE DEFAULT NULL COMMENT 'Dönem içi çıkış tarihi',
    `calisilan_gun` INT DEFAULT 0 COMMENT 'Çalışılan gün sayısı',
    
    -- Ücret Bilgileri (Luca sicil verisi)
    `ucret` DECIMAL(18, 2) DEFAULT NULL COMMENT 'Sicil ücreti',
    `ucret_tipi` VARCHAR(10) DEFAULT NULL COMMENT 'N=Net, B=Brüt',
    
    -- Luca Sicil Raw Data
    `luca_sicil_data` JSON DEFAULT NULL COMMENT 'Luca sicil Excel satırı (tüm kolonlar)',
    
    -- İş Bilgileri
    `isyeri` VARCHAR(200) DEFAULT NULL COMMENT 'Luca işyeri adı',
    `unvan` VARCHAR(200) DEFAULT NULL COMMENT 'Ünvan/Pozisyon',
    `meslek_adi` VARCHAR(200) DEFAULT NULL COMMENT 'Meslek adı',
    
    -- Sistem
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` INT DEFAULT NULL,
    
    -- Indexes
    INDEX `idx_monthly_personnel_donem` (`donem`),
    INDEX `idx_monthly_personnel_personnel_id` (`personnel_id`),
    INDEX `idx_monthly_personnel_cost_center` (`cost_center_id`),
    
    -- Unique Constraint: Bir personel, bir dönemde, bir bölümde sadece 1 kayıt
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
        
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Aylık personel sicil kayıtları (Luca import)';

-- Başarı mesajı
SELECT '✅ monthly_personnel_records tablosu başarıyla oluşturuldu!' AS sonuc;

-- =====================================================
-- VERIFICATION QUERIES (MANUEL ÇALIŞTIRIN)
-- =====================================================

/*
-- Tablo bilgilerini görüntüle
SHOW CREATE TABLE monthly_personnel_records;

-- Kolonları kontrol et
DESCRIBE monthly_personnel_records;

-- İndeksleri kontrol et
SHOW INDEX FROM monthly_personnel_records;

-- Tablo istatistikleri
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    CREATE_TIME,
    TABLE_COMMENT
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'muhasebe'
  AND TABLE_NAME = 'monthly_personnel_records';
*/

-- =====================================================
-- ÖRNEK VERİ (OPSİYONEL - TEST İÇİN)
-- =====================================================

/*
-- Örnek kayıt ekle
INSERT INTO monthly_personnel_records (
    personnel_id, donem, bolum_adi, 
    cost_center_id, cost_center_code,
    ise_giris_tarihi, isten_cikis_tarihi,
    ucret, ucret_tipi,
    isyeri, unvan, meslek_adi
) VALUES (
    1, '2025-10', '34-HABAŞ 9 ALİAĞA',
    34, '34',
    '2025-10-01', NULL,
    37500.00, 'B',
    'KADIOĞULLARI ENDÜSTRİYEL YAPI SİS.PEYZAJ LTD.ŞTİ.',
    'İnşaat İşçisi', 'İnşaat İşçisi'
);

-- Sorgu testi
SELECT 
    p.first_name,
    p.last_name,
    mpr.donem,
    mpr.bolum_adi,
    mpr.cost_center_code,
    mpr.ucret,
    mpr.ucret_tipi
FROM monthly_personnel_records mpr
JOIN personnel p ON p.id = mpr.personnel_id
ORDER BY mpr.donem DESC, p.last_name;
*/

-- =====================================================
-- ROLLBACK (GEREKİRSE)
-- =====================================================

/*
-- Tabloyu sil
DROP TABLE IF EXISTS monthly_personnel_records;
*/

SELECT '✅ monthly_personnel_records tablosu başarıyla oluşturuldu!' AS sonuc;
