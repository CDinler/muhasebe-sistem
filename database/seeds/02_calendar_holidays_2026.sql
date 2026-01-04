-- 2026 Türkiye Resmi Tatil Günleri
-- Tarih: 3 Ocak 2026

USE muhasebe_sistem;

-- Önce mevcut 2026 tatillerini temizle (varsa)
DELETE FROM calendar_holidays WHERE year = 2026;

-- 2026 Resmi Tatilleri
INSERT INTO calendar_holidays (holiday_date, year, name, type) VALUES
-- Yılbaşı
('2026-01-01', 2026, 'Yılbaşı', 'RESMI_TATIL'),

-- Ulusal Egemenlik ve Çocuk Bayramı
('2026-04-23', 2026, 'Ulusal Egemenlik ve Çocuk Bayramı', 'RESMI_TATIL'),

-- Emek ve Dayanışma Günü
('2026-05-01', 2026, 'Emek ve Dayanışma Günü', 'RESMI_TATIL'),

-- Gençlik ve Spor Bayramı
('2026-05-19', 2026, 'Gençlik ve Spor Bayramı', 'RESMI_TATIL'),

-- Ramazan Bayramı (tahmini: 31 Mart - 3 Nisan 2026)
-- Not: Resmi açıklama gelince güncellenecek
('2026-03-31', 2026, 'Ramazan Bayramı Arife (Yarım Gün)', 'DINI_BAYRAM'),
('2026-04-01', 2026, 'Ramazan Bayramı 1. Gün', 'DINI_BAYRAM'),
('2026-04-02', 2026, 'Ramazan Bayramı 2. Gün', 'DINI_BAYRAM'),
('2026-04-03', 2026, 'Ramazan Bayramı 3. Gün', 'DINI_BAYRAM'),

-- Kurban Bayramı (tahmini: 7-11 Haziran 2026)
-- Not: Resmi açıklama gelince güncellenecek
('2026-06-07', 2026, 'Kurban Bayramı Arife (Yarım Gün)', 'DINI_BAYRAM'),
('2026-06-08', 2026, 'Kurban Bayramı 1. Gün', 'DINI_BAYRAM'),
('2026-06-09', 2026, 'Kurban Bayramı 2. Gün', 'DINI_BAYRAM'),
('2026-06-10', 2026, 'Kurban Bayramı 3. Gün', 'DINI_BAYRAM'),
('2026-06-11', 2026, 'Kurban Bayramı 4. Gün', 'DINI_BAYRAM'),

-- Zafer Bayramı
('2026-08-30', 2026, 'Zafer Bayramı', 'RESMI_TATIL'),

-- Cumhuriyet Bayramı
('2026-10-29', 2026, 'Cumhuriyet Bayramı', 'RESMI_TATIL');

-- Kontrol
SELECT 
    holiday_date,
    name,
    type,
    DAYNAME(holiday_date) as gun_adi
FROM calendar_holidays 
WHERE year = 2026
ORDER BY holiday_date;

SELECT COUNT(*) as toplam_tatil_gunu FROM calendar_holidays WHERE year = 2026;
