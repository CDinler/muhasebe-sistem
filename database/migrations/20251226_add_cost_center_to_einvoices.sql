-- 20251226_add_cost_center_to_einvoices.sql
-- einvoices tablosuna cost_center_id sütunu ekler

ALTER TABLE einvoices
ADD COLUMN cost_center_id INT NULL COMMENT 'Maliyet merkezi ID',
ADD INDEX idx_einvoices_cost_center (cost_center_id),
ADD CONSTRAINT fk_einvoices_cost_center FOREIGN KEY (cost_center_id) REFERENCES cost_centers(id) ON DELETE SET NULL;
