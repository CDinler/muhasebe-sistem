-- =============================================================================================================
-- KAPSAMLI EVRAK TÜRÜ SİSTEMİ - 3 Sütunlu Yapı
-- Oluşturma Tarihi: 2025-12-30
-- Amaç: Ana evrak türü (document_types) ve alt türleri (document_subtypes) ile standart sınıflandırma
-- Türkçe karakter desteği: utf8mb4_turkish_ci collation
-- =============================================================================================================

-- 1. MEVCUT TABLOLARI YEDEKLE (Opsiyonel)
-- ============================================================================
-- DROP TABLE IF EXISTS document_types_backup;
-- CREATE TABLE document_types_backup AS SELECT * FROM document_types;
-- DROP TABLE IF EXISTS document_subtypes_backup;
-- CREATE TABLE document_subtypes_backup AS SELECT * FROM document_subtypes;

-- 2. MEVCUT TABLOLARI TEMİZLE
-- ============================================================================
TRUNCATE TABLE document_subtypes;
TRUNCATE TABLE document_types;

-- 3. ANA EVRAK TÜRLERİ - Türkçe Karakter Desteği ile
-- ============================================================================
INSERT INTO document_types (code, name, category, sort_order) VALUES
-- 🔷 A. FATURALAR (Invoices)
('ALIS_FATURASI', 'Alış Faturası', 'FATURA', 10),
('SATIS_FATURASI', 'Satış Faturası', 'FATURA', 20),
('IADE_FATURASI', 'İade Faturası', 'FATURA', 30),
('HAKEDIS_FATURASI', 'Hakediş Faturası', 'FATURA', 40),
('PROFORMA_FATURA', 'Proforma Fatura', 'FATURA', 50),

-- 🔷 B. NAKİT/BANKA İŞLEMLERİ (Cash/Bank Transactions)
('KASA_TAHSILAT', 'Kasa Tahsilat Fişi', 'KASA', 100),
('KASA_TEDIYE', 'Kasa Tediye Fişi', 'KASA', 110),
('BANKA_TAHSILAT', 'Banka Tahsilat Fişi', 'BANKA', 120),
('BANKA_TEDIYE', 'Banka Tediye Fişi', 'BANKA', 130),
('DEKONT', 'Dekont', 'BANKA', 140),
('VIRMAN', 'Virman Fişi', 'BANKA', 150),

-- 🔷 C. KIYMETLİ EVRAK (Negotiable Instruments)
('ALINAN_CEK', 'Alınan Çek', 'CEK_SENET', 200),
('VERILEN_CEK', 'Verilen Çek', 'CEK_SENET', 210),
('CEK_TAHSILAT_ODEME', 'Çek Tahsilat/Ödeme', 'CEK_SENET', 220),
('ALINAN_SENET', 'Alınan Senet', 'CEK_SENET', 230),
('VERILEN_SENET', 'Verilen Senet', 'CEK_SENET', 240),
('SENET_TAHSILAT_ODEME', 'Senet Tahsilat/Ödeme', 'CEK_SENET', 250),

-- 🔷 D. PERSONEL İŞLEMLERİ (Payroll)
('MAAS_BORDROSU', 'Maaş Bordrosu', 'PERSONEL', 300),
('SGK_BILDIRGESI', 'SGK Bildirgesi', 'PERSONEL', 310),

-- 🔷 E. GİDER BELGELERİ (Expense Documents)
('GIDER_PUSULASI', 'Gider Pusulası', 'GIDER', 400),
('SERBEST_MESLEK_MAKBUZU', 'Serbest Meslek Makbuzu', 'GIDER', 410),
('MUSTAHSIL_MAKBUZU', 'Müstahsil Makbuzu', 'GIDER', 420),

-- 🔷 F. VERGİ İŞLEMLERİ (Tax Operations)
('VERGI_BEYANNAMESI', 'Vergi Beyannamesi', 'VERGI', 500),
('VERGI_ODEME', 'Vergi Ödeme', 'VERGI', 510),

