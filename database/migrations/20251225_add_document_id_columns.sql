-- ============================================================================
-- TRANSACTIONS TABLOSUNA YENİ KOLONLAR EKLE
-- document_type_id ve document_subtype_id foreign key kolonları
-- ============================================================================

-- 1. Yeni kolonları ekle
ALTER TABLE transactions
ADD COLUMN document_type_id INT NULL AFTER document_subtype,
ADD COLUMN document_subtype_id INT NULL AFTER document_type_id;

-- 2. Foreign key constraints ekle
ALTER TABLE transactions
ADD CONSTRAINT fk_transactions_document_type
    FOREIGN KEY (document_type_id) REFERENCES document_types(id),
ADD CONSTRAINT fk_transactions_document_subtype
    FOREIGN KEY (document_subtype_id) REFERENCES document_subtypes(id);

-- 3. Index ekle (performans için)
CREATE INDEX idx_transactions_document_type ON transactions(document_type_id);
CREATE INDEX idx_transactions_document_subtype ON transactions(document_subtype_id);

-- ============================================================================
-- VERİ MİGRASYONU: Eski VARCHAR değerlerden yeni ID'lere
-- ============================================================================

UPDATE transactions t
INNER JOIN document_type_mapping m 
    ON (t.document_type = m.old_document_type OR (t.document_type IS NULL AND m.old_document_type IS NULL))
    AND (t.document_subtype = m.old_document_subtype OR (t.document_subtype IS NULL AND m.old_document_subtype IS NULL))
SET 
    t.document_type_id = m.new_document_type_id,
    t.document_subtype_id = m.new_document_subtype_id
WHERE m.new_document_type_id IS NOT NULL 
  AND m.new_document_subtype_id IS NOT NULL;

-- ============================================================================
-- KONTROL SORGUSU
-- ============================================================================

-- Migration istatistikleri
SELECT 
    'VERİ MİGRASYONU SONUÇLARI' as rapor,
    COUNT(*) as toplam_transaction,
    SUM(CASE WHEN document_type_id IS NOT NULL THEN 1 ELSE 0 END) as type_id_dolu,
    SUM(CASE WHEN document_subtype_id IS NOT NULL THEN 1 ELSE 0 END) as subtype_id_dolu,
    SUM(CASE WHEN document_type_id IS NOT NULL AND document_subtype_id IS NOT NULL THEN 1 ELSE 0 END) as her_ikisi_dolu,
    ROUND(SUM(CASE WHEN document_type_id IS NOT NULL AND document_subtype_id IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as basari_yuzdesi
FROM transactions;

-- Karşılaştırma: Eski vs Yeni
SELECT 
    t.document_type as eski_type,
    dt.name as yeni_type,
    t.document_subtype as eski_subtype,
    ds.name as yeni_subtype,
    COUNT(*) as kayit_sayisi
FROM transactions t
LEFT JOIN document_types dt ON t.document_type_id = dt.id
LEFT JOIN document_subtypes ds ON t.document_subtype_id = ds.id
GROUP BY t.document_type, dt.name, t.document_subtype, ds.name
ORDER BY kayit_sayisi DESC
LIMIT 20;
