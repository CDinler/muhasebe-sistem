-- ===================================================================
-- MUHASEBEDocument Subtypes Migration - YEVMIYE_KAYDI_SABLONU.md'ye göre
-- ===================================================================

-- 1. parent_code kolonu ekle
ALTER TABLE document_subtypes ADD COLUMN parent_code VARCHAR(50) AFTER code;
ALTER TABLE document_subtypes ADD INDEX idx_parent_code (parent_code);
ALTER TABLE document_subtypes ADD CONSTRAINT fk_subtype_parent FOREIGN KEY (parent_code) REFERENCES document_types(code);

-- 2. Mevcut kayıtları güncelle (varsa)
UPDATE document_subtypes SET parent_code = 'ALIS_FATURA' WHERE code IN ('E_FATURA', 'E_ARSIV', 'KAGIT_MATBU');

-- 3. 74 alt evrak türünü ekle (YEVMIYE_KAYDI_SABLONU.md'den)

-- FATURA kategorisi (5 ana tür)
-- ALIS_FATURASI (4 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('ALIS_E_FATURA', 'ALIS_FATURA', 'E-Fatura (Alış)', 'E_BELGE', 1, 1),
('ALIS_E_ARSIV', 'ALIS_FATURA', 'E-Arşiv (Alış)', 'E_BELGE', 2, 1),
('ALIS_KAGIT_MATBU', 'ALIS_FATURA', 'Kağıt/Matbu (Alış)', 'MANUEL', 3, 1),
('ALIS_ITHALAT', 'ALIS_FATURA', 'İthalat Faturası', 'MANUEL', 4, 1);

-- SATIS_FATURASI (4 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('SATIS_E_FATURA', 'SATIS_FATURA', 'E-Fatura (Satış)', 'E_BELGE', 1, 1),
('SATIS_E_ARSIV', 'SATIS_FATURA', 'E-Arşiv (Satış)', 'E_BELGE', 2, 1),
('SATIS_KAGIT_MATBU', 'SATIS_FATURA', 'Kağıt/Matbu (Satış)', 'MANUEL', 3, 1),
('SATIS_IHRACAT', 'SATIS_FATURA', 'İhracat Faturası', 'MANUEL', 4, 1);

-- IADE_FATURA (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('IADE_ALIS', 'IADE_FATURA', 'Alış İade', 'MANUEL', 1, 1),
('IADE_SATIS', 'IADE_FATURA', 'Satış İade', 'MANUEL', 2, 1);

-- HAKEDIS_FATURASI (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('HAKEDIS_GECICI', 'HAKEDIS_FATURASI', 'Geçici Hakediş', 'MANUEL', 1, 1),
('HAKEDIS_KESIN', 'HAKEDIS_FATURASI', 'Kesin Hakediş', 'MANUEL', 2, 1);

-- PROFORMA_FATURA (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('PROFORMA_NORMAL', 'PROFORMA_FATURA', 'Normal Proforma', 'MANUEL', 1, 1);

-- KASA kategorisi (2 ana tür)
-- KASA_TAHSILAT (3 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('KASA_TAHSILAT_NAKIT', 'KASA_TAHSILAT', 'Nakit Tahsilat', 'MANUEL', 1, 1),
('KASA_TAHSILAT_CEK', 'KASA_TAHSILAT', 'Çek Tahsilat', 'MANUEL', 2, 1),
('KASA_TAHSILAT_SENET', 'KASA_TAHSILAT', 'Senet Tahsilat', 'MANUEL', 3, 1);

-- KASA_TEDIYE (3 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('KASA_TEDIYE_NAKIT', 'KASA_TEDIYE', 'Nakit Ödeme', 'MANUEL', 1, 1),
('KASA_TEDIYE_CEK', 'KASA_TEDIYE', 'Çek Ödeme', 'MANUEL', 2, 1),
('KASA_TEDIYE_SENET', 'KASA_TEDIYE', 'Senet Ödeme', 'MANUEL', 3, 1);

-- BANKA kategorisi (4 ana tür)
-- BANKA_TAHSILAT (4 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('BANKA_TAHSILAT_EFT', 'BANKA_TAHSILAT', 'EFT/Havale', 'OTOMATIK', 1, 1),
('BANKA_TAHSILAT_KART', 'BANKA_TAHSILAT', 'Kredi Kartı', 'OTOMATIK', 2, 1),
('BANKA_TAHSILAT_CEK', 'BANKA_TAHSILAT', 'Çek', 'OTOMATIK', 3, 1),
('BANKA_TAHSILAT_SENET', 'BANKA_TAHSILAT', 'Senet', 'OTOMATIK', 4, 1);

-- BANKA_TEDIYE (4 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('BANKA_TEDIYE_EFT', 'BANKA_TEDIYE', 'EFT/Havale', 'OTOMATIK', 1, 1),
('BANKA_TEDIYE_KART', 'BANKA_TEDIYE', 'Kredi Kartı', 'OTOMATIK', 2, 1),
('BANKA_TEDIYE_CEK', 'BANKA_TEDIYE', 'Çek', 'OTOMATIK', 3, 1),
('BANKA_TEDIYE_SENET', 'BANKA_TEDIYE', 'Senet', 'OTOMATIK', 4, 1);

-- DEKONT (3 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('DEKONT_FAIZ_GELIR', 'DEKONT', 'Faiz Geliri', 'OTOMATIK', 1, 1),
('DEKONT_KOMISYON', 'DEKONT', 'Komisyon', 'OTOMATIK', 2, 1),
('DEKONT_DIGER', 'DEKONT', 'Diğer', 'OTOMATIK', 3, 1);

-- BANKA_VIRMAN (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('VIRMAN_HESAPLAR_ARASI', 'BANKA_VIRMAN', 'Hesaplar Arası Virman', 'OTOMATIK', 1, 1);

-- CEK_SENET kategorisi (6 ana tür)
-- ALINAN_CEK (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('ALINAN_CEK_CIRO', 'ALINAN_CEK', 'Ciro', 'MANUEL', 1, 1),
('ALINAN_CEK_PORTFOY', 'ALINAN_CEK', 'Portföy', 'MANUEL', 2, 1);

-- VERILEN_CEK (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('VERILEN_CEK_NORMAL', 'VERILEN_CEK', 'Normal Çek', 'MANUEL', 1, 1);

-- CEK_TAHSILAT_ODEME (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('CEK_TAHSILAT', 'CEK_TAHSILAT_ODEME', 'Çek Tahsil', 'MANUEL', 1, 1),
('CEK_ODEME', 'CEK_TAHSILAT_ODEME', 'Çek Ödeme', 'MANUEL', 2, 1);

-- ALINAN_SENET (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('ALINAN_SENET_CIRO', 'ALINAN_SENET', 'Ciro', 'MANUEL', 1, 1),
('ALINAN_SENET_PORTFOY', 'ALINAN_SENET', 'Portföy', 'MANUEL', 2, 1);

-- VERILEN_SENET (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('VERILEN_SENET_NORMAL', 'VERILEN_SENET', 'Normal Senet', 'MANUEL', 1, 1);

-- SENET_TAHSILAT_ODEME (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('SENET_TAHSILAT', 'SENET_TAHSILAT_ODEME', 'Senet Tahsil', 'MANUEL', 1, 1),
('SENET_ODEME', 'SENET_TAHSILAT_ODEME', 'Senet Ödeme', 'MANUEL', 2, 1);

-- PERSONEL kategorisi (2 ana tür)
-- MAAS_BORDROSU (3 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('BORDRO_AYLIK', 'MAAS_BORDROSU', 'Aylık Bordro', 'OTOMATIK', 1, 1),
('BORDRO_HAFTALIK', 'MAAS_BORDROSU', 'Haftalık Bordro', 'OTOMATIK', 2, 1),
('BORDRO_GUNLUK', 'MAAS_BORDROSU', 'Günlük Bordro', 'OTOMATIK', 3, 1);

-- SGK_BILDIRGESI (4 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('SGK_NORMAL', 'SGK_BILDIRGESI', 'Normal SGK', 'OTOMATIK', 1, 1),
('SGK_EKLEME', 'SGK_BILDIRGESI', 'Ekleme Bildirge', 'OTOMATIK', 2, 1),
('SGK_DUZELTME', 'SGK_BILDIRGESI', 'Düzeltme Bildirge', 'OTOMATIK', 3, 1),
('SGK_IPTAL', 'SGK_BILDIRGESI', 'İptal Bildirge', 'OTOMATIK', 4, 1);

-- GIDER kategorisi (3 ana tür)
-- GIDER_PUSULASI (5 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('GIDER_YEMEK', 'GIDER_PUSULASI', 'Yemek Gideri', 'MANUEL', 1, 1),
('GIDER_YAKIT', 'GIDER_PUSULASI', 'Yakıt Gideri', 'MANUEL', 2, 1),
('GIDER_KIRTASIYE', 'GIDER_PUSULASI', 'Kırtasiye', 'MANUEL', 3, 1),
('GIDER_ULASIM', 'GIDER_PUSULASI', 'Ulaşım', 'MANUEL', 4, 1),
('GIDER_DIGER', 'GIDER_PUSULASI', 'Diğer Giderler', 'MANUEL', 5, 1);

-- SERBEST_MESLEK_MAKBUZU (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('SMM_NORMAL', 'SERBEST_MESLEK_MAKBUZU', 'Normal SMM', 'MANUEL', 1, 1),
('SMM_TEVKIFATLI', 'SERBEST_MESLEK_MAKBUZU', 'Tevkifatlı SMM', 'MANUEL', 2, 1);

-- MUSTAHSIL_MAKBUZU (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('MUSTAHSIL_NORMAL', 'MUSTAHSIL_MAKBUZU', 'Normal Müstahsil', 'MANUEL', 1, 1);

-- VERGI kategorisi (2 ana tür)
-- VERGI_BEYANNAMESI (8 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('BEYAN_KDV', 'VERGI_BEYANNAMESI', 'KDV Beyannamesi', 'OTOMATIK', 1, 1),
('BEYAN_STOPAJ', 'VERGI_BEYANNAMESI', 'Stopaj Beyannamesi', 'OTOMATIK', 2, 1),
('BEYAN_GELIR', 'VERGI_BEYANNAMESI', 'Gelir Vergisi', 'OTOMATIK', 3, 1),
('BEYAN_KURUMLAR', 'VERGI_BEYANNAMESI', 'Kurumlar Vergisi', 'OTOMATIK', 4, 1),
('BEYAN_GECICI', 'VERGI_BEYANNAMESI', 'Geçici Vergi', 'OTOMATIK', 5, 1),
('BEYAN_DAMGA', 'VERGI_BEYANNAMESI', 'Damga Vergisi', 'OTOMATIK', 6, 1),
('BEYAN_MTV', 'VERGI_BEYANNAMESI', 'MTV', 'OTOMATIK', 7, 1),
('BEYAN_DIGER', 'VERGI_BEYANNAMESI', 'Diğer Vergiler', 'OTOMATIK', 8, 1);

-- VERGI_ODEME (4 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('VERGI_ODEME_KDV', 'VERGI_ODEME', 'KDV Ödemesi', 'MANUEL', 1, 1),
('VERGI_ODEME_STOPAJ', 'VERGI_ODEME', 'Stopaj Ödemesi', 'MANUEL', 2, 1),
('VERGI_ODEME_DIGER', 'VERGI_ODEME', 'Diğer Vergi Ödemesi', 'MANUEL', 3, 1),
('VERGI_ODEME_TAHAKKUK', 'VERGI_ODEME', 'Vergi Tahakkuku', 'MANUEL', 4, 1);

-- MUHASEBE kategorisi (6 ana tür)
-- MAHSUP (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('MAHSUP_CARI', 'MAHSUP', 'Cari Mahsup', 'MANUEL', 1, 1),
('MAHSUP_HESAP', 'MAHSUP', 'Hesap Mahsup', 'MANUEL', 2, 1);

-- YEVMIYE (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('YEVMIYE_GENEL', 'YEVMIYE', 'Genel Yevmiye', 'MANUEL', 1, 1);

-- ACILIS (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('ACILIS_DONEM', 'ACILIS', 'Dönem Açılış', 'MANUEL', 1, 1);

-- KAPANIS_FISI (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('KAPANIS_DONEM', 'KAPANIS_FISI', 'Dönem Kapanış', 'MANUEL', 1, 1),
('KAPANIS_YILSONU', 'KAPANIS_FISI', 'Yılsonu Kapanış', 'MANUEL', 2, 1);

-- DUZELTME (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('DUZELTME_HATA', 'DUZELTME', 'Hata Düzeltme', 'MANUEL', 1, 1),
('DUZELTME_TAHAKKUK', 'DUZELTME', 'Tahakkuk Düzeltme', 'MANUEL', 2, 1);

-- TERS_KAYIT (1 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('TERS_KAYIT_IPTAL', 'TERS_KAYIT', 'İptal (Ters Kayıt)', 'MANUEL', 1, 1);

-- STOK kategorisi (4 ana tür)
-- STOK_GIRIS (3 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('STOK_GIRIS_ALIS', 'STOK_GIRIS', 'Alıştan Giriş', 'OTOMATIK', 1, 1),
('STOK_GIRIS_IADE', 'STOK_GIRIS', 'İadeden Giriş', 'OTOMATIK', 2, 1),
('STOK_GIRIS_FIRE', 'STOK_GIRIS', 'Fire/Fazla', 'MANUEL', 3, 1);

-- STOK_CIKIS (3 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('STOK_CIKIS_SATIS', 'STOK_CIKIS', 'Satıştan Çıkış', 'OTOMATIK', 1, 1),
('STOK_CIKIS_IADE', 'STOK_CIKIS', 'İadeden Çıkış', 'OTOMATIK', 2, 1),
('STOK_CIKIS_FIRE', 'STOK_CIKIS', 'Fire/Kayıp', 'MANUEL', 3, 1);

-- SAYIM_FISI (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('SAYIM_YILSONU', 'SAYIM_FISI', 'Yılsonu Sayım', 'MANUEL', 1, 1),
('SAYIM_ARA', 'SAYIM_FISI', 'Ara Sayım', 'MANUEL', 2, 1);

-- AMORTISMAN_FISI (2 alt tür)
INSERT IGNORE INTO document_subtypes (code, parent_code, name, category, sort_order, is_active) VALUES
('AMORTISMAN_AYLIK', 'AMORTISMAN_FISI', 'Aylık Amortisman', 'OTOMATIK', 1, 1),
('AMORTISMAN_YILSONU', 'AMORTISMAN_FISI', 'Yılsonu Amortisman', 'OTOMATIK', 2, 1);

-- ===================================================================
-- Doğrulama Sorguları
-- ===================================================================
SELECT '✅ Migration Tamamlandı!' AS Durum;

SELECT 
    dt.code AS ana_evrak,
    dt.name AS ana_evrak_adi,
    COUNT(ds.id) AS alt_turu_sayisi
FROM document_types dt
LEFT JOIN document_subtypes ds ON ds.parent_code = dt.code
GROUP BY dt.code, dt.name
ORDER BY dt.category, dt.code;

SELECT 
    category,
    COUNT(*) AS toplam
FROM document_subtypes
GROUP BY category
ORDER BY category;
