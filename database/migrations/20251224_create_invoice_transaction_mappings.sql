-- Junction table for invoice-transaction relationships
-- Replaces direct einvoices.transaction_id foreign key
-- Allows many-to-many and preserves relationships even when transactions are recreated

CREATE TABLE IF NOT EXISTS invoice_transaction_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    einvoice_id INT NOT NULL,
    transaction_id INT NOT NULL,
    document_number VARCHAR(100),
    mapping_type ENUM('auto', 'manual') DEFAULT 'auto',
    confidence_score DECIMAL(3,2) DEFAULT 1.00,
    mapped_by INT NULL,
    mapped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    INDEX idx_einvoice (einvoice_id),
    INDEX idx_transaction (transaction_id),
    INDEX idx_document (document_number),
    INDEX idx_mapping_type (mapping_type),
    FOREIGN KEY (einvoice_id) REFERENCES einvoices(id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_mapping (einvoice_id, transaction_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Migrate existing einvoices.transaction_id data
INSERT INTO invoice_transaction_mappings 
    (einvoice_id, transaction_id, document_number, mapping_type, confidence_score, mapped_at)
SELECT 
    e.id,
    e.transaction_id,
    e.invoice_number,
    'auto' as mapping_type,
    1.00 as confidence_score,
    NOW() as mapped_at
FROM einvoices e
WHERE e.transaction_id IS NOT NULL
AND e.invoice_category = 'incoming';

-- Add comment
ALTER TABLE invoice_transaction_mappings 
COMMENT = 'Junction table for einvoice-transaction relationships';
