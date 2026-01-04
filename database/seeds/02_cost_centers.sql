-- Maliyet Merkezleri (Şantiyeler) Seed Data

INSERT INTO cost_centers (code, name) VALUES
('GENEL', 'Genel Giderler'),
('OFIS', 'Ofis'),
('DEPO', 'Depo');

-- Kullanıcıdan gelen gerçek şantiyeler eklenecek

SELECT 'Maliyet merkezleri seed data yüklendi: ' || COUNT(*) || ' merkez' AS status FROM cost_centers;
