-- =============================================================================================================
-- KAPSAMLI EVRAK TÜRÜ SİSTEMİ - YEVMIYE_KAYDI_SABLONU.md'ye Göre
-- Oluşturma Tarihi: 2026-01-01 (Güncellenmiş)
-- Türkçe karakter desteği: utf8mb4_turkish_ci collation
-- =============================================================================================================

-- 1. FOREIGN KEY CONSTRAINT'LERİ GEÇİCİ DEVRE DIŞI BIRAK
-- ============================================================================
SET FOREIGN_KEY_CHECKS = 0;

-- 2. MEVCUT KAYITLARI GÜNCELLEnlerden transactions foreign key nedeniyle silme yapılamıyor.
-- Geçici olarak transactions.document_subtype_id'leri NULL'a set edip temizlik yapacağız.
-- =====================================================================================
UPDATE transactions SET document_subtype_id = NULL WHERE document_subtype_id IS NOT NULL;
UPDATE transactions SET document_type_id = NULL WHERE document_type_id IS NOT NULL;
DELETE FROM document_type_mapping;
DELETE FROM document_subtypes;
DELETE FROM document_types;

-- 3. ANA EVRAK TÜRLERİ
-- ============================================================================
INSERT INTO document_types (code, name, category, sort_order) VALUES
-- 🔷 FATURA (5 ana tür)
('ALIS_FATURASI', 'Alış Faturası', 'FATURA', 10),
('SATIS_FATURASI', 'Satış Faturası', 'FATURA', 20),
('IADE_FATURASI', 'İade Faturası', 'FATURA', 30),
('HAKEDIS_FATURASI', 'Hakediş Faturası', 'FATURA', 40),
('PROFORMA_FATURA', 'Proforma Fatura', 'FATURA', 50),

-- 🔷 KASA/BANKA (6 ana tür)
('KASA_TAHSILAT', 'Kasa Tahsilat Fişi', 'KASA', 100),
('KASA_TEDIYE', 'Kasa Tediye Fişi', 'KASA', 110),
('BANKA_TAHSILAT', 'Banka Tahsilat Fişi', 'BANKA', 120),
('BANKA_TEDIYE', 'Banka Tediye Fişi', 'BANKA', 130),
('DEKONT', 'Dekont', 'BANKA', 140),
('VIRMAN', 'Virman Fişi', 'BANKA', 150),

-- 🔷 ÇEK/SENET (6 ana tür)
('ALINAN_CEK', 'Alınan Çek', 'CEK_SENET', 200),
('VERILEN_CEK', 'Verilen Çek', 'CEK_SENET', 210),
('CEK_TAHSILAT_ODEME', 'Çek Tahsilat/Ödeme', 'CEK_SENET', 220),
('ALINAN_SENET', 'Alınan Senet', 'CEK_SENET', 230),
('VERILEN_SENET', 'Verilen Senet', 'CEK_SENET', 240),
('SENET_TAHSILAT_ODEME', 'Senet Tahsilat/Ödeme', 'CEK_SENET', 250),

-- 🔷 PERSONEL (2 ana tür)
('MAAS_BORDROSU', 'Maaş Bordrosu', 'PERSONEL', 300),
('SGK_BILDIRGESI', 'SGK Bildirgesi', 'PERSONEL', 310),

-- 🔷 GİDER (3 ana tür)
('GIDER_PUSULASI', 'Gider Pusulası', 'GIDER', 400),
('SERBEST_MESLEK_MAKBUZU', 'Serbest Meslek Makbuzu', 'GIDER', 410),
('MUSTAHSIL_MAKBUZU', 'Müstahsil Makbuzu', 'GIDER', 420),

-- 🔷 VERGİ (2 ana tür)
('VERGI_BEYANNAMESI', 'Vergi Beyannamesi', 'VERGI', 500),
('VERGI_ODEME', 'Vergi Ödemesi', 'VERGI', 510),

-- 🔷 MUHASEBE (6 ana tür)
('MAHSUP_FISI', 'Mahsup Fişi', 'MUHASEBE', 600),
('YEVMIYE_FISI', 'Yevmiye Fişi', 'MUHASEBE', 610),
('ACILIS_FISI', 'Açılış Fişi', 'MUHASEBE', 620),
('KAPANIS_FISI', 'Kapanış Fişi', 'MUHASEBE', 630),
('DUZELTICI_FIS', 'Düzeltici Fiş', 'MUHASEBE', 640),
('TERS_KAYIT', 'Ters Kayıt', 'MUHASEBE', 650),

