-- Doğum tarihi, meslek kodu ve meslek adı sütunları ekle
ALTER TABLE monthly_personnel_records
ADD COLUMN dogum_tarihi DATE NULL COMMENT 'Doğum tarihi' AFTER isten_cikis_tarihi,
ADD COLUMN meslek_kodu VARCHAR(20) NULL COMMENT 'Luca meslek kodu' AFTER meslek_adi,
ADD COLUMN sgk_no VARCHAR(50) NULL COMMENT 'SSK/SGK numarası' AFTER meslek_kodu;

-- Index ekle (yaş hesaplamaları için)
CREATE INDEX idx_monthly_personnel_dogum_tarihi 
ON monthly_personnel_records(dogum_tarihi);

-- Meslek kodu index
CREATE INDEX idx_monthly_personnel_meslek_kodu
ON monthly_personnel_records(meslek_kodu);
