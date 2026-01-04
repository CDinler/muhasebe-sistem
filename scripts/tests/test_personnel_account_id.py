"""
Test script: Personnel account_id kullanımını test et
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from app.core.config import settings

def test_personnel_account_relationship():
    """Personnel-Account ilişkisini test et"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("=" * 80)
    print("PERSONNEL-ACCOUNT İLİŞKİSİ TEST")
    print("=" * 80)
    
    # Test 1: account_id olan personeller
    print("\n1️⃣  account_id ile JOIN (YENİ YÖNTEM - HIZLI)")
    print("-" * 80)
    
    query1 = text("""
        SELECT 
            p.id as personnel_id,
            p.first_name,
            p.last_name,
            p.tckn,
            p.account_id,
            a.id as account_db_id,
            a.code as account_code,
            a.name as account_name
        FROM personnel p
        JOIN accounts a ON a.id = p.account_id
        WHERE p.is_active = 1
        LIMIT 5
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query1)
        rows = result.fetchall()
        
        if rows:
            for row in rows:
                print(f"   ✅ Personel ID: {row.personnel_id}")
                print(f"      Ad Soyad: {row.first_name} {row.last_name}")
                print(f"      TC: {row.tckn}")
                print(f"      account_id (FK): {row.account_id}")
                print(f"      Hesap ID: {row.account_db_id}")
                print(f"      Hesap Kodu: {row.account_code}")
                print(f"      Hesap Adı: {row.account_name}")
                print()
        else:
            print("   ⚠️  Aktif personel bulunamadı")
    
    # Test 2: Eski yöntem ile karşılaştırma (CONCAT kullanımı)
    print("\n2️⃣  CONCAT ile JOIN (ESKİ YÖNTEM - YAVAŞ)")
    print("-" * 80)
    
    query2 = text("""
        SELECT 
            p.id as personnel_id,
            p.first_name,
            p.last_name,
            p.tckn,
            a.id as account_id,
            a.code as account_code,
            CONCAT('335.', p.tckn) as expected_code
        FROM personnel p
        LEFT JOIN accounts a ON a.code = CONCAT('335.', p.tckn)
        WHERE p.is_active = 1
        LIMIT 5
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query2)
        rows = result.fetchall()
        
        if rows:
            for row in rows:
                match_status = "✅" if row.account_code == row.expected_code else "❌"
                print(f"   {match_status} Personel ID: {row.personnel_id} - {row.first_name} {row.last_name}")
                print(f"      Beklenen: {row.expected_code}")
                print(f"      Bulunan: {row.account_code}")
                print()
    
    # Test 3: Performance karşılaştırma
    print("\n3️⃣  PERFORMANCE KARŞILAŞTIRMA")
    print("-" * 80)
    
    # Yeni yöntem - EXPLAIN
    query3_new = text("""
        EXPLAIN SELECT 
            p.id, p.first_name, p.last_name,
            a.code, a.name
        FROM personnel p
        JOIN accounts a ON a.id = p.account_id
        WHERE p.is_active = 1
    """)
    
    print("   YENİ YÖNTEM (JOIN ON account_id):")
    with engine.connect() as conn:
        result = conn.execute(query3_new)
        for row in result:
            print(f"      {row}")
    
    # Eski yöntem - EXPLAIN
    query3_old = text("""
        EXPLAIN SELECT 
            p.id, p.first_name, p.last_name,
            a.code, a.name
        FROM personnel p
        LEFT JOIN accounts a ON a.code = CONCAT('335.', p.tckn)
        WHERE p.is_active = 1
    """)
    
    print("\n   ESKİ YÖNTEM (JOIN ON CONCAT):")
    with engine.connect() as conn:
        result = conn.execute(query3_old)
        for row in result:
            print(f"      {row}")
    
    # Test 4: account_id NULL olan personeller var mı?
    print("\n4️⃣  account_id NULL OLAN PERSONELLER")
    print("-" * 80)
    
    query4 = text("""
        SELECT COUNT(*) as count
        FROM personnel
        WHERE is_active = 1 AND account_id IS NULL
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query4)
        count = result.scalar()
        
        if count > 0:
            print(f"   ⚠️  account_id NULL olan {count} aktif personel var!")
            print(f"      Bu personeller için account_id'yi güncellemeniz gerekiyor.")
        else:
            print(f"   ✅ Tüm aktif personellerin account_id'si dolu")
    
    # Test 5: Foreign Key constraint kontrolü
    print("\n5️⃣  FOREIGN KEY CONSTRAINT KONTROLÜ")
    print("-" * 80)
    
    query5 = text("""
        SELECT 
            CONSTRAINT_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'personnel'
          AND COLUMN_NAME = 'account_id'
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query5)
        rows = result.fetchall()
        
        if rows:
            for row in rows:
                print(f"   ✅ Constraint: {row.CONSTRAINT_NAME}")
                print(f"      Referans Tablo: {row.REFERENCED_TABLE_NAME}")
                print(f"      Referans Kolon: {row.REFERENCED_COLUMN_NAME}")
        else:
            print("   ⚠️  Foreign key constraint bulunamadı!")
    
    print("\n" + "=" * 80)
    print("TEST TAMAMLANDI")
    print("=" * 80)


if __name__ == "__main__":
    test_personnel_account_relationship()
