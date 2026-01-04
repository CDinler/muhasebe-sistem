-- E-FATURA TABLOSU ROLLBACK MİGRATION
-- Tarih: 16 Aralık 2025
-- Amaç: Yeni şemayı geri almak ve eski şemayı geri yüklemek

-- 1. Yeni tabloyu sil
DROP TABLE IF EXISTS einvoices CASCADE;

-- 2. Yedekten geri yükle (eğer varsa)
CREATE TABLE einvoices AS 
SELECT * FROM einvoices_backup_20251216;

-- 3. Primary key ve constraints ekle
ALTER TABLE einvoices ADD PRIMARY KEY (id);
ALTER TABLE einvoices ADD CONSTRAINT einvoices_contact_id_fkey 
    FOREIGN KEY (contact_id) REFERENCES contacts(id);
ALTER TABLE einvoices ADD CONSTRAINT einvoices_transaction_id_fkey 
    FOREIGN KEY (transaction_id) REFERENCES transactions(id);

-- 4. Sequence'i düzelt
SELECT setval('einvoices_id_seq', (SELECT MAX(id) FROM einvoices));

-- 5. İndeksleri yeniden oluştur
CREATE INDEX idx_einvoices_invoice_number ON einvoices(invoice_number);
CREATE INDEX idx_einvoices_supplier_tax_number ON einvoices(supplier_tax_number);
CREATE INDEX idx_einvoices_contact_id ON einvoices(contact_id);
CREATE INDEX idx_einvoices_transaction_id ON einvoices(transaction_id);

-- 6. Başarı mesajı
DO $$
BEGIN
    RAISE NOTICE '✅ Rollback tamamlandı! Eski şema geri yüklendi.';
    RAISE NOTICE 'Toplam kayıt sayısı: %', (SELECT COUNT(*) FROM einvoices);
END $$;
