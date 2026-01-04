-- Fazla mesai kolonları ekleme
-- 2025-12-22: Puantaj grid tablosuna fazla mesai saatleri için kolonlar ekleniyor

USE muhasebe_sistem;

-- Fazla mesai kolonları (fm = Fazla Mesai)
ALTER TABLE personnel_puantaj_grid
ADD COLUMN fm_gun_1 DECIMAL(4,1) DEFAULT NULL AFTER gun_1,
ADD COLUMN fm_gun_2 DECIMAL(4,1) DEFAULT NULL AFTER gun_2,
ADD COLUMN fm_gun_3 DECIMAL(4,1) DEFAULT NULL AFTER gun_3,
ADD COLUMN fm_gun_4 DECIMAL(4,1) DEFAULT NULL AFTER gun_4,
ADD COLUMN fm_gun_5 DECIMAL(4,1) DEFAULT NULL AFTER gun_5,
ADD COLUMN fm_gun_6 DECIMAL(4,1) DEFAULT NULL AFTER gun_6,
ADD COLUMN fm_gun_7 DECIMAL(4,1) DEFAULT NULL AFTER gun_7,
ADD COLUMN fm_gun_8 DECIMAL(4,1) DEFAULT NULL AFTER gun_8,
ADD COLUMN fm_gun_9 DECIMAL(4,1) DEFAULT NULL AFTER gun_9,
ADD COLUMN fm_gun_10 DECIMAL(4,1) DEFAULT NULL AFTER gun_10,
ADD COLUMN fm_gun_11 DECIMAL(4,1) DEFAULT NULL AFTER gun_11,
ADD COLUMN fm_gun_12 DECIMAL(4,1) DEFAULT NULL AFTER gun_12,
ADD COLUMN fm_gun_13 DECIMAL(4,1) DEFAULT NULL AFTER gun_13,
ADD COLUMN fm_gun_14 DECIMAL(4,1) DEFAULT NULL AFTER gun_14,
ADD COLUMN fm_gun_15 DECIMAL(4,1) DEFAULT NULL AFTER gun_15,
ADD COLUMN fm_gun_16 DECIMAL(4,1) DEFAULT NULL AFTER gun_16,
ADD COLUMN fm_gun_17 DECIMAL(4,1) DEFAULT NULL AFTER gun_17,
ADD COLUMN fm_gun_18 DECIMAL(4,1) DEFAULT NULL AFTER gun_18,
ADD COLUMN fm_gun_19 DECIMAL(4,1) DEFAULT NULL AFTER gun_19,
ADD COLUMN fm_gun_20 DECIMAL(4,1) DEFAULT NULL AFTER gun_20,
ADD COLUMN fm_gun_21 DECIMAL(4,1) DEFAULT NULL AFTER gun_21,
ADD COLUMN fm_gun_22 DECIMAL(4,1) DEFAULT NULL AFTER gun_22,
ADD COLUMN fm_gun_23 DECIMAL(4,1) DEFAULT NULL AFTER gun_23,
ADD COLUMN fm_gun_24 DECIMAL(4,1) DEFAULT NULL AFTER gun_24,
ADD COLUMN fm_gun_25 DECIMAL(4,1) DEFAULT NULL AFTER gun_25,
ADD COLUMN fm_gun_26 DECIMAL(4,1) DEFAULT NULL AFTER gun_26,
ADD COLUMN fm_gun_27 DECIMAL(4,1) DEFAULT NULL AFTER gun_27,
ADD COLUMN fm_gun_28 DECIMAL(4,1) DEFAULT NULL AFTER gun_28,
ADD COLUMN fm_gun_29 DECIMAL(4,1) DEFAULT NULL AFTER gun_29,
ADD COLUMN fm_gun_30 DECIMAL(4,1) DEFAULT NULL AFTER gun_30,
ADD COLUMN fm_gun_31 DECIMAL(4,1) DEFAULT NULL AFTER gun_31;

