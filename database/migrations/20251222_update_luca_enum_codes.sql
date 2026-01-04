-- Luca Puantaj Kodlarına Uyumlu Hale Getirme
-- personnel_daily_attendance tablosundaki ENUM'ları Luca ile uyumlu yap

USE muhasebe_sistem;

-- Önce mevcut ENUM değerlerini kontrol et
SELECT COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'muhasebe_sistem' 
  AND TABLE_NAME = 'personnel_daily_attendance' 
  AND COLUMN_NAME IN ('calisma_durumu', 'gun_tipi');

-- calisma_durumu ENUM'unu Luca kodlarıyla değiştir
ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN calisma_durumu ENUM(
  'N',  -- Normal
  'H',  -- Hafta Tatili
  'T',  -- Resmi Tatil
  'İ',  -- İzinli
  'S',  -- Yıllık İzin
  'R',  -- Raporlu
  'E',  -- Eksik Gün
  'Y',  -- Yarım Gün
  'G',  -- Gece Mesaisi
  'O',  -- Gündüz Mesaisi
  'K',  -- Yarım Gün Resmi Tatil
  'C'   -- Yarım Gün Hafta Tatili
) DEFAULT NULL COMMENT 'Luca uyumlu çalışma durumu kodları';

-- gun_1 .. gun_31 kolonlarını da aynı ENUM ile güncelle
ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_1 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_2 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_3 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_4 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_5 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_6 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_7 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_8 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_9 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_10 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_11 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_12 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_13 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_14 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_15 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_16 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_17 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_18 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_19 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_20 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_21 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_22 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_23 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_24 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_25 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_26 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_27 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_28 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_29 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_30 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

ALTER TABLE personnel_daily_attendance 
MODIFY COLUMN gun_31 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL;

-- Kontrol et
SELECT COLUMN_NAME, COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'muhasebe_sistem' 
  AND TABLE_NAME = 'personnel_daily_attendance' 
  AND COLUMN_NAME LIKE 'gun_%';

SELECT 'Migration completed successfully - Luca uyumlu ENUM kodları güncellendi' AS sonuc;
