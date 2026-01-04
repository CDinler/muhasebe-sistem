-- 20251226_add_supplier_iban_to_einvoices.sql
-- E-faturaların supplier_iban alanını ekler (XML'den parse edilen IBAN bilgisi)

ALTER TABLE einvoices 
ADD COLUMN supplier_iban VARCHAR(34) DEFAULT NULL COMMENT 'Satici IBAN numarasi (PayeeFinancialAccount/ID)';

-- Index ekleyelim (hızlı arama için)
CREATE INDEX idx_einvoices_supplier_iban ON einvoices(supplier_iban);