-- 🔷 G. MUHASEBE FİŞLERİ (Accounting Vouchers)
('MAHSUP_FISI', 'Mahsup Fişi', 'MUHASEBE', 600),
('YEVMIYE_FISI', 'Yevmiye Fişi (Genel Fiş)', 'MUHASEBE', 610),
('ACILIS_FISI', 'Açılış Fişi', 'MUHASEBE', 620),
('KAPANIS_FISI', 'Kapanış Fişi', 'MUHASEBE', 630),
('DUZELTICI_FIS', 'Düzeltici Fiş', 'MUHASEBE', 640),
('TERS_KAYIT', 'Ters Kayıt', 'MUHASEBE', 650),

-- 🔷 H. STOK İŞLEMLERİ (Inventory - İsteğe Bağlı)
('STOK_GIRIS', 'Stok Giriş Fişi', 'STOK', 700),
('STOK_CIKIS', 'Stok Çıkış Fişi', 'STOK', 710),
('SAYIM_FISI', 'Sayım Fişi', 'STOK', 720),
('AMORTISMAN_FISI', 'Amortisman Fişi', 'STOK', 730);

-- 4. ALT EVRAK TÜRLERİ - Türkçe Karakter Desteği ile
-- ============================================================================
INSERT INTO document_subtypes (code, name, category, sort_order) VALUES
-- A. FATURALAR - Alt Türler
('E_FATURA', 'E-Fatura', 'E_BELGE', 10),
('E_ARSIV', 'E-Arşiv', 'E_BELGE', 20),
('KAGIT_MATBU', 'Kağıt/Matbu', 'E_BELGE', 30),
('ITHALAT', 'İthalat', 'E_BELGE', 40),
('IHRACAT', 'İhracat', 'E_BELGE', 50),
('ALIS_IADE', 'Alış İade', 'FATURA', 60),
('SATIS_IADE', 'Satış İade', 'FATURA', 70),

-- B. NAKİT/BANKA İŞLEMLERİ - Alt Türler
('NAKIT', 'Nakit', 'KASA', 100),
('CEK', 'Çek', 'KASA', 110),
('SENET', 'Senet', 'KASA', 120),
('EFT_HAVALE', 'EFT/Havale', 'BANKA', 130),
('POS', 'POS', 'BANKA', 140),
('KREDI_KARTI', 'Kredi Kartı', 'BANKA', 150),
('BANKA_DEKONT', 'Banka Dekontu', 'BANKA', 160),
('POS_DEKONT', 'POS Dekontu', 'BANKA', 170),
('ATM_DEKONT', 'ATM Dekontu', 'BANKA', 180),
('KASA_KASA', 'Kasa-Kasa', 'VIRMAN', 190),
('BANKA_BANKA', 'Banka-Banka', 'VIRMAN', 200),
('KASA_BANKA', 'Kasa-Banka', 'VIRMAN', 210),

-- C. KIYMETLİ EVRAK - Alt Türler
('MUSTERI_CEKI', 'Müşteri Çeki', 'CEK_SENET', 300),
('CIRO_CEKI', 'Ciro Çeki', 'CEK_SENET', 310),
('TEMINAT_CEKI', 'Teminat Çeki', 'CEK_SENET', 320),
('TEDARIKCI_CEKI', 'Tedarikçi Çeki', 'CEK_SENET', 330),
('CEK_TAHSIL', 'Tahsil', 'CEK_SENET', 340),
('CEK_ODEME', 'Ödeme', 'CEK_SENET', 350),
('CEK_IADE', 'İade', 'CEK_SENET', 360),
('CEK_PROTESTO', 'Protestosu', 'CEK_SENET', 370),
('MUSTERI_SENEDI', 'Müşteri Senedi', 'CEK_SENET', 380),
('TEDARIKCI_SENEDI', 'Tedarikçi Senedi', 'CEK_SENET', 390),
('SENET_TAHSIL', 'Tahsil', 'CEK_SENET', 400),
('SENET_ODEME', 'Ödeme', 'CEK_SENET', 410),
('SENET_PROTESTO', 'Protestosu', 'CEK_SENET', 420),

-- D. PERSONEL İŞLEMLERİ - Alt Türler
('AYLIK_MAAS', 'Aylık Maaş', 'PERSONEL', 500),
('PRIM', 'Prim', 'PERSONEL', 510),
('IKRAMIYE', 'İkramiye', 'PERSONEL', 520),
('AGI', 'AGİ', 'PERSONEL', 530),
('KIDEM_IHBAR', 'Kıdem/İhbar', 'PERSONEL', 540),
('AYLIK_BILDIRGE', 'Aylık Bildirge', 'PERSONEL', 550),
('ISE_GIRIS_CIKIS', 'İşe Giriş/Çıkış', 'PERSONEL', 560),

