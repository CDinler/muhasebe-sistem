-- 20251227_make_xml_fields_nullable.sql
-- PDF-only e-faturalar için xml_file_path ve xml_hash kolonlarını nullable yap

-- xml_file_path nullable yap (unique constraint kaldır)
ALTER TABLE einvoices 
MODIFY COLUMN xml_file_path VARCHAR(500) NULL,
DROP INDEX xml_file_path;

-- xml_hash nullable yap (unique constraint kaldır)
ALTER TABLE einvoices 
MODIFY COLUMN xml_hash VARCHAR(64) NULL,
DROP INDEX xml_hash;

-- has_xml=0 olanlar için unique index (ETTN bazlı kontrol)
CREATE UNIQUE INDEX idx_einvoices_uuid_unique 
ON einvoices(invoice_uuid);
