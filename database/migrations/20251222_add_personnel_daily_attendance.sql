-- =====================================================
-- TAKVİMLİ PUANTAJ SİSTEMİ - personnel_daily_attendance
-- Tarih: 2025-12-22
-- Açıklama: Luca uyumlu günlük detaylı puantaj kayıtları
-- =====================================================

-- 1. Günlük Detaylı Puantaj Tablosu
CREATE TABLE IF NOT EXISTS `personnel_daily_attendance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Personel Bilgileri
    `personnel_id` INT NOT NULL COMMENT 'personnel tablosu ID',
    `tckn` VARCHAR(11) NOT NULL COMMENT 'TC Kimlik No',
    `adi_soyadi` VARCHAR(200) NOT NULL COMMENT 'Adı Soyadı',
    
    -- Tarih Bilgisi
    `attendance_date` DATE NOT NULL COMMENT 'Puantaj tarihi',
    `donem` VARCHAR(7) NOT NULL COMMENT 'YYYY-MM (örn: 2025-12)',
    `yil` INT NOT NULL COMMENT 'Yıl',
    `ay` INT NOT NULL COMMENT 'Ay (1-12)',
    `gun_no` INT NOT NULL COMMENT 'Ayın günü (1-31)',
    `gun_adi` VARCHAR(10) DEFAULT NULL COMMENT 'Pazartesi, Salı, Çarşamba, Perşembe, Cuma, Cumartesi, Pazar',
    
    -- Gün Tipi
    `gun_tipi` ENUM(
        'NORMAL',       -- Normal iş günü
        'CUMARTESI',    -- Cumartesi
        'PAZAR',        -- Pazar
        'RESMI_TATIL',  -- Resmi tatil
        'DINI_BAYRAM'   -- Dini bayram
    ) DEFAULT 'NORMAL' COMMENT 'Günün tipi',
    
    -- Çalışma Durumu
    `calisma_durumu` ENUM(
        'CALISTI',       -- Çalıştı
        'IZINLI',        -- İzinli
        'RAPORLU',       -- Raporlu/Hastalık izni
        'GELMEDI',       -- Devamsız/Gelmedi
        'TATIL',         -- Tatil günü
        'HAFTA_TATILI'   -- Hafta tatili (Cumartesi/Pazar)
    ) DEFAULT 'TATIL' COMMENT 'Personelin o günkü durumu',
    
    -- Giriş-Çıkış Saatleri (Luca'dan gelirse)
    `giris_saati` TIME DEFAULT NULL COMMENT 'Giriş saati',
    `cikis_saati` TIME DEFAULT NULL COMMENT 'Çıkış saati',
    
    -- Çalışma Süreleri (Saat cinsinden)
    `normal_saat` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Normal mesai saati',
    `fazla_mesai_saat` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Fazla mesai saati',
    `tatil_mesai_saat` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Tatil günü çalışma saati',
    `gece_vardiya_saat` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Gece vardiyası saati (22:00-06:00)',
    
    -- İzin Türleri (Gün cinsinden - 0, 0.5, 1)
    `yillik_izin` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Yıllık ücretli izin (gün)',
    `ucretsiz_izin` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Ücretsiz izin (gün)',
    `dogum_izin` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Doğum izni (gün)',
    `olum_izin` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Ölüm izni (gün)',
    `evlenme_izin` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Evlenme izni (gün)',
    `babalik_izin` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Babalık izni (gün)',
    `rapor` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Sağlık raporu (gün)',
    `mazeret_izin` DECIMAL(3, 1) DEFAULT 0 COMMENT 'Mazeret izni (gün)',
    
    -- Hesaplanan Kazanç Değerleri (Luca'nın günlük hesaplaması)
    `gunluk_kazanc` DECIMAL(10, 2) DEFAULT 0 COMMENT 'Normal günlük kazanç',
    `fm_kazanc` DECIMAL(10, 2) DEFAULT 0 COMMENT 'Fazla mesai kazancı',
    `tatil_kazanc` DECIMAL(10, 2) DEFAULT 0 COMMENT 'Tatil mesai kazancı',
    
    -- Şantiye/Maliyet Merkezi
    `cost_center_id` INT DEFAULT NULL COMMENT 'Maliyet merkezi ID',
    `santiye_adi` VARCHAR(200) DEFAULT NULL COMMENT 'Şantiye/Bölüm adı',
    
    -- Ek Bilgiler
    `vardiya_kodu` VARCHAR(20) DEFAULT NULL COMMENT 'Vardiya kodu (SABAH, AKSAM, GECE)',
    `aciklama` VARCHAR(500) DEFAULT NULL COMMENT 'Günlük açıklama/not',
    
    -- Upload Bilgisi
    `upload_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Yüklenme tarihi',
    `file_name` VARCHAR(500) DEFAULT NULL COMMENT 'Kaynak Excel dosya adı',
    
    -- İşlem Durumu
    `is_processed` TINYINT(1) DEFAULT 0 COMMENT 'Bordroya aktarıldı mı?',
    `processed_at` TIMESTAMP NULL DEFAULT NULL COMMENT 'İşlenme tarihi',
    
    -- Sistem
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (`personnel_id`) REFERENCES `personnel`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`cost_center_id`) REFERENCES `cost_centers`(`id`) ON DELETE SET NULL,
    
    -- Unique Constraint: Bir personel aynı günde sadece 1 kayıt
    UNIQUE KEY `uq_personnel_date` (`personnel_id`, `attendance_date`),
    
    -- Indexes
    INDEX `idx_attendance_donem` (`donem`),
    INDEX `idx_attendance_date` (`attendance_date`),
    INDEX `idx_attendance_tckn` (`tckn`),
    INDEX `idx_attendance_gun_tipi` (`gun_tipi`),
    INDEX `idx_attendance_calisma_durumu` (`calisma_durumu`),
    INDEX `idx_attendance_personnel_donem` (`personnel_id`, `donem`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Luca uyumlu günlük detaylı puantaj kayıtları - Takvimli sistem';


-- =====================================================
-- 2. Aylık Özet View (Performans için)
-- =====================================================

CREATE OR REPLACE VIEW `v_monthly_attendance_summary` AS
SELECT 
    `personnel_id`,
    `tckn`,
    `adi_soyadi`,
    `donem`,
    `yil`,
    `ay`,
    `cost_center_id`,
    `santiye_adi`,
    
    -- Gün Sayıları
    COUNT(*) as toplam_kayit_gun,
    SUM(CASE WHEN `calisma_durumu` = 'CALISTI' THEN 1 ELSE 0 END) as calisan_gun,
    SUM(CASE WHEN `calisma_durumu` = 'IZINLI' THEN 1 ELSE 0 END) as izinli_gun,
    SUM(CASE WHEN `calisma_durumu` = 'RAPORLU' THEN 1 ELSE 0 END) as raporlu_gun,
    SUM(CASE WHEN `calisma_durumu` = 'GELMEDI' THEN 1 ELSE 0 END) as devamsiz_gun,
    SUM(CASE WHEN `calisma_durumu` IN ('TATIL', 'HAFTA_TATILI') THEN 1 ELSE 0 END) as tatil_gun,
    
    -- Saat Toplamları
    SUM(`normal_saat`) as toplam_normal_saat,
    SUM(`fazla_mesai_saat`) as toplam_fm_saat,
    SUM(`tatil_mesai_saat`) as toplam_tatil_saat,
    SUM(`gece_vardiya_saat`) as toplam_gece_saat,
    
    -- İzin Toplamları
    SUM(`yillik_izin`) as toplam_yillik_izin,
    SUM(`ucretsiz_izin`) as toplam_ucretsiz_izin,
    SUM(`dogum_izin`) as toplam_dogum_izin,
    SUM(`olum_izin`) as toplam_olum_izin,
    SUM(`evlenme_izin`) as toplam_evlenme_izin,
    SUM(`babalik_izin`) as toplam_babalik_izin,
    SUM(`rapor`) as toplam_rapor,
    SUM(`mazeret_izin`) as toplam_mazeret_izin,
    
    -- Kazanç Toplamları
    SUM(`gunluk_kazanc`) as toplam_gunluk_kazanc,
    SUM(`fm_kazanc`) as toplam_fm_kazanc,
    SUM(`tatil_kazanc`) as toplam_tatil_kazanc,
    SUM(`gunluk_kazanc` + `fm_kazanc` + `tatil_kazanc`) as toplam_kazanc,
    
    -- İlk ve Son Kayıt
    MIN(`attendance_date`) as ilk_gun,
    MAX(`attendance_date`) as son_gun
    
FROM `personnel_daily_attendance`
GROUP BY `personnel_id`, `donem`, `cost_center_id`;


-- =====================================================
-- 3. Personel Takvim View (Günlük görünüm için)
-- =====================================================

CREATE OR REPLACE VIEW `v_personnel_calendar` AS
SELECT 
    pda.`id`,
    pda.`personnel_id`,
    p.`code` as personel_kodu,
    pda.`tckn`,
    pda.`adi_soyadi`,
    pda.`attendance_date`,
    pda.`gun_adi`,
    pda.`donem`,
    
    -- Durum bilgileri
    pda.`gun_tipi`,
    pda.`calisma_durumu`,
    pda.`giris_saati`,
    pda.`cikis_saati`,
    
    -- Saat toplamları
    pda.`normal_saat`,
    pda.`fazla_mesai_saat`,
    pda.`tatil_mesai_saat`,
    (pda.`normal_saat` + pda.`fazla_mesai_saat` + pda.`tatil_mesai_saat`) as toplam_saat,
    
    -- İzin bilgisi
    CASE 
        WHEN pda.`yillik_izin` > 0 THEN 'Yıllık İzin'
        WHEN pda.`ucretsiz_izin` > 0 THEN 'Ücretsiz İzin'
        WHEN pda.`rapor` > 0 THEN 'Rapor'
        WHEN pda.`dogum_izin` > 0 THEN 'Doğum İzni'
        WHEN pda.`evlenme_izin` > 0 THEN 'Evlenme İzni'
        WHEN pda.`babalik_izin` > 0 THEN 'Babalık İzni'
        ELSE NULL
    END as izin_turu,
    
    -- Şantiye
    cc.`name` as santiye,
    cc.`code` as santiye_kodu,
    
    -- Kazanç
    (pda.`gunluk_kazanc` + pda.`fm_kazanc` + pda.`tatil_kazanc`) as gunluk_toplam_kazanc,
    
    pda.`aciklama`
    
FROM `personnel_daily_attendance` pda
LEFT JOIN `personnel` p ON pda.`personnel_id` = p.`id`
LEFT JOIN `cost_centers` cc ON pda.`cost_center_id` = cc.`id`
ORDER BY pda.`attendance_date`, pda.`adi_soyadi`;


-- =====================================================
-- 4. İzin Bakiye Tablosu
-- =====================================================

CREATE TABLE IF NOT EXISTS `personnel_leave_balance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `personnel_id` INT NOT NULL COMMENT 'personnel tablosu ID',
    `year` INT NOT NULL COMMENT 'Yıl (2025)',
    
    -- Yıllık İzin Hakları
    `annual_leave_entitlement` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Yıllık izin hakkı (gün)',
    `annual_leave_used` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Kullanılan yıllık izin (gün)',
    `annual_leave_balance` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Kalan yıllık izin (gün)',
    
    -- Geçen Yıldan Devir
    `previous_year_balance` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Geçen yıldan devir (gün)',
    
    -- Diğer İzinler (Kullanılan)
    `sick_leave_used` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Kullanılan rapor günü',
    `unpaid_leave_used` DECIMAL(5, 2) DEFAULT 0 COMMENT 'Kullanılan ücretsiz izin (gün)',
    `permit_hours_used` DECIMAL(6, 2) DEFAULT 0 COMMENT 'Kullanılan mazeret izni (saat)',
    
    -- Sistem
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (`personnel_id`) REFERENCES `personnel`(`id`) ON DELETE CASCADE,
    
    -- Unique Constraint
    UNIQUE KEY `uq_personnel_year` (`personnel_id`, `year`),
    
    -- Indexes
    INDEX `idx_leave_year` (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Personel yıllık izin bakiyeleri';


-- =====================================================
-- 5. Vardiya Tanımları
-- =====================================================

CREATE TABLE IF NOT EXISTS `shift_definitions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(20) UNIQUE NOT NULL COMMENT 'Vardiya kodu (SABAH, AKSAM, GECE)',
    `name` VARCHAR(100) NOT NULL COMMENT 'Vardiya adı',
    
    -- Mesai Saatleri
    `start_time` TIME NOT NULL COMMENT 'Başlangıç saati',
    `end_time` TIME NOT NULL COMMENT 'Bitiş saati',
    `break_minutes` INT DEFAULT 0 COMMENT 'Mola süresi (dakika)',
    
    -- Özellikler
    `is_night_shift` TINYINT(1) DEFAULT 0 COMMENT 'Gece vardiyası mı?',
    `overtime_multiplier` DECIMAL(3, 2) DEFAULT 1.00 COMMENT 'Fazla mesai çarpanı (1.5)',
    
    -- Durum
    `is_active` TINYINT(1) DEFAULT 1 COMMENT 'Aktif mi?',
    `display_order` INT DEFAULT 0 COMMENT 'Sıralama',
    
    -- Sistem
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX `idx_shift_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Vardiya tanımları';


-- =====================================================
-- 6. Varsayılan Vardiya Kayıtları
-- =====================================================

INSERT INTO `shift_definitions` (`code`, `name`, `start_time`, `end_time`, `break_minutes`, `is_night_shift`, `overtime_multiplier`, `display_order`) VALUES
('SABAH', 'Sabah Vardiyası', '08:00:00', '17:00:00', 60, 0, 1.00, 1),
('AKSAM', 'Akşam Vardiyası', '16:00:00', '00:00:00', 60, 0, 1.00, 2),
('GECE', 'Gece Vardiyası', '00:00:00', '08:00:00', 60, 1, 1.25, 3),
('NORMAL', 'Normal Mesai (8 Saat)', '09:00:00', '18:00:00', 60, 0, 1.00, 4),
('ESNEK', 'Esnek Çalışma', '09:00:00', '17:00:00', 0, 0, 1.00, 5)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);


-- =====================================================
-- 7. Takvim Yardımcı Tablo (Resmi Tatiller)
-- =====================================================

CREATE TABLE IF NOT EXISTS `calendar_holidays` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `holiday_date` DATE NOT NULL COMMENT 'Tatil tarihi',
    `year` INT NOT NULL COMMENT 'Yıl',
    `name` VARCHAR(200) NOT NULL COMMENT 'Tatil adı',
    `type` ENUM('RESMI_TATIL', 'DINI_BAYRAM', 'OZEL') DEFAULT 'RESMI_TATIL' COMMENT 'Tatil tipi',
    `is_paid` TINYINT(1) DEFAULT 1 COMMENT 'Ücretli tatil mi?',
    
    -- Sistem
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique Constraint
    UNIQUE KEY `uq_holiday_date` (`holiday_date`),
    
    -- Indexes
    INDEX `idx_holiday_year` (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Resmi tatil ve bayram günleri';


-- =====================================================
-- 8. 2025 Resmi Tatiller
-- =====================================================

INSERT INTO `calendar_holidays` (`holiday_date`, `year`, `name`, `type`, `is_paid`) VALUES
-- 2025 Resmi Tatiller
('2025-01-01', 2025, 'Yılbaşı', 'RESMI_TATIL', 1),
('2025-03-31', 2025, 'Ramazan Bayramı 1. Gün', 'DINI_BAYRAM', 1),
('2025-04-01', 2025, 'Ramazan Bayramı 2. Gün', 'DINI_BAYRAM', 1),
('2025-04-02', 2025, 'Ramazan Bayramı 3. Gün', 'DINI_BAYRAM', 1),
('2025-04-23', 2025, 'Ulusal Egemenlik ve Çocuk Bayramı', 'RESMI_TATIL', 1),
('2025-05-01', 2025, 'İşçi Bayramı', 'RESMI_TATIL', 1),
('2025-05-19', 2025, 'Gençlik ve Spor Bayramı', 'RESMI_TATIL', 1),
('2025-06-07', 2025, 'Kurban Bayramı 1. Gün', 'DINI_BAYRAM', 1),
('2025-06-08', 2025, 'Kurban Bayramı 2. Gün', 'DINI_BAYRAM', 1),
('2025-06-09', 2025, 'Kurban Bayramı 3. Gün', 'DINI_BAYRAM', 1),
('2025-06-10', 2025, 'Kurban Bayramı 4. Gün', 'DINI_BAYRAM', 1),
('2025-07-15', 2025, 'Demokrasi ve Milli Birlik Günü', 'RESMI_TATIL', 1),
('2025-08-30', 2025, 'Zafer Bayramı', 'RESMI_TATIL', 1),
('2025-10-29', 2025, 'Cumhuriyet Bayramı', 'RESMI_TATIL', 1)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);


-- =====================================================
-- 9. Trigger: Aylık özet otomatik güncelleme
-- =====================================================

DELIMITER //

CREATE TRIGGER `trg_attendance_after_insert`
AFTER INSERT ON `personnel_daily_attendance`
FOR EACH ROW
BEGIN
    -- İzin bakiyelerini güncelle
    INSERT INTO `personnel_leave_balance` (
        `personnel_id`, 
        `year`, 
        `annual_leave_used`,
        `sick_leave_used`,
        `unpaid_leave_used`
    )
    VALUES (
        NEW.`personnel_id`,
        NEW.`yil`,
        NEW.`yillik_izin`,
        NEW.`rapor`,
        NEW.`ucretsiz_izin`
    )
    ON DUPLICATE KEY UPDATE
        `annual_leave_used` = `annual_leave_used` + NEW.`yillik_izin`,
        `sick_leave_used` = `sick_leave_used` + NEW.`rapor`,
        `unpaid_leave_used` = `unpaid_leave_used` + NEW.`ucretsiz_izin`,
        `annual_leave_balance` = `annual_leave_entitlement` + `previous_year_balance` - `annual_leave_used`;
END//

DELIMITER ;


-- =====================================================
-- Tamamlandı
-- =====================================================

SELECT 'Takvimli puantaj sistemi başarıyla oluşturuldu!' as message;
