-- Seed data for tax_codes
-- Generated: 2026-01-30
-- Rows: 30

SET FOREIGN_KEY_CHECKS=0;

TRUNCATE TABLE `tax_codes`;

INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0003', 'Gelir Vergisi Stopajı', 'GV STOPAJI', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0011', 'Kurumlar Vergisi Stopajı', 'KV STOPAJI', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0015', 'Gerçek Usulde Katma Değer Vergisi', 'KDV GERCEK', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0021', 'Banka Muameleleri Vergisi', 'BMV', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0022', 'Sigorta Muameleleri Vergisi', 'SMV', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0059', 'Konaklama Vergisi', 'KONAKLAMA', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0061', 'Kaynak Kullanımı Destekleme Fonu Kesintisi', 'KKDF KESİNTİ', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0071', 'Petrol Ve Doğalgaz Ürünlerine İlişkin Özel Tüketim Vergisi', 'ÖTV 1.LİSTE', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0073', 'Kolalı Gazoz, Alkollü İçeçekler Ve Tütün Mamüllerine İlişkin Özel Tüketim Vergisi', 'ÖTV 3.LİSTE', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0074', 'Dayanıklı Tüketim Ve Diğer Mallara İlişkin Özel Tüketim Vergisi', 'ÖTV 4.LİSTE', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0075', 'Alkollü İçeçeklere İlişkin Özel Tüketim Vergisi', 'ÖTV 3A LİSTE', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0076', 'Tütün Mamüllerine İlişkin Özel Tüketim Vergisi', 'ÖTV 3B LİSTE', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('0077', 'Kolalı Gazozlara İlişkin Özel Tüketim Vergisi', 'ÖTV 3C LİSTE', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('1047', 'Damga Vergisi', 'DAMGA V', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('1048', '5035 Sayılı Kanuna Göre Damga Vergisi', '5035SKDAMGAV', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('4071', 'Elektrik Ve Havagazi Tüketim Vergisi', 'ELK.HAVAGAZ.TÜK.VER.', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('4080', 'Özel İletişim Vergisi', 'Ö.İLETİŞİM V', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('4081', '5035 Sayılı Kanuna Göre Özel İletişim Vergisi', '5035ÖZİLETV.', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('4171', 'Petrol Ve Doğalgaz Ürünlerine İlişkin Ötv Tevkifatı', 'PTR-DGZ ÖTV TEVKİFAT', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('8001', 'Borsa Tescil Ücreti', 'BORSA TES.ÜC.', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('8002', 'Enerji Fonu', 'ENERJİ FONU', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('8004', 'Trt Payı', 'TRT PAYI', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('8005', 'Elektrik Tüketim Vergisi', 'ELK.TÜK.VER.', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('8006', 'Telsiz Kullanım Ücreti', 'TK KULLANIM', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('8007', 'Telsiz Ruhsat Ücreti', 'TK RUHSAT', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('8008', 'Çevre Temizlik Vergisi', 'ÇEV. TEM .VER.', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('9021', '4961 Banka Sigorta Muameleleri Vergisi', '4961BANKASMV', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('9040', 'Mera Fonu', 'MERA FONU', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('9077', 'Motorlu Taşıt Araçlarına İlişkin Özel Tüketim Vergisi (Tescile Tabi Olanlar)', 'ÖTV 2.LİSTE', 0, NULL);
INSERT INTO `tax_codes` (`code`, `name`, `short_name`, `is_withholding`, `description`) VALUES ('9944', 'Belediyelere Ödenen Hal Rüsumu', 'BEL.ÖD.HAL RÜSUM', 0, NULL);

SET FOREIGN_KEY_CHECKS=1;