-- E. GİDER BELGELERİ - Alt Türler (yok - direkt ana tür)

-- F. VERGİ İŞLEMLERİ - Alt Türler
('KDV_BEYANI', 'KDV', 'VERGI', 600),
('MUHTASAR_BEYANI', 'Muhtasar', 'VERGI', 610),
('GECICI_VERGI', 'Geçici Vergi', 'VERGI', 620),
('YILLIK_GELIR', 'Yıllık Gelir', 'VERGI', 630),
('STOPAJ_BEYANI', 'Stopaj', 'VERGI', 640),
('KDV_ODEME', 'KDV', 'VERGI', 650),
('STOPAJ_ODEME', 'Stopaj', 'VERGI', 660),
('GELIR_VERGISI_ODEME', 'Gelir Vergisi', 'VERGI', 670),
('DAMGA_VERGISI', 'Damga Vergisi', 'VERGI', 680),

-- G. MUHASEBE FİŞLERİ - Alt Türler
('CARI_MAHSUP', 'Cari Mahsup', 'MUHASEBE', 700),
('CEK_SENET_MAHSUP', 'Çek/Senet Mahsup', 'MUHASEBE', 710),
('DONEM_ACILIS', 'Dönem Açılış', 'MUHASEBE', 720),
('ISLETME_ACILIS', 'İşletme Açılış', 'MUHASEBE', 730),
('DONEM_KAPANIS', 'Dönem Kapanış', 'MUHASEBE', 740),

-- H. STOK İŞLEMLERİ - Alt Türler
('SATIN_ALIM', 'Satın Alım', 'STOK', 800),
('SATIS_IADESI_GIRIS', 'Satış İadesi', 'STOK', 810),
('FIRE_GIRIS', 'Fire', 'STOK', 820),
('SATIS_CIKIS', 'Satış', 'STOK', 830),
('ALIS_IADESI_CIKIS', 'Alış İadesi', 'STOK', 840),
('FIRE_CIKIS', 'Fire', 'STOK', 850);

