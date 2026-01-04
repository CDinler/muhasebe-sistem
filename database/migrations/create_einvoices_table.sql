-- E-Faturalar Tablosu
-- MySQL için

CREATE TABLE IF NOT EXISTS einvoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Fatura Kimlik Bilgileri
    invoice_number VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    invoice_ettn VARCHAR(36),
    invoice_scenario VARCHAR(50),
    invoice_type VARCHAR(50),
    
    -- Alıcı Bilgileri
    buyer_name VARCHAR(255),
    buyer_tax_number VARCHAR(20),
    buyer_tax_office VARCHAR(100),
    
    -- Satıcı Bilgileri
    supplier_name VARCHAR(255) NOT NULL,
    supplier_tax_number VARCHAR(20),
    supplier_tax_office VARCHAR(100),
    supplier_address TEXT,
    supplier_city VARCHAR(100),
    supplier_district VARCHAR(100),
    
    -- Para Birimi
    currency_code VARCHAR(3) DEFAULT 'TRY',
    exchange_rate DECIMAL(10, 4) DEFAULT 1.0000,
    
    -- KDV Matrah ve Tutarları
    vat_0_base DECIMAL(18, 2) DEFAULT 0,
    vat_0_amount DECIMAL(18, 2) DEFAULT 0,
    vat_1_base DECIMAL(18, 2) DEFAULT 0,
    vat_1_amount DECIMAL(18, 2) DEFAULT 0,
    vat_8_base DECIMAL(18, 2) DEFAULT 0,
    vat_8_amount DECIMAL(18, 2) DEFAULT 0,
    vat_10_base DECIMAL(18, 2) DEFAULT 0,
    vat_10_amount DECIMAL(18, 2) DEFAULT 0,
    vat_18_base DECIMAL(18, 2) DEFAULT 0,
    vat_18_amount DECIMAL(18, 2) DEFAULT 0,
    vat_20_base DECIMAL(18, 2) DEFAULT 0,
    vat_20_amount DECIMAL(18, 2) DEFAULT 0,
    
    -- Tutarlar
    line_extension_amount DECIMAL(18, 2) DEFAULT 0,
    tax_exclusive_amount DECIMAL(18, 2) DEFAULT 0,
    tax_inclusive_amount DECIMAL(18, 2) DEFAULT 0,
    allowance_total_amount DECIMAL(18, 2) DEFAULT 0,
    payable_amount DECIMAL(18, 2) NOT NULL,
    
    -- Durum ve İşlem Bilgileri
    import_status VARCHAR(20) DEFAULT 'pending',
    import_date DATETIME,
    accounting_transaction_id INT,
    notes TEXT,
    
    -- Zaman damgaları
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key
    FOREIGN KEY (accounting_transaction_id) REFERENCES transactions(id),
    
    -- Indexes
    INDEX idx_einvoices_number (invoice_number),
    INDEX idx_einvoices_date (invoice_date),
    INDEX idx_einvoices_ettn (invoice_ettn),
    INDEX idx_einvoices_supplier_tax (supplier_tax_number),
    INDEX idx_einvoices_import_status (import_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
