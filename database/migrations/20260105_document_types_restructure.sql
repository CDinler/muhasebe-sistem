-- =============================================================================================================
-- DOCUMENT TYPES YAPILANDIRMA - HIZLI UYGULAMA
-- Tarih: 2026-01-05
-- Açıklama: parent_code → document_type_id, requires_subtype ekleme, foreign key
-- =============================================================================================================

-- ⚠️ ÖNEMLİ: Bu script'i çalıştırmadan önce backup alın!

-- =============================================================================================================
-- 1. BACKUP AL
-- =============================================================================================================
CREATE TABLE IF NOT EXISTS document_types_backup_20260105 AS SELECT * FROM document_types;
CREATE TABLE IF NOT EXISTS document_subtypes_backup_20260105 AS SELECT * FROM document_subtypes;
CREATE TABLE IF NOT EXISTS transactions_backup_20260105 AS SELECT * FROM transactions;

SELECT 'BACKUP TAMAMLANDI - Toplam kayıtlar:' AS mesaj,
    (SELECT COUNT(*) FROM document_types) AS document_types_count,
    (SELECT COUNT(*) FROM document_subtypes) AS document_subtypes_count,
    (SELECT COUNT(*) FROM transactions) AS transactions_count;

-- =============================================================================================================
-- 2. MEVCUT DURUM ANALİZİ
-- =============================================================================================================

-- Transactions'da kullanılan document_type_id ve subtype_id değerlerini kontrol et
SELECT 'MEVCUT TRANSACTIONS ANALİZİ' AS mesaj;

SELECT 
    document_type_id,
    document_subtype_id,
    COUNT(*) AS kullanim_sayisi
FROM transactions
WHERE document_type_id IS NOT NULL OR document_subtype_id IS NOT NULL
GROUP BY document_type_id, document_subtype_id
ORDER BY kullanim_sayisi DESC;

-- =============================================================================================================
-- 3. DOCUMENT_TYPES TABLOSUNA YENİ KOLON EKLE
-- =============================================================================================================

-- requires_subtype kolonu ekle (hangi evrak türleri alt tür gerektiriyor?)
ALTER TABLE document_types 
ADD COLUMN IF NOT EXISTS requires_subtype BOOLEAN DEFAULT FALSE COMMENT 'Alt evrak türü seçimi zorunlu mu?';

-- Fatura türleri için alt tür zorunlu yap
UPDATE document_types 
SET requires_subtype = TRUE 
WHERE code IN ('ALIS_FATURASI', 'SATIS_FATURASI', 'IADE_FATURASI', 'HAKEDIS_FATURASI');

SELECT 'REQUIRES_SUBTYPE GÜNCELLENDI' AS mesaj,
    name,
    requires_subtype
FROM document_types
WHERE requires_subtype = TRUE;

-- =============================================================================================================
-- 4. DOCUMENT_SUBTYPES TABLOSUNA YENİ KOLON EKLE
-- =============================================================================================================

-- Önce document_type_id kolonu ekle (NULL olabilir, sonra dolduracağız)
ALTER TABLE document_subtypes 
ADD COLUMN IF NOT EXISTS document_type_id INT NULL COMMENT 'Ana evrak türü ID' AFTER id;

-- parent_code'dan document_type_id'yi doldur
UPDATE document_subtypes ds
INNER JOIN document_types dt ON ds.parent_code = dt.code
SET ds.document_type_id = dt.id;

-- Kontrol: Hangi kayıtlar NULL kaldı?
SELECT 
    'NULL KALAN KAYITLAR (Eşleşmeyen parent_code)' AS uyari,
    id,
    parent_code,
    code,
    name
FROM document_subtypes
WHERE document_type_id IS NULL;

-- Eğer NULL kayıt yoksa devam et
SELECT 'DOCUMENT_TYPE_ID DOLDURULDU' AS mesaj,
    COUNT(*) AS toplam_kayit,
    COUNT(document_type_id) AS doldurulmus_kayit
FROM document_subtypes;

-- =============================================================================================================
-- 5. FOREIGN KEY CONSTRAINT EKLE
-- =============================================================================================================

-- Önce mevcut foreign key varsa kaldır
ALTER TABLE document_subtypes DROP FOREIGN KEY IF EXISTS fk_subtype_type;

-- Yeni foreign key ekle
ALTER TABLE document_subtypes
ADD CONSTRAINT fk_subtype_type 
    FOREIGN KEY (document_type_id) 
    REFERENCES document_types(id) 
    ON DELETE CASCADE;

