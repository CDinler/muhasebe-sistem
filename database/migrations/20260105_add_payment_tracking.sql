-- ============================================================
-- Fatura Ödeme Takip Sistemi
-- Date: 2026-01-05
-- Purpose: invoice_transaction_mappings tablosuna ödeme bilgileri ekleme
-- ============================================================

-- 1. payment_amount kolonu ekle
ALTER TABLE invoice_transaction_mappings
ADD COLUMN payment_amount DECIMAL(18,2) DEFAULT NULL 
COMMENT 'Bu fiş ile yapılan ödeme tutarı (NULL = ödeme değil, sadece muhasebe ilişkisi)';

-- 2. payment_date kolonu ekle  
ALTER TABLE invoice_transaction_mappings
ADD COLUMN payment_date DATE DEFAULT NULL
COMMENT 'Ödeme tarihi (transaction.transaction_date cache)';

-- 3. payment_status kolonu ekle (opsiyonel - computed field olarak da yapılabilir)
ALTER TABLE invoice_transaction_mappings
ADD COLUMN payment_status ENUM('pending', 'completed', 'cancelled') DEFAULT 'completed'
COMMENT 'Ödeme durumu (opsiyonel)';

-- 4. Index'ler ekle - performans için
CREATE INDEX idx_payment_amount ON invoice_transaction_mappings(payment_amount);
CREATE INDEX idx_payment_date ON invoice_transaction_mappings(payment_date);
CREATE INDEX idx_payment_status ON invoice_transaction_mappings(payment_status);

-- 5. Composite index - ödenmeyen faturaları hızlı bulmak için
CREATE INDEX idx_einvoice_payment ON invoice_transaction_mappings(einvoice_id, payment_amount);

-- 6. Mevcut verileri güncelle - transaction date'i cache'le
UPDATE invoice_transaction_mappings m
JOIN transactions t ON m.transaction_id = t.id
SET m.payment_date = t.transaction_date
WHERE m.payment_amount IS NOT NULL;

-- 7. Tablo açıklamasını güncelle
ALTER TABLE invoice_transaction_mappings 
COMMENT = 'Fatura-Fiş ilişkileri ve ödeme takibi - payment_amount NULL ise sadece ilişki, dolu ise ödeme kaydı';

-- ============================================================
-- KULLANIM ÖRNEKLERİ
-- ============================================================

-- Örnek 1: Tam Ödeme Kaydı
-- INSERT INTO invoice_transaction_mappings 
--     (einvoice_id, transaction_id, document_number, payment_amount, payment_date, mapping_type, confidence_score, notes)
-- VALUES 
--     (123, 456, 'ABC2025000001', 10000.00, '2026-01-05', 'manual', 1.00, 'Tam ödeme - banka havalesi');

-- Örnek 2: Kısmi Ödeme (1. taksit)
-- INSERT INTO invoice_transaction_mappings 
--     (einvoice_id, transaction_id, document_number, payment_amount, payment_date, mapping_type, notes)
-- VALUES 
--     (123, 457, 'ABC2025000001', 5000.00, '2026-01-05', 'manual', '1. taksit - 5000 TL');

-- Örnek 3: Muhasebe İlişkisi (Ödeme Değil)
-- INSERT INTO invoice_transaction_mappings 
--     (einvoice_id, transaction_id, document_number, payment_amount, mapping_type, notes)
-- VALUES 
--     (123, 458, 'ABC2025000001', NULL, 'auto', 'Alış faturası muhasebe kaydı');

-- ============================================================
-- SORGULAR - Ödeme Durumu Kontrolü
-- ============================================================

-- Faturanın toplam ödenen tutarı
-- SELECT 
--     e.id,
--     e.invoice_number,
--     e.payable_amount AS total,
--     COALESCE(SUM(m.payment_amount), 0) AS paid,
--     e.payable_amount - COALESCE(SUM(m.payment_amount), 0) AS remaining
-- FROM einvoices e
-- LEFT JOIN invoice_transaction_mappings m ON e.id = m.einvoice_id AND m.payment_amount IS NOT NULL
-- WHERE e.id = 123
-- GROUP BY e.id;

-- Ödenmeyen faturalar
-- SELECT 
--     e.id,
--     e.invoice_number,
--     e.supplier_name,
--     e.issue_date,
--     e.payable_amount AS total,
--     COALESCE(SUM(m.payment_amount), 0) AS paid,
--     e.payable_amount - COALESCE(SUM(m.payment_amount), 0) AS remaining,
--     DATEDIFF(CURRENT_DATE, e.issue_date) AS days_overdue
-- FROM einvoices e
-- LEFT JOIN invoice_transaction_mappings m ON e.id = m.einvoice_id AND m.payment_amount IS NOT NULL
-- WHERE e.invoice_category = 'incoming'
-- GROUP BY e.id
-- HAVING remaining > 0
-- ORDER BY days_overdue DESC;

-- ============================================================
-- ROLLBACK
-- ============================================================

-- Index'leri kaldır
-- DROP INDEX idx_payment_amount ON invoice_transaction_mappings;
-- DROP INDEX idx_payment_date ON invoice_transaction_mappings;
-- DROP INDEX idx_payment_status ON invoice_transaction_mappings;
-- DROP INDEX idx_einvoice_payment ON invoice_transaction_mappings;

-- Kolonları kaldır
-- ALTER TABLE invoice_transaction_mappings DROP COLUMN payment_amount;
-- ALTER TABLE invoice_transaction_mappings DROP COLUMN payment_date;
-- ALTER TABLE invoice_transaction_mappings DROP COLUMN payment_status;
