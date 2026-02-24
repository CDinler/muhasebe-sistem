# -*- coding: utf-8 -*-
"""
Admin kullanıcısı için şifre hash'i oluştur
Kullanım: python create_admin_hash.py
"""
from app.core.security import get_password_hash

# Admin şifresi
password = "admin123"
hashed = get_password_hash(password)

print("=" * 60)
print("Admin Kullanıcı Bilgileri")
print("=" * 60)
print(f"Kullanıcı Adı: admin")
print(f"Şifre: {password}")
print(f"Hash: {hashed}")
print("=" * 60)
print("\nSQL Komutu:")
print("=" * 60)

sql = f"""
-- Admin kullanıcısı oluştur
-- Şifre: {password}

-- Önce mevcut admin kullanıcısını sil (varsa)
DELETE FROM users WHERE username = 'admin';

-- Yeni admin kullanıcısı ekle
INSERT INTO users (username, email, hashed_password, full_name, role, is_active) 
VALUES ('admin', 'admin@muhasebe.local', '{hashed}', 'Admin User', 'admin', 1);

SELECT * FROM users WHERE username = 'admin';
"""

print(sql)
print("=" * 60)
