-- ============================================================================
-- DOCUMENT TYPE MAPPING - MANUEL DÜZELTMELER
-- Mevcut değerleri lookup tablolara bağlar
-- ============================================================================

-- Tüm mappingleri temizle önce
UPDATE document_type_mapping 
SET new_document_type_id = NULL, 
    new_document_subtype_id = NULL,
    is_verified = FALSE;

-- ============================================================================
-- 1. ANA TİP MAPPINGLER (17 farklı kombinasyon)
-- ============================================================================

-- BANKA TEDİYE FİŞİ -> BANKA_TEDIYE
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'BANKA_TEDIYE')
WHERE m.old_document_type = 'BANKA TEDİYE FİŞİ';

-- BORDRO -> BORDRO
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'BORDRO')
WHERE m.old_document_type = 'BORDRO';

-- KASA TAHSİLAT FİŞİ -> KASA_TAHSILAT
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'KASA_TAHSILAT')
WHERE m.old_document_type = 'KASA TAHSİLAT FİŞİ';

-- ALIŞ FATURASI -> ALIS_FATURA
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'ALIS_FATURA')
WHERE m.old_document_type = 'ALIŞ FATURASI';

-- BANKA TAHSİLAT FİŞİ -> BANKA_TAHSILAT
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'BANKA_TAHSILAT')
WHERE m.old_document_type = 'BANKA TAHSİLAT FİŞİ';

-- SATIŞ FATURASI -> SATIS_FATURA
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'SATIS_FATURA')
WHERE m.old_document_type = 'SATIŞ FATURASI';

-- YEVMİYE FİŞİ -> YEVMIYE
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'YEVMIYE')
WHERE m.old_document_type = 'YEVMİYE FİŞİ';

-- HAKEDİŞ RAPORU -> HAKEDIS
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'HAKEDIS')
WHERE m.old_document_type = 'HAKEDİŞ RAPORU';

-- VERİLEN ÇEK -> VERILEN_CEK
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'VERILEN_CEK')
WHERE m.old_document_type = 'VERİLEN ÇEK';

-- ÇEK TAHSİLAT/ÖDEME -> CEK_TAHSILAT_ODEME
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'CEK_TAHSILAT_ODEME')
WHERE m.old_document_type = 'ÇEK TAHSİLAT/ÖDEME';

-- ALINAN ÇEK -> ALINAN_CEK
UPDATE document_type_mapping m
SET m.new_document_type_id = (SELECT id FROM document_types WHERE code = 'ALINAN_CEK')
WHERE m.old_document_type = 'ALINAN ÇEK';

-- ============================================================================
-- 2. ALT TİP MAPPINGLER
-- ============================================================================

-- EFT/Havale -> EFT_HAVALE
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'EFT_HAVALE')
WHERE m.old_document_subtype = 'EFT/Havale';

-- Personel Ödemesi -> PERSONEL_ODEME
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'PERSONEL_ODEME')
WHERE m.old_document_subtype = 'Personel Ödemesi';

-- Nakit -> NAKIT
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'NAKIT')
WHERE m.old_document_subtype = 'Nakit';

-- E-Fatura -> E_FATURA
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'E_FATURA')
WHERE m.old_document_subtype = 'E-Fatura';

-- Kredi Kartı -> KREDI_KARTI
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'KREDI_KARTI')
WHERE m.old_document_subtype = 'Kredi Kartı';

-- E-Arşiv -> E_ARSIV
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'E_ARSIV')
WHERE m.old_document_subtype = 'E-Arşiv';

-- Düzeltme/Mahsup -> DUZELTME_MAHSUP
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'DUZELTME_MAHSUP')
WHERE m.old_document_subtype = 'Düzeltme/Mahsup';

-- Tedarikçi Çeki -> TEDARIKCI_CEKI
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'TEDARIKCI_CEKI')
WHERE m.old_document_subtype = 'Tedarikçi Çeki';

-- Kağıt/Matbu -> KAGIT_MATBU
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'KAGIT_MATBU')
WHERE m.old_document_subtype = 'Kağıt/Matbu';

-- Müşteri Çeki -> MUSTERI_CEKI
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'MUSTERI_CEKI')
WHERE m.old_document_subtype = 'Müşteri Çeki';

-- Ödeme -> ODEME
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'ODEME')
WHERE m.old_document_subtype = 'Ödeme';

-- Serbest Meslek Makbuzu -> SMM
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'SMM')
WHERE m.old_document_subtype = 'Serbest Meslek Makbuzu';

-- Dekont -> DEKONT
UPDATE document_type_mapping m
SET m.new_document_subtype_id = (SELECT id FROM document_subtypes WHERE code = 'DEKONT')
WHERE m.old_document_subtype = 'Dekont';

-- ============================================================================
-- 3. TÜM MAPPINGLER İÇİN VERIFIED FLAG SET ET
-- ============================================================================
UPDATE document_type_mapping
SET is_verified = TRUE
WHERE new_document_type_id IS NOT NULL 
  AND new_document_subtype_id IS NOT NULL;

-- ============================================================================
-- KONTROL SORGUSU
-- ============================================================================
SELECT 
    'MAPPING SONUÇLARI' as rapor,
    COUNT(*) as toplam_mapping,
    SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN 1 ELSE 0 END) as tamamlanan,
    SUM(CASE WHEN new_document_type_id IS NULL OR new_document_subtype_id IS NULL THEN 1 ELSE 0 END) as eksik,
    SUM(record_count) as toplam_kayit,
    SUM(CASE WHEN new_document_type_id IS NOT NULL AND new_document_subtype_id IS NOT NULL THEN record_count ELSE 0 END) as eslenen_kayit
FROM document_type_mapping;