-- Toplam fazla mesai kolonu
ALTER TABLE personnel_puantaj_grid
ADD COLUMN toplam_fm DECIMAL(5,1) DEFAULT 0 AFTER yarim_gun;

-- Trigger'ları güncelle - toplam FM hesapla
DROP TRIGGER IF EXISTS personnel_puantaj_grid_before_insert;
DROP TRIGGER IF EXISTS personnel_puantaj_grid_before_update;

DELIMITER $$

CREATE TRIGGER personnel_puantaj_grid_before_insert
BEFORE INSERT ON personnel_puantaj_grid
FOR EACH ROW
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE calisilan INT DEFAULT 0;
    DECLARE ssk INT DEFAULT 0;
    DECLARE izin INT DEFAULT 0;
    DECLARE eksik INT DEFAULT 0;
    DECLARE yarim INT DEFAULT 0;
    DECLARE fm_toplam DECIMAL(5,1) DEFAULT 0;
    DECLARE gun_value VARCHAR(2);
    DECLARE fm_value DECIMAL(4,1);
    
    WHILE i <= 31 DO
        SET gun_value = CASE i
            WHEN 1 THEN NEW.gun_1 WHEN 2 THEN NEW.gun_2 WHEN 3 THEN NEW.gun_3
            WHEN 4 THEN NEW.gun_4 WHEN 5 THEN NEW.gun_5 WHEN 6 THEN NEW.gun_6
            WHEN 7 THEN NEW.gun_7 WHEN 8 THEN NEW.gun_8 WHEN 9 THEN NEW.gun_9
            WHEN 10 THEN NEW.gun_10 WHEN 11 THEN NEW.gun_11 WHEN 12 THEN NEW.gun_12
            WHEN 13 THEN NEW.gun_13 WHEN 14 THEN NEW.gun_14 WHEN 15 THEN NEW.gun_15
            WHEN 16 THEN NEW.gun_16 WHEN 17 THEN NEW.gun_17 WHEN 18 THEN NEW.gun_18
            WHEN 19 THEN NEW.gun_19 WHEN 20 THEN NEW.gun_20 WHEN 21 THEN NEW.gun_21
            WHEN 22 THEN NEW.gun_22 WHEN 23 THEN NEW.gun_23 WHEN 24 THEN NEW.gun_24
            WHEN 25 THEN NEW.gun_25 WHEN 26 THEN NEW.gun_26 WHEN 27 THEN NEW.gun_27
            WHEN 28 THEN NEW.gun_28 WHEN 29 THEN NEW.gun_29 WHEN 30 THEN NEW.gun_30
            WHEN 31 THEN NEW.gun_31
        END;
        
        SET fm_value = CASE i
            WHEN 1 THEN NEW.fm_gun_1 WHEN 2 THEN NEW.fm_gun_2 WHEN 3 THEN NEW.fm_gun_3
            WHEN 4 THEN NEW.fm_gun_4 WHEN 5 THEN NEW.fm_gun_5 WHEN 6 THEN NEW.fm_gun_6
            WHEN 7 THEN NEW.fm_gun_7 WHEN 8 THEN NEW.fm_gun_8 WHEN 9 THEN NEW.fm_gun_9
            WHEN 10 THEN NEW.fm_gun_10 WHEN 11 THEN NEW.fm_gun_11 WHEN 12 THEN NEW.fm_gun_12
            WHEN 13 THEN NEW.fm_gun_13 WHEN 14 THEN NEW.fm_gun_14 WHEN 15 THEN NEW.fm_gun_15
            WHEN 16 THEN NEW.fm_gun_16 WHEN 17 THEN NEW.fm_gun_17 WHEN 18 THEN NEW.fm_gun_18
            WHEN 19 THEN NEW.fm_gun_19 WHEN 20 THEN NEW.fm_gun_20 WHEN 21 THEN NEW.fm_gun_21
            WHEN 22 THEN NEW.fm_gun_22 WHEN 23 THEN NEW.fm_gun_23 WHEN 24 THEN NEW.fm_gun_24
            WHEN 25 THEN NEW.fm_gun_25 WHEN 26 THEN NEW.fm_gun_26 WHEN 27 THEN NEW.fm_gun_27
            WHEN 28 THEN NEW.fm_gun_28 WHEN 29 THEN NEW.fm_gun_29 WHEN 30 THEN NEW.fm_gun_30
            WHEN 31 THEN NEW.fm_gun_31
        END;
        
        -- Çalışılan günler (N=Normal, G=Gece, O=Off-day çalışma)
        IF gun_value IN ('N', 'G', 'O') THEN
            SET calisilan = calisilan + 1;
        END IF;
        
        -- SSK günleri (N, G, O, İ, S)
        IF gun_value IN ('N', 'G', 'O', 'İ', 'S') THEN
            SET ssk = ssk + 1;
        END IF;
        
        -- İzin günleri (İ=Ücretli, S=Ücretsiz)
        IF gun_value IN ('İ', 'S') THEN
            SET izin = izin + 1;
        END IF;
        
        -- Eksik günler (E=Eksik)
        IF gun_value = 'E' THEN
            SET eksik = eksik + 1;
        END IF;
        
        -- Yarım günler (Y=Yarım)
        IF gun_value = 'Y' THEN
            SET yarim = yarim + 1;
        END IF;
        
        -- Fazla mesai toplamı
        IF fm_value IS NOT NULL THEN
            SET fm_toplam = fm_toplam + fm_value;
        END IF;
        
        SET i = i + 1;
    END WHILE;
    
    SET NEW.calisilan_gun = calisilan;
    SET NEW.ssk_gun = ssk;
    SET NEW.izin_gun = izin;
    SET NEW.eksik_gun = eksik;
    SET NEW.yarim_gun = yarim;
    SET NEW.toplam_fm = fm_toplam;
