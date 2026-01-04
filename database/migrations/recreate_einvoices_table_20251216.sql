-- E-FATURA TABLOSU YENİDEN YAPILANDIRMA MİGRATION
-- Tarih: 16 Aralık 2025
-- Amaç: XML bazlı, ID ilişkili, eksiksiz veri yapısı

-- 1. Eski tabloyu yedekle
CREATE TABLE IF NOT EXISTS einvoices_backup_20251216 AS 
SELECT * FROM einvoices;

-- 2. Eski tabloyu sil
DROP TABLE IF EXISTS einvoices CASCADE;

-- 3. Yeni tablo yapısını oluştur
CREATE TABLE einvoices (
    id SERIAL PRIMARY KEY,
    
    -- XML Bilgisi
    xml_file_path VARCHAR(500) UNIQUE NOT NULL,
    xml_hash VARCHAR(64) UNIQUE NOT NULL,
    invoice_category VARCHAR(50) DEFAULT 'incoming',  -- incoming, outgoing, incoming-archive, outgoing-archive
    
    -- Temel Fatura Bilgileri (UBL-TR)
    invoice_uuid VARCHAR(36) UNIQUE NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    invoice_profile VARCHAR(100),  -- TEMELFATURA, TICARIFATURA, EARSIVFATURA
    invoice_type VARCHAR(50),      -- SATIS, IADE, TEVKIFAT
    
    -- Tarih Bilgileri
    issue_date DATE NOT NULL,
    issue_time TIME,
    tax_point_date DATE,           -- Vergi tarihi (varsa)
    
    -- Tedarikçi (Supplier) Bilgileri
    supplier_tax_number VARCHAR(11),
    supplier_id_scheme VARCHAR(10),  -- VKN veya TCKN
    supplier_name VARCHAR(255),
    supplier_address TEXT,
    supplier_city VARCHAR(100),
    supplier_district VARCHAR(100),
    supplier_postal_code VARCHAR(10),
    supplier_tax_office VARCHAR(100),
    supplier_email VARCHAR(255),
    supplier_phone VARCHAR(20),
    
    -- Alıcı (Customer) Bilgileri (genelde biz)
    customer_tax_number VARCHAR(11),
    customer_name VARCHAR(255),
    
    -- Parasal Bilgiler (Decimal 18,2)
    line_extension_amount DECIMAL(18, 2),   -- Mal/Hizmet Toplamı
    tax_exclusive_amount DECIMAL(18, 2),    -- Vergiler Hariç
    tax_inclusive_amount DECIMAL(18, 2),    -- Vergiler Dahil
    payable_amount DECIMAL(18, 2),          -- Ödenecek Tutar
    allowance_total DECIMAL(18, 2),         -- İndirim Toplamı
    charge_total DECIMAL(18, 2),            -- Masraf Toplamı
    
    -- Vergi Bilgileri
    total_tax_amount DECIMAL(18, 2),        -- KDV Toplamı
    withholding_tax_amount DECIMAL(18, 2),  -- Tevkifat Tutarı
    withholding_percent DECIMAL(5, 2),      -- Tevkifat Oranı
    withholding_code VARCHAR(10),           -- Tevkifat Kodu
    
    -- İlişkiler (ID bazlı - Foreign Keys)
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE SET NULL,
    
    -- Durum Takibi
    processing_status VARCHAR(50) DEFAULT 'IMPORTED',
    -- IMPORTED: XML parse edildi
    -- MATCHED: Contact eşleştirildi  
    -- ACCOUNTED: Muhasebe kaydı oluşturuldu
    -- ERROR: Hata var
    
    error_message TEXT,
    
    -- Raw Data (Tüm XML parse edilmiş JSON)
    raw_data JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imported_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT check_tax_number_length CHECK (
        supplier_tax_number IS NULL OR 
        LENGTH(supplier_tax_number) BETWEEN 10 AND 11
    ),
    CONSTRAINT check_processing_status CHECK (
        processing_status IN ('IMPORTED', 'MATCHED', 'ACCOUNTED', 'ERROR')
    ),
    CONSTRAINT check_invoice_category CHECK (
        invoice_category IN ('incoming', 'outgoing', 'incoming-archive', 'outgoing-archive')
    )
);

-- 4. İndeksler (Performans için)
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

-- JSONB için GIN index (hızlı JSON arama)
CREATE INDEX idx_einvoices_raw_data ON einvoices USING GIN(raw_data);

-- 5. Trigger: updated_at otomatik güncelleme
CREATE OR REPLACE FUNCTION update_einvoices_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_einvoices_updated_at
    BEFORE UPDATE ON einvoices
    FOR EACH ROW
    EXECUTE FUNCTION update_einvoices_updated_at();

-- 6. Yorum ekle (Dokümantasyon)
COMMENT ON TABLE einvoices IS 'E-Fatura ve E-Arşiv faturalar (UBL-TR 1.2 standardı)';
COMMENT ON COLUMN einvoices.xml_file_path IS 'XML dosyasının relative path (data/einvoices/incoming/2024/...)';
COMMENT ON COLUMN einvoices.xml_hash IS 'SHA256 hash - Mükerrer kontrol için';
COMMENT ON COLUMN einvoices.invoice_category IS 'Fatura kategorisi (gelen/giden, efatura/earsiv)';
COMMENT ON COLUMN einvoices.contact_id IS 'Tedarikçi/Müşteri ID (Foreign Key)';
COMMENT ON COLUMN einvoices.transaction_id IS 'İlişkili yevmiye fişi ID (Foreign Key)';
COMMENT ON COLUMN einvoices.processing_status IS 'İşlem durumu takibi';
COMMENT ON COLUMN einvoices.raw_data IS 'XML parse edilmiş tüm veri (JSONB)';

-- 7. Başarı mesajı
DO $$
BEGIN
    RAISE NOTICE '✅ E-Fatura tablosu başarıyla oluşturuldu!';
    RAISE NOTICE 'Yedek tablo: einvoices_backup_20251216';
    RAISE NOTICE 'Toplam alan sayısı: %', (
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'einvoices'
    );
END $$;
