-- FUTURE MIGRATION: Remove deprecated related_invoice_number column
-- 
-- REASON: 
--   This field is redundant - we use invoice_transaction_mappings junction table
--   for invoice-transaction relationships (many-to-many support).
--
-- BEFORE RUNNING:
--   1. Ensure all invoice relationships are migrated to invoice_transaction_mappings
--   2. Backup data: SELECT id, transaction_number, related_invoice_number 
--      FROM transactions WHERE related_invoice_number IS NOT NULL;
--   3. Verify no application code uses this field
--
-- ROLLBACK:
--   ALTER TABLE transactions 
--   ADD COLUMN related_invoice_number VARCHAR(100) COMMENT 'DEPRECATED - Use invoice_transaction_mappings';

-- Remove the deprecated column
ALTER TABLE transactions 
DROP COLUMN related_invoice_number;

-- Add comment about the change
ALTER TABLE transactions 
COMMENT = 'Transaction headers - invoice relationships via invoice_transaction_mappings table';
