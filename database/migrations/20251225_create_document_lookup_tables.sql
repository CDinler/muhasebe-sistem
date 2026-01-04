-- ============================================================================
-- EVRAK SINIFLANDIRMA LOOKUP TABLOLARI
-- Oluşturma Tarihi: 2024-12-25
-- Amaç: document_type ve document_subtype için referans tabloları
-- ============================================================================

-- 1. Ana Evrak Tipleri Tablosu
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE COMMENT 'Kısa kod (ör: SATIS_FATURA)',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Tam açıklama (ör: Satış Faturası)',
    category VARCHAR(50) NOT NULL COMMENT 'Kategori: FATURA, KASA, BANKA, PERSONEL, VERGI, DIGER',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Alt Evrak Tipleri Tablosu
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_subtypes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE COMMENT 'Kısa kod (ör: E_FATURA)',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Tam açıklama (ör: E-Fatura)',
    category VARCHAR(50) NOT NULL COMMENT 'Kategori: E_BELGE, KASA, BANKA, DIGER',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Ana Evrak Verileri
-- ============================================================================
INSERT INTO document_types (code, name, category, sort_order) VALUES
-- FATURA Kategorisi
('ALIS_FATURA', 'Alış Faturası', 'FATURA', 10),
('SATIS_FATURA', 'Satış Faturası', 'FATURA', 20),
('PROFORMA_FATURA', 'Proforma Fatura', 'FATURA', 30),
('IADE_FATURA', 'İade Faturası', 'FATURA', 40),

-- BANKA Kategorisi
('BANKA_TEDIYE', 'Banka Tediye Fişi', 'BANKA', 100),
('BANKA_TAHSILAT', 'Banka Tahsilat Fişi', 'BANKA', 110),
('BANKA_VIRMAN', 'Banka Virman', 'BANKA', 120),
('KREDI_KARTI_ODEME', 'Kredi Kartı Ödeme', 'BANKA', 130),

-- KASA Kategorisi
('KASA_TEDIYE', 'Kasa Tediye Fişi', 'KASA', 200),
('KASA_TAHSILAT', 'Kasa Tahsilat Fişi', 'KASA', 210),

-- ÇEK/SENET Kategorisi
('ALINAN_CEK', 'Alınan Çek', 'CEK_SENET', 300),
('VERILEN_CEK', 'Verilen Çek', 'CEK_SENET', 310),
('ALINAN_SENET', 'Alınan Senet', 'CEK_SENET', 320),
('VERILEN_SENET', 'Verilen Senet', 'CEK_SENET', 330),
('CEK_TAHSILAT_ODEME', 'Çek Tahsilat/Ödeme', 'CEK_SENET', 340),

-- PERSONEL Kategorisi
('BORDRO', 'Bordro', 'PERSONEL', 400),
('AVANS', 'Avans', 'PERSONEL', 410),
('HARCAMA', 'Harcama', 'PERSONEL', 420),

-- VERGİ/MUHASEBE Kategorisi
('VERGI_BEYANI', 'Vergi Beyanı', 'VERGI', 500),
('SGK_BORDRO', 'SGK Bordrosu', 'VERGI', 510),
('MUHTASAR', 'Muhtasar Beyanı', 'VERGI', 520),
('HAKEDIS', 'Hakediş Raporu', 'VERGI', 530),

-- DİĞER Kategorisi
('YEVMIYE', 'Yevmiye Fişi', 'DIGER', 900),
('ACILIS', 'Açılış Fişi', 'DIGER', 910),
('MAHSUP', 'Mahsup Fişi', 'DIGER', 920),
('DUZELTME', 'Düzeltme Fişi', 'DIGER', 930);

-- 4. Alt Evrak Verileri
-- ============================================================================
INSERT INTO document_subtypes (code, name, category, sort_order) VALUES
-- E-Belge Kategorisi
('E_FATURA', 'E-Fatura', 'E_BELGE', 10),
('E_ARSIV', 'E-Arşiv', 'E_BELGE', 20),
('E_IRSALIYE', 'E-İrsaliye', 'E_BELGE', 30),
('E_SMM', 'E-SMM', 'E_BELGE', 40),
('KAGIT_MATBU', 'Kağıt/Matbu', 'E_BELGE', 50),

-- Banka İşlem Tipleri
('EFT_HAVALE', 'EFT/Havale', 'BANKA', 100),
('KREDI_KARTI', 'Kredi Kartı', 'BANKA', 110),
('DEKONT', 'Dekont', 'BANKA', 120),
('VIRMAN', 'Virman', 'BANKA', 130),

-- Kasa İşlem Tipleri
('NAKIT', 'Nakit', 'KASA', 200),
('KASA_VIRMAN', 'Kasa Virman', 'KASA', 210),

-- Çek/Senet Tipleri
('MUSTERI_CEKI', 'Müşteri Çeki', 'CEK_SENET', 300),
('TEDARIKCI_CEKI', 'Tedarikçi Çeki', 'CEK_SENET', 310),
('ODEME', 'Ödeme', 'CEK_SENET', 320),
('TAHSILAT', 'Tahsilat', 'CEK_SENET', 330),

