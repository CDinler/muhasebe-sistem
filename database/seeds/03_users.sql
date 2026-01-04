-- Admin kullanıcı oluştur
-- Şifre: admin123 (production'da değiştirilmeli!)

-- NOT: Hashed password'u backend'den oluşturmalıyız
-- Şimdilik placeholder

INSERT INTO users (username, email, hashed_password, full_name, role) VALUES
('admin', 'admin@muhasebe.local', '$2b$12$placeholder', 'Admin User', 'muhasebeci');

SELECT 'Admin kullanıcı oluşturuldu' AS status;
