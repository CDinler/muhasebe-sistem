"""Şifre doğrulamasını test et"""
from passlib.context import CryptContext
from app.core.database import SessionLocal
from sqlalchemy import text

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

db = SessionLocal()
try:
    # Admin user'ı al
    result = db.execute(
        text("SELECT username, hashed_password FROM users WHERE username = 'admin'")
    ).fetchone()
    
    if not result:
        print("❌ Admin kullanıcısı bulunamadı!")
    else:
        username = result[0]
        hashed_password = result[1]
        
        print("=" * 60)
        print("ŞİFRE DOĞRULAMA TESTİ")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Hash (ilk 50 karakter): {hashed_password[:50]}...")
        print(f"Hash başlangıcı: {hashed_password[:10]}")
        print("=" * 60)
        
        # Test şifresi
        test_password = "admin123"
        
        # Şifreyi doğrula
        try:
            is_valid = pwd_context.verify(test_password, hashed_password)
            
            if is_valid:
                print(f"✅ Şifre DOĞRU! '{test_password}' hash ile eşleşiyor")
            else:
                print(f"❌ Şifre YANLIŞ! '{test_password}' hash ile eşleşmiyor")
                
                # Yeni hash oluştur ve karşılaştır
                print("\n🔄 Yeni hash oluşturuluyor...")
                new_hash = pwd_context.hash(test_password)
                print(f"Yeni hash (ilk 50 karakter): {new_hash[:50]}...")
                print(f"Yeni hash başlangıcı: {new_hash[:10]}")
                
                # Database hash'i ile karşılaştır
                print(f"\nDatabase hash başlangıcı: {hashed_password[:10]}")
                print(f"Yeni hash başlangıcı:      {new_hash[:10]}")
                
                if hashed_password.startswith("$argon2"):
                    print("✅ Database hash'i argon2 formatında")
                else:
                    print("❌ Database hash'i argon2 formatında DEĞİL!")
                    print(f"   Hash başlangıcı: {hashed_password[:20]}")
                
        except Exception as e:
            print(f"❌ Doğrulama hatası: {e}")
            
        print("=" * 60)
        
finally:
    db.close()
