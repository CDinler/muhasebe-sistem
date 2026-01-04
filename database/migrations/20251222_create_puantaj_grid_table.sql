-- Excel Benzeri Puantaj Tablosu
-- Her personel-dönem bir satır, 31 günlük kolonlar

CREATE TABLE IF NOT EXISTS personnel_puantaj_grid (
  id INT AUTO_INCREMENT PRIMARY KEY,
  
  -- Personel Bilgisi
  personnel_id INT NOT NULL,
  donem VARCHAR(7) NOT NULL COMMENT 'YYYY-MM formatında',
  yil INT NOT NULL,
  ay INT NOT NULL,
  
  -- 31 Günlük Kolonlar (Luca uyumlu ENUM kodları)
  gun_1 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_2 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_3 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_4 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_5 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_6 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_7 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_8 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_9 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_10 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_11 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_12 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_13 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_14 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_15 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_16 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_17 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_18 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_19 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_20 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_21 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_22 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_23 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_24 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_25 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_26 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_27 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_28 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_29 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_30 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  gun_31 ENUM('N','H','T','İ','S','R','E','Y','G','O','K','C') DEFAULT NULL,
  
  -- Özet Alanlar (trigger ile otomatik hesaplanacak)
  calisilan_gun_sayisi INT DEFAULT 0 COMMENT 'N, G, O kodlarının toplamı',
  ssk_gun_sayisi INT DEFAULT 0,
  yillik_izin_gun INT DEFAULT 0 COMMENT 'S kodlarının toplamı',
  izin_gun_sayisi INT DEFAULT 0 COMMENT 'İ kodlarının toplamı',
  rapor_gun_sayisi INT DEFAULT 0 COMMENT 'R kodlarının toplamı',
  eksik_gun_sayisi INT DEFAULT 0 COMMENT 'E kodlarının toplamı',
  yarim_gun_sayisi DECIMAL(3,1) DEFAULT 0 COMMENT 'Y, K, C kodlarının toplamı (0.5 olarak)',
  toplam_gun_sayisi INT DEFAULT 0,
  
  -- Timestamp
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- İndeksler
  INDEX idx_personnel_donem (personnel_id, donem),
  INDEX idx_donem (donem),
  INDEX idx_yil_ay (yil, ay),
  UNIQUE KEY uk_personnel_donem (personnel_id, donem),
  
  -- Foreign Key
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE
  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Excel benzeri puantaj girişi - her personel-dönem bir satır';

-- Özet alanları otomatik hesaplayan trigger
DELIMITER //

CREATE TRIGGER trg_puantaj_grid_calculate
BEFORE INSERT ON personnel_puantaj_grid
FOR EACH ROW
BEGIN
  DECLARE i INT DEFAULT 1;
  DECLARE gun_kodu VARCHAR(1);
  DECLARE calisilan INT DEFAULT 0;
  DECLARE izin INT DEFAULT 0;
  DECLARE yillik INT DEFAULT 0;
  DECLARE rapor INT DEFAULT 0;
  DECLARE eksik INT DEFAULT 0;
  DECLARE yarim DECIMAL(3,1) DEFAULT 0;
  
  -- 31 günü döngü ile kontrol et
  WHILE i <= 31 DO
    SET gun_kodu = CASE i
      WHEN 1 THEN NEW.gun_1
      WHEN 2 THEN NEW.gun_2
      WHEN 3 THEN NEW.gun_3
      WHEN 4 THEN NEW.gun_4
      WHEN 5 THEN NEW.gun_5
      WHEN 6 THEN NEW.gun_6
      WHEN 7 THEN NEW.gun_7
      WHEN 8 THEN NEW.gun_8
      WHEN 9 THEN NEW.gun_9
      WHEN 10 THEN NEW.gun_10
      WHEN 11 THEN NEW.gun_11
      WHEN 12 THEN NEW.gun_12
      WHEN 13 THEN NEW.gun_13
      WHEN 14 THEN NEW.gun_14
      WHEN 15 THEN NEW.gun_15
      WHEN 16 THEN NEW.gun_16
      WHEN 17 THEN NEW.gun_17
      WHEN 18 THEN NEW.gun_18
      WHEN 19 THEN NEW.gun_19
      WHEN 20 THEN NEW.gun_20
      WHEN 21 THEN NEW.gun_21
      WHEN 22 THEN NEW.gun_22
      WHEN 23 THEN NEW.gun_23
      WHEN 24 THEN NEW.gun_24
      WHEN 25 THEN NEW.gun_25
      WHEN 26 THEN NEW.gun_26
      WHEN 27 THEN NEW.gun_27
      WHEN 28 THEN NEW.gun_28
      WHEN 29 THEN NEW.gun_29
      WHEN 30 THEN NEW.gun_30
      WHEN 31 THEN NEW.gun_31
    END;
    
    IF gun_kodu IN ('N', 'G', 'O') THEN
      SET calisilan = calisilan + 1;
    END IF;
    
    IF gun_kodu = 'İ' THEN
      SET izin = izin + 1;
    END IF;
    
    IF gun_kodu = 'S' THEN
      SET yillik = yillik + 1;
    END IF;
    
    IF gun_kodu = 'R' THEN
      SET rapor = rapor + 1;
    END IF;
    
    IF gun_kodu = 'E' THEN
      SET eksik = eksik + 1;
    END IF;
    
    IF gun_kodu IN ('Y', 'K', 'C') THEN
      SET yarim = yarim + 0.5;
    END IF;
    
    SET i = i + 1;
  END WHILE;
  
  SET NEW.calisilan_gun_sayisi = calisilan;
  SET NEW.izin_gun_sayisi = izin;
  SET NEW.yillik_izin_gun = yillik;
  SET NEW.rapor_gun_sayisi = rapor;
  SET NEW.eksik_gun_sayisi = eksik;
  SET NEW.yarim_gun_sayisi = yarim;
  SET NEW.ssk_gun_sayisi = calisilan + yillik + izin;
  SET NEW.toplam_gun_sayisi = calisilan + yillik + izin + rapor;
END//

-- UPDATE trigger
CREATE TRIGGER trg_puantaj_grid_update
BEFORE UPDATE ON personnel_puantaj_grid
FOR EACH ROW
BEGIN
  DECLARE i INT DEFAULT 1;
  DECLARE gun_kodu VARCHAR(1);
  DECLARE calisilan INT DEFAULT 0;
  DECLARE izin INT DEFAULT 0;
  DECLARE yillik INT DEFAULT 0;
  DECLARE rapor INT DEFAULT 0;
  DECLARE eksik INT DEFAULT 0;
  DECLARE yarim DECIMAL(3,1) DEFAULT 0;
  
  WHILE i <= 31 DO
    SET gun_kodu = CASE i
      WHEN 1 THEN NEW.gun_1
      WHEN 2 THEN NEW.gun_2
      WHEN 3 THEN NEW.gun_3
      WHEN 4 THEN NEW.gun_4
      WHEN 5 THEN NEW.gun_5
      WHEN 6 THEN NEW.gun_6
      WHEN 7 THEN NEW.gun_7
      WHEN 8 THEN NEW.gun_8
      WHEN 9 THEN NEW.gun_9
      WHEN 10 THEN NEW.gun_10
      WHEN 11 THEN NEW.gun_11
      WHEN 12 THEN NEW.gun_12
      WHEN 13 THEN NEW.gun_13
      WHEN 14 THEN NEW.gun_14
      WHEN 15 THEN NEW.gun_15
      WHEN 16 THEN NEW.gun_16
      WHEN 17 THEN NEW.gun_17
      WHEN 18 THEN NEW.gun_18
      WHEN 19 THEN NEW.gun_19
      WHEN 20 THEN NEW.gun_20
      WHEN 21 THEN NEW.gun_21
      WHEN 22 THEN NEW.gun_22
      WHEN 23 THEN NEW.gun_23
      WHEN 24 THEN NEW.gun_24
      WHEN 25 THEN NEW.gun_25
      WHEN 26 THEN NEW.gun_26
      WHEN 27 THEN NEW.gun_27
      WHEN 28 THEN NEW.gun_28
      WHEN 29 THEN NEW.gun_29
      WHEN 30 THEN NEW.gun_30
      WHEN 31 THEN NEW.gun_31
    END;
    
    IF gun_kodu IN ('N', 'G', 'O') THEN SET calisilan = calisilan + 1; END IF;
    IF gun_kodu = 'İ' THEN SET izin = izin + 1; END IF;
    IF gun_kodu = 'S' THEN SET yillik = yillik + 1; END IF;
    IF gun_kodu = 'R' THEN SET rapor = rapor + 1; END IF;
    IF gun_kodu = 'E' THEN SET eksik = eksik + 1; END IF;
    IF gun_kodu IN ('Y', 'K', 'C') THEN SET yarim = yarim + 0.5; END IF;
    
    SET i = i + 1;
  END WHILE;
  
  SET NEW.calisilan_gun_sayisi = calisilan;
  SET NEW.izin_gun_sayisi = izin;
  SET NEW.yillik_izin_gun = yillik;
  SET NEW.rapor_gun_sayisi = rapor;
  SET NEW.eksik_gun_sayisi = eksik;
  SET NEW.yarim_gun_sayisi = yarim;
  SET NEW.ssk_gun_sayisi = calisilan + yillik + izin;
  SET NEW.toplam_gun_sayisi = calisilan + yillik + izin + rapor;
END//

DELIMITER ;

SELECT 'Tablo oluşturuldu: personnel_puantaj_grid' AS sonuc;
