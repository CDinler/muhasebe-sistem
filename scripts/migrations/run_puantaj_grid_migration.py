"""
Puantaj Grid tablosunu oluştur
"""
import pymysql
import sys

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'muhasebe_sistem',
    'charset': 'utf8mb4'
}

def run_migration():
    print("="*80)
    print("PUANTAJ GRID TABLOSU OLUŞTURULUYOR")
    print("="*80)
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Migration dosyasını oku
        with open('../database/migrations/20251222_create_puantaj_grid_table.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # DELIMITER değiştirme işlemi için özel işlem
        # Trigger'ları ayrı çalıştır
        parts = sql_content.split('DELIMITER //')
        
        # İlk kısım (CREATE TABLE)
        main_sql = parts[0]
        cursor.execute(main_sql)
        connection.commit()
        print("✓ Tablo oluşturuldu")
        
        # Trigger'ları çalıştır
        if len(parts) > 1:
            trigger_part = parts[1].split('DELIMITER ;')[0]
            triggers = trigger_part.strip().split('//')
            
            for i, trigger_sql in enumerate(triggers, 1):
                trigger_sql = trigger_sql.strip()
                if trigger_sql and 'CREATE TRIGGER' in trigger_sql:
                    try:
                        cursor.execute(trigger_sql)
                        connection.commit()
                        print(f"✓ Trigger {i} oluşturuldu")
                    except Exception as e:
                        print(f"✗ Trigger {i} hatası: {e}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*80)
        print("✅ MIGRATION TAMAMLANDI")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
