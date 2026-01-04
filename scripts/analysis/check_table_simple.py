"""
Basit tablo kontrolü - pymysql ile
"""
import pymysql

def check_table():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='muhasebe_sistem',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # Tablo var mı?
        cursor.execute("""
            SELECT TABLE_NAME, TABLE_ROWS, CREATE_TIME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'muhasebe_sistem'
              AND TABLE_NAME = 'monthly_personnel_records'
        """)
        
        result = cursor.fetchone()
        
        if result:
            print("✅ TABLO MEVCUT!")
            print(f"   Tablo: {result[0]}")
            print(f"   Satır sayısı: {result[1]}")
            print(f"   Oluşturulma: {result[2]}")
            
            # Kolonları göster
            cursor.execute("""
                SELECT COLUMN_NAME, COLUMN_TYPE
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'muhasebe_sistem'
                  AND TABLE_NAME = 'monthly_personnel_records'
                ORDER BY ORDINAL_POSITION
            """)
            
            print("\n📋 KOLONLAR:")
            for row in cursor:
                print(f"   - {row[0]}: {row[1]}")
            
            conn.close()
            return True
        else:
            print("❌ TABLO YOK!")
            print("\n🔧 SQL ÇALIŞTIRMANIZ GEREKİYOR:")
            print("   http://localhost/phpmyadmin → muhasebe → SQL")
            print("   Dosya: database/migrations/20251218_add_monthly_personnel_records.sql")
            conn.close()
            return False
            
    except pymysql.Error as e:
        print(f"❌ BAĞLANTI HATASI: {e}")
        print("\nXAMPP MySQL çalışıyor mu kontrol edin!")
        return False

if __name__ == "__main__":
    check_table()
