-- =============================================================================================================
-- DOCUMENT SUBTYPES KALDIRMA
-- Tarih: 2026-01-06
-- Açıklama: document_subtypes tablosu ve ilişkili kolonlar tamamen kaldırılıyor
-- =============================================================================================================

-- ⚠️ BACKUP AL
CREATE TABLE IF NOT EXISTS document_subtypes_backup_20260106 AS SELECT * FROM document_subtypes;
CREATE TABLE IF NOT EXISTS transactions_backup_20260106 AS SELECT * FROM transactions;

SELECT 'BACKUP ALINDI' AS mesaj;

-- =============================================================================================================
-- 1. FOREIGN KEY'LERİ KALDIR
-- =============================================================================================================

ALTER TABLE transactions DROP FOREIGN KEY IF EXISTS fk_trans_subtype;
ALTER TABLE document_subtypes DROP FOREIGN KEY IF EXISTS fk_subtype_type;

SELECT 'FOREIGN KEY''LER KALDIRILDI' AS mesaj;

-- =============================================================================================================
-- 2. TRANSACTIONS TABLOSUNDAN document_subtype_id KOLONUNU KALDIR
-- =============================================================================================================

ALTER TABLE transactions DROP COLUMN IF EXISTS document_subtype_id;

SELECT 'transactions.document_subtype_id KALDIRILDI' AS mesaj;

-- =============================================================================================================
-- 3. DOCUMENT_SUBTYPES TABLOSUNU KALDIR
-- =============================================================================================================

DROP TABLE IF EXISTS document_subtypes;

SELECT 'document_subtypes TABLOSU KALDIRILDI' AS mesaj;

-- =============================================================================================================
-- 4. DOCUMENT_TYPES TABLOSUNDAN requires_subtype KOLONUNU KALDIR
-- =============================================================================================================

ALTER TABLE document_types DROP COLUMN IF EXISTS requires_subtype;

SELECT 'document_types.requires_subtype KALDIRILDI' AS mesaj;

-- =============================================================================================================
-- KONTROL
-- =============================================================================================================

SELECT '========================================' AS '';
SELECT 'DOCUMENT_SUBTYPES KALDIRILDI - KONTROL' AS mesaj;
SELECT '========================================' AS '';

-- Tablonun silindiğini doğrula
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 'BAŞARILI: document_subtypes tablosu yok'
        ELSE 'HATA: Tablo hala mevcut'
    END AS sonuc
FROM information_schema.tables 
WHERE table_schema = DATABASE() 
  AND table_name = 'document_subtypes';

-- Transactions kolonunun silindiğini doğrula
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 'BAŞARILI: document_subtype_id kolonu yok'
        ELSE 'HATA: Kolon hala mevcut'
    END AS sonuc
FROM information_schema.columns 
WHERE table_schema = DATABASE() 
  AND table_name = 'transactions'
  AND column_name = 'document_subtype_id';

SELECT '========================================' AS '';
SELECT 'İŞLEM TAMAMLANDI' AS sonuc;
SELECT '========================================' AS '';

-- =============================================================================================================
-- ROLLBACK (SORUN OLURSA)
-- =============================================================================================================

/*
-- Geri almak için:
CREATE TABLE document_subtypes AS SELECT * FROM document_subtypes_backup_20260106;
ALTER TABLE transactions ADD COLUMN document_subtype_id INT NULL;
UPDATE transactions t1 
INNER JOIN transactions_backup_20260106 t2 ON t1.id = t2.id 
SET t1.document_subtype_id = t2.document_subtype_id;
*/