-- Personel İşlem Tipleri
('PERSONEL_ODEME', 'Personel Ödemesi', 'PERSONEL', 400),
('MAAS', 'Maaş', 'PERSONEL', 410),
('PRIM', 'Prim', 'PERSONEL', 420),
('MESAI', 'Mesai', 'PERSONEL', 430),
('AVANS', 'Avans', 'PERSONEL', 440),

-- Diğer
('SMM', 'Serbest Meslek Makbuzu', 'DIGER', 900),
('DUZELTME_MAHSUP', 'Düzeltme/Mahsup', 'DIGER', 910);

-- 5. Geçici Mapping Tablosu (Migration İçin)
-- ============================================================================
-- Mevcut değerleri yeni değerlere map etmek için
CREATE TABLE IF NOT EXISTS document_type_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    old_document_type VARCHAR(100),
    old_document_subtype VARCHAR(100),
    new_document_type_id INT,
    new_document_subtype_id INT,
    record_count INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_old_type (old_document_type),
    INDEX idx_old_subtype (old_document_subtype),
    FOREIGN KEY (new_document_type_id) REFERENCES document_types(id),
    FOREIGN KEY (new_document_subtype_id) REFERENCES document_subtypes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Mevcut Verilerden Mapping Tablosunu Doldur
-- ============================================================================
INSERT INTO document_type_mapping (old_document_type, old_document_subtype, record_count)
SELECT 
    document_type,
    document_subtype,
    COUNT(*) as record_count
FROM transactions
WHERE (document_type IS NOT NULL AND document_type != '')
   OR (document_subtype IS NOT NULL AND document_subtype != '')
GROUP BY document_type, document_subtype
ORDER BY record_count DESC;

-- 7. Otomatik Mapping (Tam Eşleşmeler)
-- ============================================================================
-- Type eşleştirmeleri
UPDATE document_type_mapping m
JOIN document_types dt ON UPPER(TRIM(m.old_document_type)) = UPPER(TRIM(dt.name))
SET m.new_document_type_id = dt.id
WHERE m.new_document_type_id IS NULL;

-- Subtype eşleştirmeleri
UPDATE document_type_mapping m
JOIN document_subtypes ds ON UPPER(TRIM(m.old_document_subtype)) = UPPER(TRIM(ds.name))
SET m.new_document_subtype_id = ds.id
WHERE m.new_document_subtype_id IS NULL;

-- 8. Özel Mapping Kuralları (Varsa Farklı İsimler)
-- ============================================================================
-- Bordro -> Bordro + Personel Ödemesi
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'BORDRO'),
    m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'PERSONEL_ODEME'),
    m.is_verified = TRUE
WHERE m.old_document_type = 'BORDRO' AND m.old_document_subtype = 'Personel Ödemesi';

-- Banka Tediye + EFT/Havale
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'BANKA_TEDIYE'),
    m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'EFT_HAVALE'),
    m.is_verified = TRUE
WHERE m.old_document_type = 'BANKA TEDİYE FİŞİ' AND m.old_document_subtype = 'EFT/Havale';

-- Kasa Tahsilat + Nakit
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'KASA_TAHSILAT'),
    m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'NAKIT'),
    m.is_verified = TRUE
WHERE m.old_document_type = 'KASA TAHSİLAT FİŞİ' AND m.old_document_subtype = 'Nakit';

-- Alış Fatura + E-Fatura
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'ALIS_FATURA'),
    m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'E_FATURA'),
    m.is_verified = TRUE
WHERE m.old_document_type = 'ALIŞ FATURASI' AND m.old_document_subtype = 'E-Fatura';

-- Satış Fatura + E-Fatura
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'SATIS_FATURA'),
    m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'E_FATURA'),
    m.is_verified = TRUE
WHERE m.old_document_type = 'SATIŞ FATURASI' AND m.old_document_subtype = 'E-Fatura';

-- Yevmiye + Düzeltme/Mahsup
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'YEVMIYE'),
    m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'DUZELTME_MAHSUP'),
    m.is_verified = TRUE
WHERE m.old_document_type = 'YEVMİYE FİŞİ' AND m.old_document_subtype = 'Düzeltme/Mahsup';

-- ============================================================================
-- KONTROL SORGUSU
-- ============================================================================
-- Mapping durumunu görmek için:
/*
SELECT 
    old_document_type,
    old_document_subtype,
    dt.name as new_type,
    ds.name as new_subtype,
    record_count,
    is_verified
FROM document_type_mapping m
LEFT JOIN document_types dt ON m.new_document_type_id = dt.id
LEFT JOIN document_subtypes ds ON m.new_document_subtype_id = ds.id
ORDER BY record_count DESC;
*/

-- Eksik mappingleri görmek için:
/*
SELECT * FROM document_type_mapping
WHERE (new_document_type_id IS NULL OR new_document_subtype_id IS NULL)
  AND record_count > 0
ORDER BY record_count DESC;
*/