-- Unique constraint ekle (aynı type altında aynı code tekrar etmesin)
ALTER TABLE document_subtypes DROP INDEX IF EXISTS unique_type_code;
ALTER TABLE document_subtypes
ADD UNIQUE KEY unique_type_code (document_type_id, code);

SELECT 'FOREIGN KEY VE UNIQUE CONSTRAINT EKLENDİ' AS mesaj;

-- =============================================================================================================
-- 6. TRANSACTIONS TABLOSUNA FOREIGN KEY EKLE
-- =============================================================================================================

-- Önce mevcut foreign key'leri kaldır
ALTER TABLE transactions DROP FOREIGN KEY IF EXISTS fk_trans_doctype;
ALTER TABLE transactions DROP FOREIGN KEY IF EXISTS fk_trans_subtype;

-- Foreign key'leri ekle
ALTER TABLE transactions
ADD CONSTRAINT fk_trans_doctype 
    FOREIGN KEY (document_type_id) 
    REFERENCES document_types(id);

ALTER TABLE transactions
ADD CONSTRAINT fk_trans_subtype 
    FOREIGN KEY (document_subtype_id) 
    REFERENCES document_subtypes(id);

SELECT 'TRANSACTIONS FOREIGN KEY EKLENDİ' AS mesaj;

-- =============================================================================================================
-- 7. DUPLICATE KAYITLARI TEMİZLE
-- =============================================================================================================

-- Duplicate kontrol (aynı document_type_id ve code kombinasyonu)
SELECT 
    'DUPLICATE KONTROL' AS mesaj,
    document_type_id,
    code,
    COUNT(*) AS tekrar_sayisi,
    GROUP_CONCAT(id ORDER BY id) AS id_listesi
FROM document_subtypes
GROUP BY document_type_id, code
HAVING COUNT(*) > 1;

-- Eğer duplicate varsa manuel olarak silin (hangi ID'nin tutulacağına karar verin)
-- Örnek:
-- DELETE FROM document_subtypes WHERE id IN (25, 28);  -- Sadece örnek!

-- =============================================================================================================
-- 8. SON KONTROL VE RAPOR
-- =============================================================================================================

SELECT '========================================' AS '';
SELECT 'MİGRATİON TAMAMLANDI - ÖZET RAPOR' AS mesaj;
SELECT '========================================' AS '';

-- Document Types
SELECT 
    'DOCUMENT TYPES' AS tablo,
    COUNT(*) AS toplam_kayit,
    SUM(requires_subtype = TRUE) AS alt_tur_gerektiren,
    SUM(requires_subtype = FALSE) AS alt_tur_gerekmez
FROM document_types;

-- Document Subtypes
SELECT 
    'DOCUMENT SUBTYPES' AS tablo,
    COUNT(*) AS toplam_kayit,
    COUNT(document_type_id) AS type_id_dolu,
    COUNT(*) - COUNT(document_type_id) AS type_id_null
FROM document_subtypes;

-- Transactions
SELECT 
    'TRANSACTIONS' AS tablo,
    COUNT(*) AS toplam_kayit,
    COUNT(document_type_id) AS type_id_dolu,
    COUNT(document_subtype_id) AS subtype_id_dolu
FROM transactions;

-- Alt türleri olan evrak türleri
SELECT 
    'ALT TÜR DAĞILIMI' AS rapor,
    dt.name AS evrak_turu,
    COUNT(ds.id) AS alt_tur_sayisi
FROM document_types dt
LEFT JOIN document_subtypes ds ON dt.id = ds.document_type_id
GROUP BY dt.id, dt.name
ORDER BY alt_tur_sayisi DESC;

SELECT '========================================' AS '';
SELECT 'MİGRATİON BAŞARILI!' AS sonuc;
SELECT '========================================' AS '';

-- =============================================================================================================
-- 9. ROLLBACK (SORUN OLURSA)
-- =============================================================================================================

/*
-- Eğer sorun olursa backup'tan geri yükle:

DROP TABLE document_types;
DROP TABLE document_subtypes;
UPDATE transactions SET document_type_id = NULL, document_subtype_id = NULL;

CREATE TABLE document_types AS SELECT * FROM document_types_backup_20260105;
CREATE TABLE document_subtypes AS SELECT * FROM document_subtypes_backup_20260105;

SELECT 'ROLLBACK TAMAMLANDI' AS mesaj;
*/
