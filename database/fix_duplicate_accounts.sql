-- Hesap planı duplikasyonlarını temizleme SQL script

-- ADIM 1: Kullanılmayan duplikasyonları bul ve sil
DELETE FROM accounts 
WHERE code IN ('100.0', '191.0', '320.0', '689.0', '770.0')
AND NOT EXISTS (
    SELECT 1 FROM transaction_lines tl 
    WHERE tl.account_id = accounts.id
);

-- ADIM 2: Kullanılan duplikasyonları birleştir (örnek: 100.0 → 100)
-- Önce transaction_lines'ı base hesaba taşı
UPDATE transaction_lines tl
JOIN accounts a_source ON tl.account_id = a_source.id
JOIN accounts a_target ON SUBSTRING_INDEX(a_source.code, '.', 1) = a_target.code
SET tl.account_id = a_target.id
WHERE a_source.code LIKE '%.0' 
AND a_source.code IN ('100.0', '191.0', '320.0', '689.0', '770.0')
AND a_target.code = SUBSTRING_INDEX(a_source.code, '.', 1);

-- Sonra duplikasyonu sil
DELETE FROM accounts 
WHERE code IN ('100.0', '191.0', '320.0', '689.0', '770.0');

-- ADIM 3: Doğrulama
SELECT 
    SUBSTRING_INDEX(code, '.', 1) as base_code,
    GROUP_CONCAT(code ORDER BY code) as all_codes,
    COUNT(*) as count
FROM accounts
WHERE code LIKE '100%' OR code LIKE '191%' OR code LIKE '320%' OR code LIKE '689%' OR code LIKE '770%'
GROUP BY SUBSTRING_INDEX(code, '.', 1)
HAVING count > 1;
