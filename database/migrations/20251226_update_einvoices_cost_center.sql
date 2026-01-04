-- 20251226_update_einvoices_cost_center.sql
-- Mevcut e-faturaların cost_center_id alanını transaction_id üzerinden günceller

UPDATE einvoices e
JOIN transactions t ON e.transaction_id = t.id
SET e.cost_center_id = t.cost_center_id
WHERE e.transaction_id IS NOT NULL;
