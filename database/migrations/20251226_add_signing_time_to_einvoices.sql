-- 20251226_add_signing_time_to_einvoices.sql
-- E-faturaların signing_time alanını ekler (XML'deki SigningTime - imzalanma zamanı)

ALTER TABLE einvoices 
ADD COLUMN signing_time TIMESTAMP NULL COMMENT 'SigningTime - Fatura imzalanma zamani (XML SigningTime)' AFTER tax_point_date;

-- Index ekleyelim (tarih sorgularında kullanılabilir)
CREATE INDEX idx_einvoices_signing_time ON einvoices(signing_time);
