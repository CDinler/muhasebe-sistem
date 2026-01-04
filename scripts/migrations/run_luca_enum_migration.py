"""
Luca ENUM kodlarını güncelle
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
    """Migration çalıştır"""
    print("="*80)
    print("LUCA ENUM KODLARI GÜNCELLENİYOR")
    print("="*80)
    
    try:
        # MySQL bağlantısı
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Migration dosyasını oku
        with open('../database/migrations/20251222_update_luca_enum_codes.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # SQL komutlarını ayır ve çalıştır
        commands = sql_content.split(';')
        
        for i, command in enumerate(commands, 1):
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    print(f"\n[{i}] Çalıştırılıyor...")
                    cursor.execute(command)
                    
                    # SELECT sonuçlarını göster
                    if command.upper().startswith('SELECT'):
                        results = cursor.fetchall()
                        for row in results:
                            print(f"    {row}")
                    
                    connection.commit()
                    print(f"    ✓ Başarılı")
                    
                except Exception as e:
                    print(f"    ✗ Hata: {e}")
                    connection.rollback()
        
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