-- 🔷 STOK (4 ana tür - İsteğe bağlı)
('STOK_GIRIS', 'Stok Giriş Fişi', 'STOK', 700),
('STOK_CIKIS', 'Stok Çıkış Fişi', 'STOK', 710),
('SAYIM_FISI', 'Sayım Fişi', 'STOK', 720),
('AMORTISMAN_FISI', 'Amortisman Fişi', 'STOK', 730);

-- 4. ALT EVRAK TÜRLERİ (document_subtypes)
-- ============================================================================

-- 🔷 FATURA Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- ALIS_FATURASI
('ALIS_FATURASI', 'E_FATURA', 'E-Fatura', 'E-Fatura (işletmeden alış)', 10),
('ALIS_FATURASI', 'E_ARSIV', 'E-Arşiv', 'E-Arşiv (perakendeden alış)', 20),
('ALIS_FATURASI', 'KAGIT_MATBU', 'Kağıt/Matbu', 'Kağıt/Matbu fatura', 30),
('ALIS_FATURASI', 'ITHALAT', 'İthalat', 'İthalat faturası', 40),
-- SATIS_FATURASI
('SATIS_FATURASI', 'E_FATURA', 'E-Fatura', 'E-Fatura (işletmeye satış)', 50),
('SATIS_FATURASI', 'E_ARSIV', 'E-Arşiv', 'E-Arşiv (perakendeye satış)', 60),
('SATIS_FATURASI', 'KAGIT_MATBU', 'Kağıt/Matbu', 'Kağıt/Matbu fatura', 70),
('SATIS_FATURASI', 'IHRACAT', 'İhracat', 'İhracat faturası', 80),
-- IADE_FATURASI
('IADE_FATURASI', 'ALIS_IADE', 'Alış İade', 'Alış iade', 90),
('IADE_FATURASI', 'SATIS_IADE', 'Satış İade', 'Satış iade', 100),
-- HAKEDIS_FATURASI
('HAKEDIS_FATURASI', 'E_FATURA', 'E-Fatura', 'E-Fatura hakediş', 110),
('HAKEDIS_FATURASI', 'E_ARSIV', 'E-Arşiv', 'E-Arşiv hakediş', 120);

-- 🔷 KASA/BANKA Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- KASA_TAHSILAT
('KASA_TAHSILAT', 'NAKIT', 'Nakit', 'Nakit tahsilat', 200),
('KASA_TAHSILAT', 'CEK', 'Çek', 'Çek ile tahsilat', 210),
('KASA_TAHSILAT', 'SENET', 'Senet', 'Senet ile tahsilat', 220),
-- KASA_TEDIYE
('KASA_TEDIYE', 'NAKIT', 'Nakit', 'Nakit ödeme', 230),
('KASA_TEDIYE', 'CEK', 'Çek', 'Çek ile ödeme', 240),
('KASA_TEDIYE', 'SENET', 'Senet', 'Senet ile ödeme', 250),
-- BANKA_TAHSILAT
('BANKA_TAHSILAT', 'EFT_HAVALE', 'EFT/Havale', 'EFT/Havale geliri', 260),
('BANKA_TAHSILAT', 'POS', 'POS', 'Kredi kartı tahsilat', 270),
('BANKA_TAHSILAT', 'CEK', 'Çek', 'Çek tahsili', 280),
('BANKA_TAHSILAT', 'SENET', 'Senet', 'Senet tahsili', 290),
-- BANKA_TEDIYE
('BANKA_TEDIYE', 'EFT_HAVALE', 'EFT/Havale', 'EFT/Havale gideri', 300),
('BANKA_TEDIYE', 'KREDI_KARTI', 'Kredi Kartı', 'Kredi kartı ödemesi', 310),
('BANKA_TEDIYE', 'CEK', 'Çek', 'Çek ödemesi', 320),
('BANKA_TEDIYE', 'SENET', 'Senet', 'Senet ödemesi', 330),
-- DEKONT
('DEKONT', 'BANKA_DEKONT', 'Banka Dekontu', 'Banka dekontu', 340),
('DEKONT', 'POS_DEKONT', 'POS Dekontu', 'POS dekontu', 350),
('DEKONT', 'ATM_DEKONT', 'ATM Dekontu', 'ATM dekontu', 360),
-- VIRMAN
('VIRMAN', 'KASA_KASA', 'Kasa-Kasa', 'Kasalar arası', 370),
('VIRMAN', 'BANKA_BANKA', 'Banka-Banka', 'Bankalar arası', 380),
('VIRMAN', 'KASA_BANKA', 'Kasa-Banka', 'Kasa-Banka arası', 390);

