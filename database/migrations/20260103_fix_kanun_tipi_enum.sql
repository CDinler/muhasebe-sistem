-- Fix kanun_tipi enum values in personnel_contracts
-- Tarih: 3 Ocak 2026

USE muhasebe_sistem;

-- Mevcut değerleri kontrol et
SELECT DISTINCT kanun_tipi, COUNT(*) as adet 
FROM personnel_contracts 
GROUP BY kanun_tipi;

-- '05510' -> 'K05510_TABI' olarak güncelle
UPDATE personnel_contracts 
SET kanun_tipi = 'K05510_TABI' 
WHERE kanun_tipi = '05510';

-- '00000' -> 'K05510_DEGIL' olarak güncelle
UPDATE personnel_contracts 
SET kanun_tipi = 'K05510_DEGIL' 
WHERE kanun_tipi = '00000';

-- 'EMEKLI' zaten doğru, dokunma

-- NULL olanları varsayılan olarak K05510_TABI yap
UPDATE personnel_contracts 
SET kanun_tipi = 'K05510_TABI' 
WHERE kanun_tipi IS NULL;

-- Sonucu kontrol et
SELECT DISTINCT kanun_tipi, COUNT(*) as adet 
FROM personnel_contracts 
GROUP BY kanun_tipi;
