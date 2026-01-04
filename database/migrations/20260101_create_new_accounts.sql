-- ============================================================================
-- YENİ HESAPLARI OLUŞTURMA SCRIPT'İ
-- Tarih: 2026-01-01
-- Amaç: 191 detaylı yapı, iade hesabı, özel iletişim vergisi hesapları
-- ============================================================================

-- YEDEKLEME (Opsiyonel)
-- CREATE TABLE accounts_backup_20260101 AS SELECT * FROM accounts;

-- ============================================================================
-- 1. YENİ 191 HESAPLARI (Detaylı KDV Yapısı)
-- ============================================================================
INSERT INTO accounts (code, name, account_type, is_active) VALUES
-- Normal KDV (Tevkifatsız)
('191.01.001', 'İndirilecek KDV %1', 'ASSET', true),
('191.08.001', 'İndirilecek KDV %8', 'ASSET', true),
('191.10.001', 'İndirilecek KDV %10', 'ASSET', true),
('191.18.001', 'İndirilecek KDV %18', 'ASSET', true),
('191.20.001', 'İndirilecek KDV %20', 'ASSET', true),

-- Tevkifatlı KDV
('191.01.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %1', 'ASSET', true),
('191.08.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %8', 'ASSET', true),
('191.10.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %10', 'ASSET', true),
('191.18.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %18', 'ASSET', true),
('191.20.002', 'Sorumlu Sıfatıyla KDV Tevkifatı %20', 'ASSET', true)

ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    is_active = VALUES(is_active);

-- ============================================================================
-- 2. İADE HESABI
-- ============================================================================
INSERT INTO accounts (code, name, account_type, is_active) VALUES
('602.00002', 'Alıştan İadeler', 'INCOME', true)
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    is_active = VALUES(is_active);

-- ============================================================================
-- 3. ÖZEL İLETİŞİM VERGİSİ VE İLGİLİ HESAPLAR
-- ============================================================================
INSERT INTO accounts (code, name, account_type, is_active) VALUES
-- 689 - Diğer Olağan Dışı Gider ve Zararlar
('689.00001', '5035 Sayılı Kanuna Göre Özel İletişim Vergisi', 'EXPENSE', true),
('689.00005', 'Telsiz Kullanım Ücreti', 'EXPENSE', true),
-- Aracılık hesapları için 689'u kullanıyoruz (şablona göre)
-- 679 - Diğer Olağandışı Gelir ve Karlar (Düzeltmeler için)
('679.00001', 'Düzeltmeler (Negatif Fark)', 'INCOME', true),
-- 659 - Diğer Olağan Gelir ve Karlar (Pozitif fark için)
('659.00003', 'Düzeltmeler (Pozitif Fark)', 'INCOME', true),
-- Konaklama Vergisi
('740.00209', 'Konaklama Vergisi', 'EXPENSE', true)

ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    is_active = VALUES(is_active);

-- ============================================================================
-- 4. ESKİ 191 HESAPLARINI PASİFLEŞTİR (Henüz değil - veri geçişi sonrası)
-- ============================================================================
-- UPDATE accounts SET is_active = false WHERE code IN ('191.00001', '191.00002');
-- NOT: Bu adım veri migration'dan sonra yapılacak

-- ============================================================================
-- 5. KONTROL
-- ============================================================================
SELECT 
    '==============================================' as sep,
    'YENİ HESAPLAR OLUŞTURULDU' as durum,
    '==============================================' as sep2;

SELECT 
    'Toplam 191 Hesabı' as kategori,
    COUNT(*) as adet
FROM accounts
WHERE code LIKE '191.%.0%' AND is_active = true;

SELECT 
    code,
    name,
    account_type,
    is_active
FROM accounts
WHERE code IN (
    '191.01.001', '191.08.001', '191.10.001', '191.18.001', '191.20.001',
    '191.01.002', '191.08.002', '191.10.002', '191.18.002', '191.20.002',
    '602.00002',
    '689.00001', '689.00005', '679.00001', '659.00003', '740.00209'
)
ORDER BY code;

-- ============================================================================
-- NOTLAR:
-- 1. Eski 191.00001/191.00002 henüz pasifleştirilmedi (veri geçişi bekliyor)
-- 2. Yeni hesaplar aktif durumda
-- 3. ON DUPLICATE KEY UPDATE ile güvenli (tekrar çalıştırılabilir)
-- ============================================================================
