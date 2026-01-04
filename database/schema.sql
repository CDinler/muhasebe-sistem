-- Muhasebe Database Schema
-- PostgreSQL 15+
-- Created: 14 Aralık 2025

-- Database oluştur
CREATE DATABASE muhasebe_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'Turkish_Turkey.1254'
    LC_CTYPE = 'Turkish_Turkey.1254'
    TEMPLATE = template0;

\c muhasebe_db

-- 1. Hesap Planı
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- asset, liability, equity, income, expense
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_account_type CHECK (account_type IN ('asset', 'liability', 'equity', 'income', 'expense'))
);

CREATE INDEX idx_accounts_code ON accounts(code);
CREATE INDEX idx_accounts_type ON accounts(account_type);

-- 2. Maliyet Merkezleri (Şantiyeler)
CREATE TABLE cost_centers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_cost_centers_code ON cost_centers(code);

-- 3. Cari Hesaplar
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    tax_number VARCHAR(20) UNIQUE,
    tax_office VARCHAR(100),
    contact_type VARCHAR(50) DEFAULT 'both', -- customer, supplier, both
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(50),
    email VARCHAR(100),
    address VARCHAR(500)
);

CREATE INDEX idx_contacts_name ON contacts(name);
CREATE INDEX idx_contacts_tax_number ON contacts(tax_number);

-- 4. Fişler (Transaction Header)
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_number VARCHAR(50) UNIQUE NOT NULL,
    transaction_date DATE NOT NULL,
    accounting_period VARCHAR(7) NOT NULL, -- 2025-12 format
    cost_center_id INTEGER REFERENCES cost_centers(id),
    description TEXT,
    document_type VARCHAR(100),
    document_subtype VARCHAR(100),
    document_number VARCHAR(100),
    related_invoice_number VARCHAR(100)
);

CREATE INDEX idx_transactions_number ON transactions(transaction_number);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_period ON transactions(accounting_period);
CREATE INDEX idx_transactions_cost_center ON transactions(cost_center_id);

-- 5. Fiş Satırları (Transaction Lines)
CREATE TABLE transaction_lines (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    contact_id INTEGER REFERENCES contacts(id),
    description TEXT,
    debit NUMERIC(18, 2) DEFAULT 0,
    credit NUMERIC(18, 2) DEFAULT 0,
    quantity NUMERIC(18, 4),
    unit VARCHAR(20),
    CONSTRAINT chk_debit_credit CHECK ((debit >= 0 AND credit >= 0))
);

CREATE INDEX idx_transaction_lines_transaction ON transaction_lines(transaction_id);
CREATE INDEX idx_transaction_lines_account ON transaction_lines(account_id);
CREATE INDEX idx_transaction_lines_contact ON transaction_lines(contact_id);

-- 6. E-Faturalar
CREATE TABLE einvoices (
    id SERIAL PRIMARY KEY,
    
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
    exchange_rate NUMERIC(10, 4) DEFAULT 1.0000,
    
    -- KDV Matrah ve Tutarları
    vat_0_base NUMERIC(18, 2) DEFAULT 0,
    vat_0_amount NUMERIC(18, 2) DEFAULT 0,
    vat_1_base NUMERIC(18, 2) DEFAULT 0,
    vat_1_amount NUMERIC(18, 2) DEFAULT 0,
    vat_8_base NUMERIC(18, 2) DEFAULT 0,
    vat_8_amount NUMERIC(18, 2) DEFAULT 0,
    vat_10_base NUMERIC(18, 2) DEFAULT 0,
    vat_10_amount NUMERIC(18, 2) DEFAULT 0,
    vat_18_base NUMERIC(18, 2) DEFAULT 0,
    vat_18_amount NUMERIC(18, 2) DEFAULT 0,
    vat_20_base NUMERIC(18, 2) DEFAULT 0,
    vat_20_amount NUMERIC(18, 2) DEFAULT 0,
    
    -- Tutarlar
    line_extension_amount NUMERIC(18, 2) DEFAULT 0,
    tax_exclusive_amount NUMERIC(18, 2) DEFAULT 0,
    tax_inclusive_amount NUMERIC(18, 2) DEFAULT 0,
    allowance_total_amount NUMERIC(18, 2) DEFAULT 0,
    payable_amount NUMERIC(18, 2) NOT NULL,
    
    -- Durum ve İşlem Bilgileri
    import_status VARCHAR(20) DEFAULT 'pending', -- pending, imported, error
    import_date TIMESTAMP,
    accounting_transaction_id INTEGER REFERENCES transactions(id),
    notes TEXT,
    
    -- Zaman damgaları
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_einvoices_number ON einvoices(invoice_number);
CREATE INDEX idx_einvoices_date ON einvoices(invoice_date);
CREATE INDEX idx_einvoices_ettn ON einvoices(invoice_ettn);
CREATE INDEX idx_einvoices_supplier_tax ON einvoices(supplier_tax_number);
CREATE INDEX idx_einvoices_import_status ON einvoices(import_status);

-- 7. Kullanıcılar
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'muhasebeci', -- patron, muhasebeci, santiye
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- Başarılı mesajı
SELECT 'Database schema created successfully!' AS status;
