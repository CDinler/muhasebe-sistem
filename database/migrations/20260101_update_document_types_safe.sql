-- ========================================================================================================
-- EVRAK TÜRÜ SİSTEMİ GÜNCELLEMESİ - Mevcut Kayıtları Koruyarak
-- Oluşturma Tarihi: 2026-01-01
-- Amaç: YEVMIYE_KAYDI_SABLONU.md'ye uygun evrak türü yapısını eklemek
-- NOT: Transactions tablosu mevcut document_subtype_id'leri kullanıyor, bu yüzden mevcut kayıtlar KORUNUYOR
-- ========================================================================================================

-- 1. Yalnızca document_type_mapping'i temizle (transactions'a bağlı değil)
DELETE FROM document_type_mapping;

-- 2. Mevcut document_types'ı GÜNCELLE (name ve category'yi YEVMIYE_KAYDI_SABLONU.md'ye göre)
-- Mevcut 26 evrak türünün bazılarını güncelliyoruz

UPDATE document_types SET name = 'Alış Faturası', category = 'FATURA' WHERE code = 'ALIS_FATURA';
UPDATE document_types SET name = 'Satış Faturası', category = 'FATURA' WHERE code = 'SATIS_FATURA';
UPDATE document_types SET name = 'İade Faturası', category = 'FATURA' WHERE code = 'IADE_FATURA';
UPDATE document_types SET name = 'Proforma Fatura', category = 'FATURA' WHERE code = 'PROFORMA_FATURA';

-- 3. Eksik FATURA türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('HAKEDIS_FATURASI', 'Hakediş Faturası', 'FATURA', 40);

-- 4. KASA/BANKA türlerini GÜNCELLE
UPDATE document_types SET name = 'Banka Tahsilat Fişi', category = 'BANKA' WHERE code = 'BANKA_TAHSILAT';
UPDATE document_types SET name = 'Banka Tediye Fişi', category = 'BANKA' WHERE code = 'BANKA_TEDIYE';
UPDATE document_types SET name = 'Kasa Tahsilat Fişi', category = 'KASA' WHERE code = 'KASA_TAHSILAT';
UPDATE document_types SET name = 'Kasa Tediye Fişi', category = 'KASA' WHERE code = 'KASA_TEDIYE';

-- 5. Eksik KASA/BANKA türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('DEKONT', 'Dekont', 'BANKA', 140),
('VIRMAN', 'Virman Fişi', 'BANKA', 150);

-- 6. ÇEK/SENET türlerini GÜNCELLE
UPDATE document_types SET name = 'Alınan Çek', category = 'CEK_SENET' WHERE code = 'ALINAN_CEK';
UPDATE document_types SET name = 'Verilen Çek', category = 'CEK_SENET' WHERE code = 'VERILEN_CEK';
UPDATE document_types SET name = 'Alınan Senet', category = 'CEK_SENET' WHERE code = 'ALINAN_SENET';
UPDATE document_types SET name = 'Verilen Senet', category = 'CEK_SENET' WHERE code = 'VERILEN_SENET';
UPDATE document_types SET name = 'Çek Tahsilat/Ödeme', category = 'CEK_SENET' WHERE code = 'CEK_TAHSILAT_ODEME';

-- 7. Eksik ÇEK/SENET türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('SENET_TAHSILAT_ODEME', 'Senet Tahsilat/Ödeme', 'CEK_SENET', 250);

-- 8. PERSONEL türlerini GÜNCELLE
UPDATE document_types SET name = 'Maaş Bordrosu', category = 'PERSONEL' WHERE code = 'BORDRO';

-- 9. Eksik PERSONEL türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('MAAS_BORDROSU', 'Maaş Bordrosu', 'PERSONEL', 300),
('SGK_BILDIRGESI', 'SGK Bildirgesi', 'PERSONEL', 310);

-- 10. GİDER türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('GIDER_PUSULASI', 'Gider Pusulası', 'GIDER', 400),
('SERBEST_MESLEK_MAKBUZU', 'Serbest Meslek Makbuzu', 'GIDER', 410),
('MUSTAHSIL_MAKBUZU', 'Müstahsil Makbuzu', 'GIDER', 420);

-- 11. VERGİ türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('VERGI_BEYANNAMESI', 'Vergi Beyannamesi', 'VERGI', 500),
('VERGI_ODEME', 'Vergi Ödemesi', 'VERGI', 510);

-- 12. MUHASEBE türlerini GÜNCELLE
UPDATE document_types SET name = 'Yevmiye Fişi', category = 'MUHASEBE' WHERE code = 'YEVMIYE';
UPDATE document_types SET name = 'Açılış Fişi', category = 'MUHASEBE' WHERE code = 'ACILIS';
UPDATE document_types SET name = 'Mahsup Fişi', category = 'MUHASEBE' WHERE code = 'MAHSUP';
UPDATE document_types SET name = 'Düzeltici Fiş', category = 'MUHASEBE' WHERE code = 'DUZELTME';

-- 13. Eksik MUHASEBE türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('MAHSUP_FISI', 'Mahsup Fişi', 'MUHASEBE', 600),
('YEVMIYE_FISI', 'Yevmiye Fişi', 'MUHASEBE', 610),
('ACILIS_FISI', 'Açılış Fişi', 'MUHASEBE', 620),
('KAPANIS_FISI', 'Kapanış Fişi', 'MUHASEBE', 630),
('DUZELTICI_FIS', 'Düzeltici Fiş', 'MUHASEBE', 640),
('TERS_KAYIT', 'Ters Kayıt', 'MUHASEBE', 650);

-- 14. STOK türlerini EKLE
INSERT IGNORE INTO document_types (code, name, category, sort_order) VALUES
('STOK_GIRIS', 'Stok Giriş Fişi', 'STOK', 700),
('STOK_CIKIS', 'Stok Çıkış Fişi', 'STOK', 710),
('SAYIM_FISI', 'Sayım Fişi', 'STOK', 720),
('AMORTISMAN_FISI', 'Amortisman Fişi', 'STOK', 730);

-- ========================================================================================================
-- ÖZET
-- ========================================================================================================
-- ✅ Mevcut 26 document_types korundu ve güncellendi
-- ✅ Yeni evrak türleri eklendi (HAKEDIS_FATURASI, GİDER, VERGİ, STOK, vb.)
-- ✅ Transactions tablosundaki mevcut document_subtype_id'ler BİZALMADI
-- ⏳ document_subtypes için ayrı bir migration gerekecek (parent_code kolonu eklenecek)
-- ========================================================================================================