-- 🔷 ÇEK/SENET Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- ALINAN_CEK
('ALINAN_CEK', 'MUSTERI_CEKI', 'Müşteri Çeki', 'Tahsilat amaçlı', 400),
('ALINAN_CEK', 'CIRO_CEKI', 'Ciro Çeki', 'Ciro edilmiş', 410),
('ALINAN_CEK', 'TEMINAT_CEKI', 'Teminat Çeki', 'Teminat amaçlı', 420),
-- VERILEN_CEK
('VERILEN_CEK', 'TEDARIKCI_CEKI', 'Tedarikçi Çeki', 'Ödeme amaçlı', 430),
('VERILEN_CEK', 'TEMINAT_CEKI', 'Teminat Çeki', 'Teminat amaçlı', 440),
-- CEK_TAHSILAT_ODEME
('CEK_TAHSILAT_ODEME', 'CEK_TAHSIL', 'Çek Tahsil', 'Çek tahsil edildi', 450),
('CEK_TAHSILAT_ODEME', 'CEK_ODEME', 'Çek Ödeme', 'Çek ödendi', 460),
('CEK_TAHSILAT_ODEME', 'CEK_IADE', 'Çek İade', 'Çek iade edildi', 470),
('CEK_TAHSILAT_ODEME', 'CEK_PROTESTO', 'Çek Protesto', 'Karşılıksız çek', 480),
-- ALINAN_SENET
('ALINAN_SENET', 'MUSTERI_SENEDI', 'Müşteri Senedi', 'Tahsilat amaçlı', 490),
-- VERILEN_SENET
('VERILEN_SENET', 'TEDARIKCI_SENEDI', 'Tedarikçi Senedi', 'Ödeme amaçlı', 500),
-- SENET_TAHSILAT_ODEME
('SENET_TAHSILAT_ODEME', 'SENET_TAHSIL', 'Senet Tahsil', 'Senet tahsil edildi', 510),
('SENET_TAHSILAT_ODEME', 'SENET_ODEME', 'Senet Ödeme', 'Senet ödendi', 520),
('SENET_TAHSILAT_ODEME', 'SENET_PROTESTO', 'Senet Protesto', 'Ödenmedi', 530);

-- 🔷 PERSONEL Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- MAAS_BORDROSU
('MAAS_BORDROSU', 'AYLIK_MAAS', 'Aylık Maaş', 'Normal maaş', 600),
('MAAS_BORDROSU', 'PRIM', 'Prim', 'Prim ödemesi', 610),
('MAAS_BORDROSU', 'IKRAMIYE', 'İkramiye', 'İkramiye/Bonus', 620),
('MAAS_BORDROSU', 'AGI', 'AGİ', 'Asgari geçim indirimi', 630),
('MAAS_BORDROSU', 'KIDEM_IHBAR', 'Kıdem/İhbar', 'Kıdem tazminatı', 640),
-- SGK_BILDIRGESI
('SGK_BILDIRGESI', 'AYLIK_BILDIRGE', 'Aylık Bildirge', 'SGK prim bildirimi', 650),
('SGK_BILDIRGESI', 'ISE_GIRIS_CIKIS', 'İşe Giriş/Çıkış', 'İşe giriş/çıkış bildirimi', 660);

-- 🔷 GİDER Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- SERBEST_MESLEK_MAKBUZU
('SERBEST_MESLEK_MAKBUZU', 'E_SMM', 'E-SMM', 'Elektronik SMM', 700),
('SERBEST_MESLEK_MAKBUZU', 'KAGIT', 'Kağıt', 'Kağıt SMM', 710),
-- MUSTAHSIL_MAKBUZU
('MUSTAHSIL_MAKBUZU', 'E_MUSTAHSIL', 'E-Müstahsil', 'Elektronik', 720),
('MUSTAHSIL_MAKBUZU', 'KAGIT', 'Kağıt', 'Kağıt', 730);