END$$

CREATE TRIGGER personnel_puantaj_grid_before_update
BEFORE UPDATE ON personnel_puantaj_grid
FOR EACH ROW
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE calisilan INT DEFAULT 0;
    DECLARE ssk INT DEFAULT 0;
    DECLARE izin INT DEFAULT 0;
    DECLARE eksik INT DEFAULT 0;
    DECLARE yarim INT DEFAULT 0;
    DECLARE fm_toplam DECIMAL(5,1) DEFAULT 0;
    DECLARE gun_value VARCHAR(2);
    DECLARE fm_value DECIMAL(4,1);
    
    WHILE i <= 31 DO
        SET gun_value = CASE i
            WHEN 1 THEN NEW.gun_1 WHEN 2 THEN NEW.gun_2 WHEN 3 THEN NEW.gun_3
            WHEN 4 THEN NEW.gun_4 WHEN 5 THEN NEW.gun_5 WHEN 6 THEN NEW.gun_6
            WHEN 7 THEN NEW.gun_7 WHEN 8 THEN NEW.gun_8 WHEN 9 THEN NEW.gun_9
            WHEN 10 THEN NEW.gun_10 WHEN 11 THEN NEW.gun_11 WHEN 12 THEN NEW.gun_12
            WHEN 13 THEN NEW.gun_13 WHEN 14 THEN NEW.gun_14 WHEN 15 THEN NEW.gun_15
            WHEN 16 THEN NEW.gun_16 WHEN 17 THEN NEW.gun_17 WHEN 18 THEN NEW.gun_18
            WHEN 19 THEN NEW.gun_19 WHEN 20 THEN NEW.gun_20 WHEN 21 THEN NEW.gun_21
            WHEN 22 THEN NEW.gun_22 WHEN 23 THEN NEW.gun_23 WHEN 24 THEN NEW.gun_24
            WHEN 25 THEN NEW.gun_25 WHEN 26 THEN NEW.gun_26 WHEN 27 THEN NEW.gun_27
            WHEN 28 THEN NEW.gun_28 WHEN 29 THEN NEW.gun_29 WHEN 30 THEN NEW.gun_30
            WHEN 31 THEN NEW.gun_31
        END;
        
        SET fm_value = CASE i
            WHEN 1 THEN NEW.fm_gun_1 WHEN 2 THEN NEW.fm_gun_2 WHEN 3 THEN NEW.fm_gun_3
            WHEN 4 THEN NEW.fm_gun_4 WHEN 5 THEN NEW.fm_gun_5 WHEN 6 THEN NEW.fm_gun_6
            WHEN 7 THEN NEW.fm_gun_7 WHEN 8 THEN NEW.fm_gun_8 WHEN 9 THEN NEW.fm_gun_9
            WHEN 10 THEN NEW.fm_gun_10 WHEN 11 THEN NEW.fm_gun_11 WHEN 12 THEN NEW.fm_gun_12
            WHEN 13 THEN NEW.fm_gun_13 WHEN 14 THEN NEW.fm_gun_14 WHEN 15 THEN NEW.fm_gun_15
            WHEN 16 THEN NEW.fm_gun_16 WHEN 17 THEN NEW.fm_gun_17 WHEN 18 THEN NEW.fm_gun_18
            WHEN 19 THEN NEW.fm_gun_19 WHEN 20 THEN NEW.fm_gun_20 WHEN 21 THEN NEW.fm_gun_21
            WHEN 22 THEN NEW.fm_gun_22 WHEN 23 THEN NEW.fm_gun_23 WHEN 24 THEN NEW.fm_gun_24
            WHEN 25 THEN NEW.fm_gun_25 WHEN 26 THEN NEW.fm_gun_26 WHEN 27 THEN NEW.fm_gun_27
            WHEN 28 THEN NEW.fm_gun_28 WHEN 29 THEN NEW.fm_gun_29 WHEN 30 THEN NEW.fm_gun_30
            WHEN 31 THEN NEW.fm_gun_31
        END;
        
        IF gun_value IN ('N', 'G', 'O') THEN
            SET calisilan = calisilan + 1;
        END IF;
        
        IF gun_value IN ('N', 'G', 'O', 'İ', 'S') THEN
            SET ssk = ssk + 1;
        END IF;
        
        IF gun_value IN ('İ', 'S') THEN
            SET izin = izin + 1;
        END IF;
        
        IF gun_value = 'E' THEN
            SET eksik = eksik + 1;
        END IF;
        
        IF gun_value = 'Y' THEN
            SET yarim = yarim + 1;
        END IF;
        
        IF fm_value IS NOT NULL THEN
            SET fm_toplam = fm_toplam + fm_value;
        END IF;
        
        SET i = i + 1;
    END WHILE;
    
    SET NEW.calisilan_gun = calisilan;
    SET NEW.ssk_gun = ssk;
    SET NEW.izin_gun = izin;
    SET NEW.eksik_gun = eksik;
    SET NEW.yarim_gun = yarim;
    SET NEW.toplam_fm = fm_toplam;
