"""
Hesap kodlarını 191.01.001 → 191.01001 formatına güncelle
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Eski → Yeni hesap kodu mapping
account_updates = {
    '191.01.001': '191.01001',
    '191.01.002': '191.01002',
    '191.08.001': '191.08001',
    '191.08.002': '191.08002',
    '191.10.001': '191.10001',
    '191.10.002': '191.10002',
    '191.18.001': '191.18001',
    '191.18.002': '191.18002',
    '191.20.001': '191.20001',
    '191.20.002': '191.20002',
}

with engine.connect() as conn:
    print("📊 Hesap kodlarını güncelliyorum...\n")
    
    for old_code, new_code in account_updates.items():
        # Hesap var mı kontrol et
        result = conn.execute(
            text("SELECT code, name FROM accounts WHERE code = :old_code"),
            {"old_code": old_code}
        ).fetchone()
        
        if result:
            # Hesap kodunu güncelle
            conn.execute(
                text("UPDATE accounts SET code = :new_code WHERE code = :old_code"),
                {"old_code": old_code, "new_code": new_code}
            )
            print(f"✅ {old_code} → {new_code} ({result[1]})")
        else:
            print(f"⚠️  {old_code} bulunamadı")
    
    conn.commit()
    print("\n✨ Güncelleme tamamlandı!")
    
    # Kontrol
    print("\n📋 Güncellenmiş hesaplar:")
    result = conn.execute(
        text("SELECT code, name FROM accounts WHERE code LIKE '191.%' ORDER BY code")
    )
    for row in result:
        print(f"   {row[0]} - {row[1]}")
