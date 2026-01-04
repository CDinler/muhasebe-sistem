-- ===================================================================
-- Document Types Code Update - Transactions'ı Koruyarak
-- ===================================================================

-- ALIS_FATURA → ALIS_FATURASI (3989 transaction)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'ALIS_FATURA'
JOIN document_types dt_new ON dt_new.code = 'ALIS_FATURASI'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- SATIS_FATURA → SATIS_FATURASI (309 transaction)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'SATIS_FATURA'
JOIN document_types dt_new ON dt_new.code = 'SATIS_FATURASI'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- IADE_FATURA → IADE_FATURASI (0 transaction ama gene de güncelle)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'IADE_FATURA'
JOIN document_types dt_new ON dt_new.code = 'IADE_FATURASI'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- YEVMIYE → YEVMIYE_FISI (306 transaction)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'YEVMIYE'
JOIN document_types dt_new ON dt_new.code = 'YEVMIYE_FISI'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- MAHSUP → MAHSUP_FISI (0 transaction)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'MAHSUP'
JOIN document_types dt_new ON dt_new.code = 'MAHSUP_FISI'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- ACILIS → ACILIS_FISI (0 transaction)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'ACILIS'
JOIN document_types dt_new ON dt_new.code = 'ACILIS_FISI'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- DUZELTME → DUZELTICI_FIS (0 transaction)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'DUZELTME'
JOIN document_types dt_new ON dt_new.code = 'DUZELTICI_FIS'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- BANKA_VIRMAN → VIRMAN (0 transaction)
UPDATE transactions t
JOIN document_types dt_old ON dt_old.code = 'BANKA_VIRMAN'
JOIN document_types dt_new ON dt_new.code = 'VIRMAN'
SET t.document_type_id = dt_new.id
WHERE t.document_type_id = dt_old.id;

-- Doğrulama
SELECT 
    dt.code,
    dt.name,
    COUNT(t.id) AS transaction_sayisi
FROM document_types dt
LEFT JOIN transactions t ON t.document_type_id = dt.id
GROUP BY dt.id, dt.code, dt.name
HAVING transaction_sayisi > 0
ORDER BY transaction_sayisi DESC;
