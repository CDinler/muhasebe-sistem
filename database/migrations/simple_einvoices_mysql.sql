-- E-FATURA TABLOSU BASIT MİGRATION (MySQL/MariaDB)
-- Her komutu ayrı ayrı çalıştırın

-- Adım 1: Yedek al
CREATE TABLE IF NOT EXISTS einvoices_backup_20251216 AS SELECT * FROM einvoices;

-- Adım 2: Eski tabloyu sil
DROP TABLE IF EXISTS einvoices;

-- Adım 3: Yeni tabloyu oluştur
CREATE TABLE einvoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    xml_file_path VARCHAR(500) UNIQUE NOT NULL,
    xml_hash VARCHAR(64) UNIQUE NOT NULL,
    invoice_category VARCHAR(50) DEFAULT 'incoming',
    invoice_uuid VARCHAR(36) UNIQUE NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    invoice_profile VARCHAR(100),
    invoice_type VARCHAR(50),
    issue_date DATE NOT NULL,
    issue_time TIME,
    tax_point_date DATE,
    supplier_tax_number VARCHAR(11),
    supplier_id_scheme VARCHAR(10),
    supplier_name VARCHAR(255),
    supplier_address TEXT,
    supplier_city VARCHAR(100),
    supplier_district VARCHAR(100),
    supplier_postal_code VARCHAR(10),
    supplier_tax_office VARCHAR(100),
    supplier_email VARCHAR(255),
    supplier_phone VARCHAR(20),
    customer_tax_number VARCHAR(11),
    customer_name VARCHAR(255),
    line_extension_amount DECIMAL(18, 2),
    tax_exclusive_amount DECIMAL(18, 2),
    tax_inclusive_amount DECIMAL(18, 2),
    payable_amount DECIMAL(18, 2),
    allowance_total DECIMAL(18, 2),
    charge_total DECIMAL(18, 2),
    total_tax_amount DECIMAL(18, 2),
    withholding_tax_amount DECIMAL(18, 2),
    withholding_percent DECIMAL(5, 2),
    withholding_code VARCHAR(10),
    contact_id INT NULL,
    transaction_id INT NULL,
    processing_status VARCHAR(50) DEFAULT 'IMPORTED',
    error_message TEXT,
    raw_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    imported_by INT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
    FOREIGN KEY (imported_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adım 4: İndeksler
CREATE INDEX idx_einvoices_invoice_number ON einvoices(invoice_number);
CREATE INDEX idx_einvoices_invoice_uuid ON einvoices(invoice_uuid);
CREATE INDEX idx_einvoices_supplier_tax_number ON einvoices(supplier_tax_number);
CREATE INDEX idx_einvoices_issue_date ON einvoices(issue_date);
CREATE INDEX idx_einvoices_contact_id ON einvoices(contact_id);
CREATE INDEX idx_einvoices_transaction_id ON einvoices(transaction_id);
CREATE INDEX idx_einvoices_processing_status ON einvoices(processing_status);
CREATE INDEX idx_einvoices_xml_hash ON einvoices(xml_hash);
CREATE INDEX idx_einvoices_invoice_category ON einvoices(invoice_category);
CREATE INDEX idx_einvoices_created_at ON einvoices(created_at);

-- Adım 5: Doğrulama
SELECT 'Migration basarili!' AS status,
       COUNT(*) as column_count 
FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'einvoices';
