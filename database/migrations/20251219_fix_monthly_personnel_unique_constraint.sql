-- =====================================================
-- LUCA PERSONEL SİCİL - Unique Constraint Düzeltme
-- Tarih: 2025-12-19
-- Açıklama: Aynı personel aynı dönemde birden fazla giriş-çıkış yapabilir
--           Unique constraint'e ise_giris_tarihi ekleniyor
-- =====================================================

-- Eski constraint'i kaldır
ALTER TABLE `monthly_personnel_records` 
DROP INDEX `uq_personnel_donem_bolum`;

-- Yeni constraint ekle (giriş tarihi de dahil)
ALTER TABLE `monthly_personnel_records`
ADD UNIQUE KEY `uq_personnel_donem_bolum_giris` (`personnel_id`, `donem`, `bolum_adi`, `ise_giris_tarihi`);

-- Not: Aynı personel, aynı dönem, aynı bölüm - ama farklı giriş tarihleriyle çalışabilir
-- Örnek: ERDAL KOT - 2025-06'da 2 kez:
--   1) 2025-06-11 giriş, 2025-06-16 çıkış
--   2) 2025-06-25 giriş, 2025-07-31 çıkış