-- 5. MEVCUT VERİLERİ YENİ YAPIYA MAPLEMEK İÇİN GEÇİCİ TABLO
-- ============================================================================
-- Bu tabloda eski değerlerin yeni değerlere mapping'i tutulur
DROP TABLE IF EXISTS document_migration_map;
CREATE TABLE document_migration_map (
    id INT AUTO_INCREMENT PRIMARY KEY,
    old_document_type VARCHAR(100),
    old_document_subtype VARCHAR(100),
    new_document_type_code VARCHAR(50),
    new_document_subtype_code VARCHAR(50),
    record_count INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_old_type (old_document_type),
    INDEX idx_old_subtype (old_document_subtype)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- 6. MEVCUT VERİLERDEN MAPPİNG TABLOSUNU DOLDUR
-- ============================================================================
INSERT INTO document_migration_map (old_document_type, old_document_subtype, record_count)
SELECT 
    document_type,
    document_subtype,
    COUNT(*) as record_count
FROM transactions
WHERE (document_type IS NOT NULL AND document_type != '')
   OR (document_subtype IS NOT NULL AND document_subtype != '')
GROUP BY document_type, document_subtype
ORDER BY record_count DESC;

-- 7. OTOMATİK MAPPİNG (Türkçe Karakter Uyumlu)
-- ============================================================================
-- Ana Evrak Türü Eşleştirmeleri
UPDATE document_migration_map m
SET m.new_document_type_code = (
    CASE 
        -- FATURALAR
        WHEN m.old_document_type IN ('ALIŞ FATURASI', 'Alış Faturası', 'ALIS_FATURA') THEN 'ALIS_FATURASI'
        WHEN m.old_document_type IN ('SATIŞ FATURASI', 'Satış Faturası', 'SATIS_FATURA') THEN 'SATIS_FATURASI'
        WHEN m.old_document_type = 'PROFORMA FATURA' THEN 'PROFORMA_FATURA'
        WHEN m.old_document_type IN ('HAKEDİŞ RAPORU', 'Hakediş Raporu', 'HAKEDIS') THEN 'HAKEDIS_FATURASI'
        
        -- NAKİT/BANKA
        WHEN m.old_document_type IN ('KASA TAHSİLAT FİŞİ', 'Kasa Tahsilat Fişi', 'KASA_TAHSILAT') THEN 'KASA_TAHSILAT'
        WHEN m.old_document_type IN ('KASA TEDİYE FİŞİ', 'Kasa Tediye Fişi', 'KASA_TEDIYE') THEN 'KASA_TEDIYE'
        WHEN m.old_document_type IN ('BANKA TAHSİLAT FİŞİ', 'Banka Tahsilat Fişi', 'BANKA_TAHSILAT') THEN 'BANKA_TAHSILAT'
        WHEN m.old_document_type IN ('BANKA TEDİYE FİŞİ', 'Banka Tediye Fişi', 'BANKA_TEDIYE') THEN 'BANKA_TEDIYE'
        WHEN m.old_document_type = 'DEKONT' THEN 'DEKONT'
        WHEN m.old_document_type LIKE '%VİRMAN%' THEN 'VIRMAN'
        
        -- KIYMETLİ EVRAK
        WHEN m.old_document_type IN ('ALINAN ÇEK', 'Alınan Çek', 'ALINAN_CEK') THEN 'ALINAN_CEK'
        WHEN m.old_document_type IN ('VERİLEN ÇEK', 'Verilen Çek', 'VERILEN_CEK') THEN 'VERILEN_CEK'
        WHEN m.old_document_type LIKE '%ÇEK TAHSİLAT%' OR m.old_document_type LIKE '%ÇEK ÖDEME%' THEN 'CEK_TAHSILAT_ODEME'
        WHEN m.old_document_type IN ('ALINAN SENET', 'Alınan Senet') THEN 'ALINAN_SENET'
        WHEN m.old_document_type IN ('VERİLEN SENET', 'Verilen Senet') THEN 'VERILEN_SENET'
        
        -- PERSONEL
        WHEN m.old_document_type IN ('BORDRO', 'Bordro', 'Maaş Bordrosu') THEN 'MAAS_BORDROSU'
        WHEN m.old_document_type LIKE '%SGK%' THEN 'SGK_BILDIRGESI'
        
        -- GİDER
        WHEN m.old_document_type LIKE '%GİDER PUSULASI%' THEN 'GIDER_PUSULASI'
        WHEN m.old_document_type LIKE '%SERBEST MESLEK%' THEN 'SERBEST_MESLEK_MAKBUZU'
        WHEN m.old_document_type LIKE '%MÜSTAHSİL%' THEN 'MUSTAHSIL_MAKBUZU'
        
        -- VERGİ
        WHEN m.old_document_type LIKE '%VERGİ BEYAN%' THEN 'VERGI_BEYANNAMESI'
        WHEN m.old_document_type LIKE '%VERGİ ÖDEME%' THEN 'VERGI_ODEME'
        
        -- MUHASEBE
        WHEN m.old_document_type IN ('YEVMİYE FİŞİ', 'Yevmiye Fişi', 'YEVMIYE') THEN 'YEVMIYE_FISI'
        WHEN m.old_document_type LIKE '%MAHSUP%' THEN 'MAHSUP_FISI'
        WHEN m.old_document_type LIKE '%AÇILIŞ%' THEN 'ACILIS_FISI'
        WHEN m.old_document_type LIKE '%KAPANIŞ%' THEN 'KAPANIS_FISI'
        WHEN m.old_document_type LIKE '%DÜZELT%' THEN 'DUZELTICI_FIS'
        
        ELSE NULL
    END
)
WHERE m.new_document_type_code IS NULL;

-- Alt Evrak Türü Eşleştirmeleri
UPDATE document_migration_map m
SET m.new_document_subtype_code = (
    CASE
        -- E-BELGE
        WHEN m.old_document_subtype IN ('E-Fatura', 'E-FATURA', 'E_FATURA') THEN 'E_FATURA'
        WHEN m.old_document_subtype IN ('E-Arşiv', 'E-ARŞİV', 'E_ARSIV') THEN 'E_ARSIV'
        WHEN m.old_document_subtype IN ('Kağıt/Matbu', 'KAGIT_MATBU') THEN 'KAGIT_MATBU'
        
        -- KASA/BANKA
        WHEN m.old_document_subtype = 'Nakit' THEN 'NAKIT'
        WHEN m.old_document_subtype IN ('EFT/Havale', 'EFT_HAVALE') THEN 'EFT_HAVALE'
        WHEN m.old_document_subtype IN ('Kredi Kartı', 'KREDI_KARTI') THEN 'KREDI_KARTI'
        WHEN m.old_document_subtype = 'Dekont' THEN 'BANKA_DEKONT'
        
        -- ÇEK/SENET
        WHEN m.old_document_subtype IN ('Müşteri Çeki', 'MUSTERI_CEKI') THEN 'MUSTERI_CEKI'
        WHEN m.old_document_subtype IN ('Tedarikçi Çeki', 'TEDARIKCI_CEKI') THEN 'TEDARIKCI_CEKI'
        WHEN m.old_document_subtype IN ('Ödeme', 'ODEME') THEN 'CEK_ODEME'
        WHEN m.old_document_subtype IN ('Tahsilat', 'TAHSILAT') THEN 'CEK_TAHSIL'
        
        -- PERSONEL
        WHEN m.old_document_subtype IN ('Personel Ödemesi', 'PERSONEL_ODEME') THEN 'AYLIK_MAAS'
        WHEN m.old_document_subtype = 'Prim' THEN 'PRIM'
        WHEN m.old_document_subtype = 'Mesai' THEN 'PRIM'
        
        -- DİĞER
        WHEN m.old_document_subtype IN ('Serbest Meslek Makbuzu', 'SMM') THEN 'SERBEST_MESLEK_MAKBUZU'
        WHEN m.old_document_subtype IN ('Düzeltme/Mahsup', 'DUZELTME_MAHSUP') THEN 'CARI_MAHSUP'
        
        ELSE NULL
    END
)
WHERE m.new_document_subtype_code IS NULL;

-- 8. KONTROL VE DOĞRULAMA
-- ============================================================================
SELECT 
    '=============================================' as separator,
    'MAPPİNG DURUMU RAPORU' as rapor,
    '=============================================' as separator2;

SELECT 
    'Toplam Kayıt' as durum,
    COUNT(*) as sayi,
    SUM(record_count) as toplam_transaction
FROM document_migration_map;

SELECT 
    'Başarılı Map (Her İki Alan)' as durum,
    COUNT(*) as sayi,
    SUM(record_count) as toplam_transaction
FROM document_migration_map
WHERE new_document_type_code IS NOT NULL 
  AND new_document_subtype_code IS NOT NULL;

SELECT 
    'Sadece Ana Tür Map' as durum,
    COUNT(*) as sayi,
    SUM(record_count) as toplam_transaction
FROM document_migration_map
WHERE new_document_type_code IS NOT NULL 
  AND new_document_subtype_code IS NULL;

SELECT 
    'Başarısız (NULL)' as durum,
    COUNT(*) as sayi,
    SUM(record_count) as toplam_transaction
FROM document_migration_map
WHERE new_document_type_code IS NULL;

-- Başarısız mapping'leri göster (manuel düzeltme için)
SELECT 
    '=============================================' as separator,
    'MANUEL DÜZELTME GEREKLİ KAYITLAR' as baslik,
    '=============================================' as separator2;

SELECT 
    old_document_type,
    old_document_subtype,
    record_count,
    'MANUEL DÜZELT' as aksiyon
FROM document_migration_map
WHERE new_document_type_code IS NULL
ORDER BY record_count DESC;

-- ============================================================================
-- NOTLAR:
-- ============================================================================
-- 1. Bu migration transactions tablosunu henüz güncellemez
-- 2. Önce document_migration_map tablosunda tüm mapping'lerin doğru olduğundan emin olun
-- 3. Manuel düzeltmeler için:
--    UPDATE document_migration_map 
--    SET new_document_type_code = 'XX', new_document_subtype_code = 'YY' 
--    WHERE old_document_type = 'eski değer';
-- 4. Mapping onaylandıktan sonra ayrı bir migration ile transactions güncellenecek
-- ============================================================================
