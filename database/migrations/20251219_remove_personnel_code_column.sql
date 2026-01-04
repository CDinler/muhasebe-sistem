-- Remove unnecessary 'code' column from personnel table
-- TC Kimlik (tckn) zaten var, code gereksiz

-- Önce unique constraint varsa kaldır
ALTER TABLE personnel DROP INDEX IF EXISTS code;

-- Code kolonunu kaldır
ALTER TABLE personnel DROP COLUMN code;
