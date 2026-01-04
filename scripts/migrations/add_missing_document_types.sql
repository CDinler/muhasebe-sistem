-- ===================================================================
-- Eksik Document Types Ekleme - YEVMIYE_KAYDI_SABLONU.md'ye göre
-- ===================================================================

-- Eksik kayıtlar (YEVMIYE'de var, tabloda yok)

-- FATURA kategorisi
INSERT IGNORE INTO document_types (code, name, category, sort_order, is_active) VALUES
('ALIS_FATURASI', 'Alış Faturası', 'FATURA', 1, 1),
('SATIS_FATURASI', 'Satış Faturası', 'FATURA', 2, 1),
('IADE_FATURASI', 'İade Faturası', 'FATURA', 3, 1);

-- BANKA kategorisi
INSERT IGNORE INTO document_types (code, name, category, sort_order, is_active) VALUES
('VIRMAN', 'Banka Virman', 'BANKA', 4, 1);

-- MUHASEBE kategorisi
INSERT IGNORE INTO document_types (code, name, category, sort_order, is_active) VALUES
('MAHSUP_FISI', 'Mahsup Fişi', 'MUHASEBE', 1, 1),
('YEVMIYE_FISI', 'Yevmiye Fişi', 'MUHASEBE', 2, 1),
('ACILIS_FISI', 'Açılış Fişi', 'MUHASEBE', 3, 1),
('DUZELTICI_FIS', 'Düzeltici Fiş', 'MUHASEBE', 5, 1);

-- Doğrulama
SELECT '✅ Eksik document_types eklendi!' AS Durum;

SELECT code, name, category
FROM document_types
WHERE code IN (
    'ALIS_FATURASI', 'SATIS_FATURASI', 'IADE_FATURASI',
    'VIRMAN',
    'MAHSUP_FISI', 'YEVMIYE_FISI', 'ACILIS_FISI', 'DUZELTICI_FIS'
)
ORDER BY category, code;
