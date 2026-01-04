"""Admin şifresini sıfırla - argon2 hash ile"""
from passlib.context import CryptContext
from app.core.database import SessionLocal
from sqlalchemy import text

# Argon2 ile hash oluştur
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
new_password = "admin123"
hashed_password = pwd_context.hash(new_password)

print("=" * 60)
print("ADMİN ŞİFRE SIFIRLAMA")
print("=" * 60)
print(f"Yeni Şifre: {new_password}")
print(f"Hash (ilk 50 karakter): {hashed_password[:50]}...")
print("=" * 60)

# Database'e kaydet
db = SessionLocal()
try:
    result = db.execute(
        text("UPDATE users SET hashed_password = :hash WHERE username = 'admin'"),
        {"hash": hashed_password}
    )
    db.commit()
    
    if result.rowcount > 0:
        print("✅ Şifre başarıyla güncellendi!")
        
        # Kontrol et
        check = db.execute(
            text("SELECT username, email, is_active FROM users WHERE username = 'admin'")
        ).fetchone()
        print(f"\n📋 Kullanıcı Bilgileri:")
        print(f"   Username: {check[0]}")
        print(f"   Email: {check[1]}")
        print(f"   Active: {check[2]}")
    else:
        print("❌ Admin kullanıcısı bulunamadı!")
        
except Exception as e:
    print(f"❌ HATA: {e}")
    db.rollback()
finally:
    db.close()

print("=" * 60)
print("Backend'i yeniden başlatın ve admin/admin123 ile giriş yapın")
print("=" * 60)
