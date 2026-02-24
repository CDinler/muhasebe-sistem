-- Seed data for tax_bracket
-- Generated: 2026-01-30
-- Rows: 5

SET FOREIGN_KEY_CHECKS=0;

TRUNCATE TABLE `tax_bracket`;

INSERT INTO `tax_bracket` (`id`, `min_amount`, `max_amount`, `tax_rate`, `year`, `is_active`, `created_at`) VALUES (1, '0.00', '70000.00', '0.1500', 2025, 1, '2025-12-18 00:13:36');
INSERT INTO `tax_bracket` (`id`, `min_amount`, `max_amount`, `tax_rate`, `year`, `is_active`, `created_at`) VALUES (2, '70000.00', '150000.00', '0.2000', 2025, 1, '2025-12-18 00:13:36');
INSERT INTO `tax_bracket` (`id`, `min_amount`, `max_amount`, `tax_rate`, `year`, `is_active`, `created_at`) VALUES (3, '150000.00', '550000.00', '0.2700', 2025, 1, '2025-12-18 00:13:36');
INSERT INTO `tax_bracket` (`id`, `min_amount`, `max_amount`, `tax_rate`, `year`, `is_active`, `created_at`) VALUES (4, '550000.00', '1900000.00', '0.3500', 2025, 1, '2025-12-18 00:13:36');
INSERT INTO `tax_bracket` (`id`, `min_amount`, `max_amount`, `tax_rate`, `year`, `is_active`, `created_at`) VALUES (5, '1900000.00', NULL, '0.4000', 2025, 1, '2025-12-18 00:13:36');

SET FOREIGN_KEY_CHECKS=1;
