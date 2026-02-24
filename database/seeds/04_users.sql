-- Seed data for users
-- Generated: 2026-01-30
-- Rows: 3

SET FOREIGN_KEY_CHECKS=0;

TRUNCATE TABLE `users`;

INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `full_name`, `role`, `is_active`, `created_at`, `last_login`) VALUES (1, 'admin', 'admin@muhasebe.local', '$argon2id$v=19$m=65536,t=3,p=4$nHMOgfC+l3Ku9d5bi7GWUg$kJVuVuoMPZjVDtdzvJmk/+jPdwOn2cEi+xEJKLanJW4', 'Sistem Yöneticisi', 'admin', 1, '2025-12-14 05:35:18', NULL);
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `full_name`, `role`, `is_active`, `created_at`, `last_login`) VALUES (2, 'cagatay', 'cagatay.dinler@yimak.com.tr', '$argon2id$v=19$m=65536,t=3,p=4$A4AwpnSu1XpPCSGkdI7xXg$cizlfbA+Pq+m7ONBYF5q8jUzDVJRCo0hwV+VlUuXHMk', 'Çağatay Dinler', 'muhasebeci', 1, '2026-01-06 22:53:53', NULL);
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `full_name`, `role`, `is_active`, `created_at`, `last_login`) VALUES (3, 'Vural Garptaş', 'vural.garptas@yimak.com.tr', '$argon2id$v=19$m=65536,t=3,p=4$nxMCYGwNgbBWaq2VsjYGYA$CC7b4z7sVl/XWZGA8rdTm9FUtsGR28Co7Pu/46DwcF4', 'Vural Garptaş', 'muhasebeci', 1, '2026-01-06 22:55:32', NULL);

SET FOREIGN_KEY_CHECKS=1;
