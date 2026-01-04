-- Fiş numarası sayaç tablosu
CREATE TABLE IF NOT EXISTS transaction_counter (
    id INT PRIMARY KEY DEFAULT 1,
    last_number INT NOT NULL
);

-- Mevcut fiş numaralarını işle
INSERT INTO transaction_counter (id, last_number)
SELECT 1, MAX(CAST(SUBSTRING(transaction_number, 2, 8) AS UNSIGNED))
FROM transactions
WHERE transaction_number REGEXP '^F[0-9]{8}$';

-- Eğer hiç fiş yoksa, sıfırdan başlat
UPDATE transaction_counter SET last_number = COALESCE(last_number, 0) WHERE id = 1;
