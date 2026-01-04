-- E-Fatura PDF desteği migration
-- PDF yolu ve kaynak bilgisi ekle

-- pdf_path sütunu ekle
ALTER TABLE einvoices 
ADD COLUMN pdf_path VARCHAR(500) COMMENT 'PDF dosyasının relative path''i (data/einvoice_pdfs/... dan itibaren)';

-- has_xml flag ekle (PDF-only mi yoksa XML+PDF mi?)
ALTER TABLE einvoices 
ADD COLUMN has_xml BOOLEAN DEFAULT TRUE COMMENT 'XML dosyası var mı? False ise sadece PDF''den parse edilmiş';

-- source sütunu ekle (nereden geldiği)
ALTER TABLE einvoices 
ADD COLUMN source VARCHAR(50) DEFAULT 'xml' COMMENT 'Kaynak: xml, pdf_only, manual, api';

-- PDF path için index
CREATE INDEX idx_einvoices_pdf_path ON einvoices(pdf_path);

-- Sadece PDF olan faturaları sorgulamak için
CREATE INDEX idx_einvoices_has_xml ON einvoices(has_xml);
