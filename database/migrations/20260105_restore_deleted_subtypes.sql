-- =============================================================================================================
-- SİLİNEN DOCUMENT_SUBTYPES SATIRLARINI GERİ GETİRME
-- Tarih: 2026-01-05
-- Açıklama: 23, 24, 25, 27, 28 ID'li satırları geri getiriyoruz
-- =============================================================================================================

-- ⚠️ ÖNCE KONTROL: Bu ID'ler kullanılıyor mu?
SELECT 
    'KONTROL: Transactions tablosunda bu ID ler kullanılıyor mu?' AS mesaj,
    COUNT(*) AS kullanim_sayisi
FROM transactions
WHERE document_subtype_id IN (23, 24, 25, 27, 28);

-- ⚠️ KONTROL: Mevcut document_subtypes kayıtlarını göster
SELECT 
    id, 
    parent_code, 
    code, 
    name 
FROM document_subtypes 
WHERE id <= 30
ORDER BY id;

-- =============================================================================================================
-- GERİ YÜKLEME İŞLEMİ
-- =============================================================================================================

-- Eğer yukarıdaki kontroller OK ise aşağıdaki INSERT komutlarını çalıştırın:

-- ID 23: ALIS_FATURASI -> E_FATURA
INSERT INTO document_subtypes (id, parent_code, code, name, description, sort_order, is_active, created_at, updated_at) 
VALUES (
    23,
    'ALIS_FATURASI',
    'E_FATURA',
    'E-Fatura',
    'E-Fatura (işletmeden alış)',
    10,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    parent_code = 'ALIS_FATURASI',
    code = 'E_FATURA',
    name = 'E-Fatura',
    description = 'E-Fatura (işletmeden alış)',
    sort_order = 10,
    is_active = 1,
    updated_at = NOW();

-- ID 24: ALIS_FATURASI -> E_ARSIV
INSERT INTO document_subtypes (id, parent_code, code, name, description, sort_order, is_active, created_at, updated_at) 
VALUES (
    24,
    'ALIS_FATURASI',
    'E_ARSIV',
    'E-Arşiv',
    'E-Arşiv (perakendeden alış)',
    20,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    parent_code = 'ALIS_FATURASI',
    code = 'E_ARSIV',
    name = 'E-Arşiv',
    description = 'E-Arşiv (perakendeden alış)',
    sort_order = 20,
    is_active = 1,
    updated_at = NOW();

-- ID 25: ALIS_FATURASI -> KAGIT_MATBU
INSERT INTO document_subtypes (id, parent_code, code, name, description, sort_order, is_active, created_at, updated_at) 
VALUES (
    25,
    'ALIS_FATURASI',
    'KAGIT_MATBU',
    'Kağıt/Matbu',
    'Kağıt/Matbu fatura',
    30,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    parent_code = 'ALIS_FATURASI',
    code = 'KAGIT_MATBU',
    name = 'Kağıt/Matbu',
    description = 'Kağıt/Matbu fatura',
    sort_order = 30,
    is_active = 1,
    updated_at = NOW();

-- ID 27: SATIS_FATURASI -> E_FATURA
INSERT INTO document_subtypes (id, parent_code, code, name, description, sort_order, is_active, created_at, updated_at) 
VALUES (
    27,
    'SATIS_FATURASI',
    'E_FATURA',
    'E-Fatura',
    'E-Fatura (işletmeye satış)',
    50,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    parent_code = 'SATIS_FATURASI',
    code = 'E_FATURA',
    name = 'E-Fatura',
    description = 'E-Fatura (işletmeye satış)',
    sort_order = 50,
    is_active = 1,
    updated_at = NOW();

-- ID 28: SATIS_FATURASI -> E_ARSIV
INSERT INTO document_subtypes (id, parent_code, code, name, description, sort_order, is_active, created_at, updated_at) 
VALUES (
    28,
    'SATIS_FATURASI',
    'E_ARSIV',
    'E-Arşiv',
    'E-Arşiv (perakendeye satış)',
    60,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    parent_code = 'SATIS_FATURASI',
    code = 'E_ARSIV',
    name = 'E-Arşiv',
    description = 'E-Arşiv (perakendeye satış)',
    sort_order = 60,
    is_active = 1,
    updated_at = NOW();

-- =============================================================================================================
-- SON KONTROL
-- =============================================================================================================

-- Geri yüklenen kayıtları kontrol et
SELECT 
    id, 
    parent_code, 
    code, 
    name,
    description,
    sort_order,
    is_active
FROM document_subtypes 
WHERE id IN (23, 24, 25, 27, 28)
ORDER BY id;

-- Özet rapor
SELECT 
    'GERİ YÜKLEME TAMAMLANDI' AS mesaj,
    COUNT(*) AS toplam_kayit
FROM document_subtypes 
WHERE id IN (23, 24, 25, 27, 28);
