"""
monthly_personnel_records tablosunu kontrol et
"""
from app.database import get_db
from sqlalchemy import text

def check_table():
    db = next(get_db())
    
    try:
        # Tablo var mı kontrol et
        result = db.execute(text("""
            SELECT TABLE_NAME, TABLE_ROWS, CREATE_TIME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'muhasebe'
              AND TABLE_NAME = 'monthly_personnel_records'
        """))
        
        table_info = result.fetchone()
        
        if table_info:
            print("✅ TABLO MEVCUT!")
            print(f"   Tablo: {table_info[0]}")
            print(f"   Satır sayısı: {table_info[1]}")
            print(f"   Oluşturulma: {table_info[2]}")
            
            # Kolonları göster
            result = db.execute(text("""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'muhasebe'
                  AND TABLE_NAME = 'monthly_personnel_records'
                ORDER BY ORDINAL_POSITION
            """))
            
            print("\n📋 KOLONLAR:")
            for col in result:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   - {col[0]}: {col[1]} ({nullable})")
            
            return True
        else:
            print("❌ TABLO YOK!")
            print("\nSQL'i çalıştırmanız gerekiyor:")
            print("1. http://localhost/phpmyadmin")
            print("2. muhasebe veritabanı → SQL sekmesi")
            print("3. database/migrations/20251218_add_monthly_personnel_records.sql dosyasını çalıştırın")
            return False
            
    except Exception as e:
        print(f"❌ HATA: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    check_table()
