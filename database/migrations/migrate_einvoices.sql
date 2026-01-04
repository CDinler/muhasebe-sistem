-- ============================================================================
-- E-FATURA TABLOSU YENİLEME MİGRATION
-- Tarih: 2024-12-16
-- Amaç: einvoices tablosunu UBL-TR şemasına göre yeniden oluşturmak
-- ============================================================================

-- 1. Yedek al
CREATE TABLE IF NOT EXISTS einvoices_backup_20251216 AS SELECT * FROM einvoices;

-- 2. Eski tabloyu sil
DROP TABLE IF EXISTS einvoices;

-- 3. Yeni tabloyu oluştur
CREATE TABLE einvoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- XML Tracking
    xml_file_path VARCHAR(500) UNIQUE NOT NULL COMMENT 'XML dosyasinin tam yolu',
    xml_hash VARCHAR(64) UNIQUE NOT NULL COMMENT 'SHA256 hash - mukerrer kontrol',
    invoice_category VARCHAR(50) DEFAULT 'incoming' COMMENT 'incoming/outgoing/incoming-archive/outgoing-archive',
    
    -- Invoice Core (UBL-TR)
    invoice_uuid VARCHAR(36) UNIQUE NOT NULL COMMENT 'cbc:UUID - Fatura ETTN',
    invoice_number VARCHAR(50) NOT NULL COMMENT 'cbc:ID - Fatura numarasi',
    invoice_profile VARCHAR(100) COMMENT 'cbc:ProfileID - TEMELFATURA, TICARIFATURA, EARSIVFATURA',
    invoice_type VARCHAR(50) COMMENT 'cbc:InvoiceTypeCode - SATIS, IADE, TEVKIFAT',
    
    -- Dates
    issue_date DATE NOT NULL COMMENT 'cbc:IssueDate - Duzenlenme tarihi',
    issue_time TIME COMMENT 'cbc:IssueTime - Duzenlenme saati',
    tax_point_date DATE COMMENT 'cbc:TaxPointDate - Vergilendirme tarihi',
    
    -- Supplier (Satici - 10 alan)
    supplier_tax_number VARCHAR(11) COMMENT 'VKN/TCKN - Satici vergi kimlik no',
    supplier_id_scheme VARCHAR(10) COMMENT 'VKN veya TCKN',
    supplier_name VARCHAR(255) COMMENT 'Satici unvan',
    supplier_address TEXT COMMENT 'Satici adres',
    supplier_city VARCHAR(100) COMMENT 'Satici sehir',
    supplier_district VARCHAR(100) COMMENT 'Satici ilce',
    supplier_postal_code VARCHAR(10) COMMENT 'Satici posta kodu',
    supplier_tax_office VARCHAR(100) COMMENT 'Satici vergi dairesi',
    supplier_email VARCHAR(255) COMMENT 'Satici e-posta',
    supplier_phone VARCHAR(20) COMMENT 'Satici telefon',
    
    -- Customer (Alici - 2 alan)
    customer_tax_number VARCHAR(11) COMMENT 'VKN/TCKN - Alici vergi kimlik no',
    customer_name VARCHAR(255) COMMENT 'Alici unvan',
    
    -- Amounts (Tutarlar - 6 alan)
    line_extension_amount DECIMAL(18, 2) COMMENT 'cbc:LineExtensionAmount - Mal hizmet toplam tutari',
    tax_exclusive_amount DECIMAL(18, 2) COMMENT 'cbc:TaxExclusiveAmount - Vergiler haric tutar',
    tax_inclusive_amount DECIMAL(18, 2) COMMENT 'cbc:TaxInclusiveAmount - Vergiler dahil tutar',
    payable_amount DECIMAL(18, 2) COMMENT 'cbc:PayableAmount - Odenecek tutar',
    allowance_total DECIMAL(18, 2) COMMENT 'Toplam indirim',
    charge_total DECIMAL(18, 2) COMMENT 'Toplam artirim',
    
    -- Tax (Vergiler - 4 alan)
    total_tax_amount DECIMAL(18, 2) COMMENT 'KDV toplami',
    withholding_tax_amount DECIMAL(18, 2) COMMENT 'Tevkifat tutari',
    withholding_percent DECIMAL(5, 2) COMMENT 'Tevkifat orani',
    withholding_code VARCHAR(10) COMMENT 'Tevkifat kodu',
    
    -- Foreign Keys (Iliskiler - 3 alan)
    contact_id INT NULL COMMENT 'contacts tablosu ile iliski',
    transaction_id INT NULL COMMENT 'transactions tablosu ile iliski',
    imported_by INT NULL COMMENT 'Import eden kullanici',
    
    -- Status (Durum - 2 alan)
    processing_status VARCHAR(50) DEFAULT 'IMPORTED' COMMENT 'IMPORTED, MATCHED, TRANSACTION_CREATED, ERROR',
    error_message TEXT COMMENT 'Hata mesaji',
    
    -- Raw Data (Ham veri - 1 alan)
    raw_data JSON COMMENT 'Orijinal XML verisi JSON formatinda',
    
    -- Metadata (2 alan)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE SET NULL,
    FOREIGN KEY (imported_by) REFERENCES users(id) ON DELETE SET NULL
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='E-Fatura kayitlari (UBL-TR 1.2 semasi)';

-- 4. İndeksler
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

-- 5. Dogrulama
SELECT 'Migration basarili!' AS status,
       COUNT(*) as column_count 
FROM information_schema.columns 
WHERE table_schema = 'muhasebe_sistem' 
  AND table_name = 'einvoices';
