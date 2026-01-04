-- Hesap Planı Seed Data
-- Temel Türk muhasebe hesap planı

-- AKTİF HESAPLAR (1xx)
INSERT INTO accounts (code, name, account_type) VALUES
('100', 'KASA', 'asset'),
('101', 'ALINAN ÇEKLER', 'asset'),
('102', 'BANKALAR', 'asset'),
('120', 'ALICILAR', 'asset'),
('121', 'ALACAK SENETLERİ', 'asset'),
('131', 'PEŞİN ÖDENEN VERGİLER', 'asset'),
('191', 'İNDİRİLECEK KDV', 'asset');

-- PASİF HESAPLAR (2xx-3xx)
INSERT INTO accounts (code, name, account_type) VALUES
('320', 'SATICILAR', 'liability'),
('321', 'BORÇ SENETLERİ', 'liability'),
('360', 'ÖDENECEK VERGİ VE FONLAR', 'liability'),
('361', 'ÖDENECEK SOSYAL GÜVENLİK KESİNTİLERİ', 'liability'),
('391', 'HESAPLANAN KDV', 'liability');

-- SERMAYE HESAPLARI (5xx)
INSERT INTO accounts (code, name, account_type) VALUES
('500', 'SERMAYE', 'equity'),
('580', 'GEÇMİŞ YILLAR KARLARI', 'equity'),
('590', 'DÖNEM NET KARI', 'equity');

-- GELİR HESAPLARI (6xx)
INSERT INTO accounts (code, name, account_type) VALUES
('600', 'YURTİÇİ SATIŞLAR', 'income'),
('601', 'YURTDIŞI SATIŞLAR', 'income'),
('602', 'DİĞER GELİRLER', 'income');

-- GİDER HESAPLARI (7xx)
INSERT INTO accounts (code, name, account_type) VALUES
('710', 'DİREKT İLK MADDE VE MALZEME GİDERLERİ', 'expense'),
('720', 'DİREKT İŞÇİLİK GİDERLERİ', 'expense'),
('730', 'GENEL ÜRETİM GİDERLERİ', 'expense'),
('760', 'PAZARLAMA SATIŞ VE DAĞITIM GİDERLERİ', 'expense'),
('770', 'GENEL YÖNETİM GİDERLERİ', 'expense'),
('780', 'FİNANSMAN GİDERLERİ', 'expense');

SELECT 'Hesap planı seed data yüklendi: ' || COUNT(*) || ' hesap' AS status FROM accounts;