END$$

DELIMITER ;

-- Test personeli ekle (Ahmet Yılmaz - 2025 Ocak dönemi için örnek veri)
INSERT INTO personnel_puantaj_grid (
    personnel_id, donem, sicil_no, adi_soyadi,
    gun_1, fm_gun_1, gun_2, fm_gun_2, gun_3, fm_gun_3, gun_4, fm_gun_4, gun_5, fm_gun_5,
    gun_6, gun_7, gun_8, fm_gun_8, gun_9, fm_gun_9, gun_10, fm_gun_10,
    gun_11, gun_12, gun_13, fm_gun_13, gun_14, gun_15, gun_16, fm_gun_16,
    gun_17, gun_18, gun_19, gun_20, fm_gun_20, gun_21, gun_22, fm_gun_22,
    gun_23, gun_24, gun_25, gun_26, gun_27, gun_28, gun_29, gun_30, gun_31
) VALUES (
    (SELECT id FROM personnel WHERE sicil_no = '00001' LIMIT 1),
    '2025-01',
    '00001',
    'TEST PERSONEL',
    -- Hafta 1: 1-5 Ocak (Ça-Pz)
    'N', 2.0,  -- 1 Ça - Normal + 2 FM
    'N', 1.5,  -- 2 Pe - Normal + 1.5 FM
    'N', NULL, -- 3 Cu - Normal
    'H', NULL, -- 4 Ct - Hafta tatili
    'H', NULL, -- 5 Pz - Hafta tatili
    -- Hafta 2: 6-12 Ocak (Pt-Pz)
    'N', NULL, -- 6 Pt - Normal
    'N', NULL, -- 7 Sa - Normal
    'N', 3.0,  -- 8 Ça - Normal + 3 FM
    'N', 2.5,  -- 9 Pe - Normal + 2.5 FM
    'N', 4.0,  -- 10 Cu - Normal + 4 FM
    'H', NULL, -- 11 Ct - Hafta tatili
    'H', NULL, -- 12 Pz - Hafta tatili
    -- Hafta 3: 13-19 Ocak (Pt-Pz)
    'N', 1.0,  -- 13 Pt - Normal + 1 FM
    'N', NULL, -- 14 Sa - Normal
    'N', NULL, -- 15 Ça - Normal
    'İ', NULL, -- 16 Pe - Ücretli izin
    'İ', NULL, -- 17 Cu - Ücretli izin
    'H', NULL, -- 18 Ct - Hafta tatili
    'H', NULL, -- 19 Pz - Hafta tatili
    -- Hafta 4: 20-26 Ocak (Pt-Pz)
    'N', 2.0,  -- 20 Pt - Normal + 2 FM
    'N', NULL, -- 21 Sa - Normal
    'N', 1.5,  -- 22 Ça - Normal + 1.5 FM
    'N', NULL, -- 23 Pe - Normal
    'N', NULL, -- 24 Cu - Normal
    'H', NULL, -- 25 Ct - Hafta tatili
    'H', NULL, -- 26 Pz - Hafta tatili
    -- Son günler: 27-31 Ocak (Pt-Cu)
    'N', NULL, -- 27 Pt - Normal
    'N', NULL, -- 28 Sa - Normal
    'N', NULL, -- 29 Ça - Normal
    'N', NULL, -- 30 Pe - Normal
    'N', NULL  -- 31 Cu - Normal
) ON DUPLICATE KEY UPDATE
    gun_1='N', fm_gun_1=2.0, gun_2='N', fm_gun_2=1.5, gun_3='N', fm_gun_3=NULL,
    gun_4='H', gun_5='H', gun_6='N', gun_7='N',
    gun_8='N', fm_gun_8=3.0, gun_9='N', fm_gun_9=2.5, gun_10='N', fm_gun_10=4.0,
    gun_11='H', gun_12='H', gun_13='N', fm_gun_13=1.0, gun_14='N',
    gun_15='N', gun_16='İ', gun_17='İ', gun_18='H', gun_19='H',
    gun_20='N', fm_gun_20=2.0, gun_21='N', gun_22='N', fm_gun_22=1.5,
    gun_23='N', gun_24='N', gun_25='H', gun_26='H',
    gun_27='N', gun_28='N', gun_29='N', gun_30='N', gun_31='N';

SELECT 'Migration completed successfully!' as status;
SELECT 'Test personel eklendi: 00001 - TEST PERSONEL (2025-01)' as message;
SELECT CONCAT('Toplam FM: ', toplam_fm, ' saat') as fm_info 
FROM personnel_puantaj_grid 
WHERE sicil_no = '00001' AND donem = '2025-01';