-- 🔷 VERGİ Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- VERGI_BEYANNAMESI
('VERGI_BEYANNAMESI', 'KDV_BEYANI', 'KDV Beyanı', 'KDV beyannamesi', 800),
('VERGI_BEYANNAMESI', 'MUHTASAR_BEYANI', 'Muhtasar Beyanı', 'Muhtasar beyanname', 810),
('VERGI_BEYANNAMESI', 'GECICI_VERGI', 'Geçici Vergi', 'Geçici vergi', 820),
('VERGI_BEYANNAMESI', 'YILLIK_GELIR', 'Yıllık Gelir', 'Yıllık gelir vergisi', 830),
('VERGI_BEYANNAMESI', 'STOPAJ_BEYANI', 'Stopaj Beyanı', 'Stopaj beyannamesi', 840),
-- VERGI_ODEME
('VERGI_ODEME', 'KDV_ODEME', 'KDV Ödeme', 'KDV ödemesi', 850),
('VERGI_ODEME', 'STOPAJ_ODEME', 'Stopaj Ödeme', 'Stopaj ödemesi', 860),
('VERGI_ODEME', 'GELIR_VERGISI_ODEME', 'Gelir Vergisi', 'Gelir vergisi ödemesi', 870),
('VERGI_ODEME', 'DAMGA_VERGISI', 'Damga Vergisi', 'Damga vergisi', 880);

-- 🔷 MUHASEBE Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- MAHSUP_FISI
('MAHSUP_FISI', 'CARI_MAHSUP', 'Cari Mahsup', 'Alacak-Borç mahsubu', 900),
('MAHSUP_FISI', 'CEK_SENET_MAHSUP', 'Çek/Senet Mahsup', 'Kıymetli evrak mahsubu', 910),
-- ACILIS_FISI
('ACILIS_FISI', 'DONEM_ACILIS', 'Dönem Açılış', 'Yıl/Dönem açılışı', 920),
('ACILIS_FISI', 'ISLETME_ACILIS', 'İşletme Açılış', 'Yeni işletme açılışı', 930),
-- KAPANIS_FISI
('KAPANIS_FISI', 'DONEM_KAPANIS', 'Dönem Kapanış', 'Yıl/Dönem kapanışı', 940);

-- 🔷 STOK Alt Türleri
INSERT INTO document_subtypes (parent_code, code, name, description, sort_order) VALUES
-- STOK_GIRIS
('STOK_GIRIS', 'SATIN_ALIM', 'Satın Alım', 'Satın alım girişi', 1000),
('STOK_GIRIS', 'SATIS_IADESI_GIRIS', 'Satış İadesi', 'Satış iadesi girişi', 1010),
('STOK_GIRIS', 'FIRE_GIRIS', 'Fire Girişi', 'Fire girişi', 1020),
-- STOK_CIKIS
('STOK_CIKIS', 'SATIS_CIKIS', 'Satış Çıkış', 'Satış çıkışı', 1030),
('STOK_CIKIS', 'ALIS_IADESI_CIKIS', 'Alış İadesi', 'Alış iadesi çıkışı', 1040),
('STOK_CIKIS', 'FIRE_CIKIS', 'Fire Çıkışı', 'Fire çıkışı', 1050);

-- 5. FOREIGN KEY CONSTRAINT'LERİ YENİDEN AKTİF ET
-- ============================================================================
SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================================================
-- ÖZET
-- =============================================================================================================
-- Ana Evrak Türü (document_types): 34 kayıt
--   • FATURA: 5
--   • KASA/BANKA: 6
--   • ÇEK/SENET: 6
--   • PERSONEL: 2
--   • GİDER: 3
--   • VERGİ: 2
--   • MUHASEBE: 6
--   • STOK: 4
--
-- Alt Evrak Türü (document_subtypes): 74 kayıt
--   • Fatura: 12
--   • Kasa/Banka: 19
--   • Çek/Senet: 14
--   • Personel: 7
--   • Gider: 4
--   • Vergi: 9
--   • Muhasebe: 5
--   • Stok: 6
-- =============================================================================================================
