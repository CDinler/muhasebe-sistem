"""
Database migration'ını çalıştırmak için yardımcı script.
MySQL komutu olmadığında bu script ile migration çalıştırılabilir.
"""

import mysql.connector
from pathlib import Path

# Database bağlantı bilgileri
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'muhasebe_db'
}

MIGRATION_FILE = Path(__file__).parent.parent / 'database' / 'migrations' / '20251226_add_einvoice_pdf_support.sql'

def run_migration():
    """Migration SQL dosyasını çalıştır."""
    
    print("=" * 80)
    print("E-FATURA PDF DESTEK MIGRATION")
    print("=" * 80)
    
    # SQL dosyasını oku
    print(f"\n📄 Migration dosyası okunuyor: {MIGRATION_FILE}")
    
    if not MIGRATION_FILE.exists():
        print(f"❌ Dosya bulunamadı: {MIGRATION_FILE}")
        return False
    
    with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"✅ {len(sql_content)} karakter SQL kodu okundu")
    
    # SQL komutlarını ayır (-- yorumları ve boş satırları atla)
    sql_commands = []
    for line in sql_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            sql_commands.append(line)
    
    sql_script = ' '.join(sql_commands)
    
    # Her statement'ı ayır
    statements = []
    current = []
    for part in sql_script.split(';'):
        part = part.strip()
        if part:
            statements.append(part + ';')
    
    print(f"📋 {len(statements)} SQL statement bulundu\n")
    
    # Database'e bağlan
    print("🔌 Database'e bağlanılıyor...")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"✅ Bağlantı başarılı: {DB_CONFIG['database']}\n")
        
        # Her statement'ı çalıştır
        for i, statement in enumerate(statements, 1):
            if not statement.strip():
                continue
                
            print(f"▶ Statement {i}/{len(statements)}:")
            print(f"  {statement[:80]}{'...' if len(statement) > 80 else ''}")
            
            try:
                cursor.execute(statement)
                conn.commit()
                print(f"  ✅ Başarılı")
            except mysql.connector.Error as e:
                if 'Duplicate column name' in str(e):
                    print(f"  ⚠️  Kolon zaten mevcut (atlandı)")
                elif 'Duplicate key name' in str(e):
                    print(f"  ⚠️  Index zaten mevcut (atlandı)")
                else:
                    print(f"  ❌ Hata: {e}")
                    raise
            
            print()
        
        # Sonuçları kontrol et
        print("=" * 80)
        print("KONTROL: Kolonlar eklendi mi?")
        print("=" * 80)
        
        cursor.execute("SHOW COLUMNS FROM einvoices LIKE 'pdf_path'")
        pdf_path_col = cursor.fetchone()
        
        cursor.execute("SHOW COLUMNS FROM einvoices LIKE 'has_xml'")
        has_xml_col = cursor.fetchone()
        
        cursor.execute("SHOW COLUMNS FROM einvoices LIKE 'source'")
        source_col = cursor.fetchone()
        
        if pdf_path_col:
            print("✅ pdf_path kolonu mevcut")
        else:
            print("❌ pdf_path kolonu BULUNAMADI!")
        
        if has_xml_col:
            print("✅ has_xml kolonu mevcut")
        else:
            print("❌ has_xml kolonu BULUNAMADI!")
        
        if source_col:
            print("✅ source kolonu mevcut")
        else:
            print("❌ source kolonu BULUNAMADI!")
        
        # Index kontrolü
        cursor.execute("SHOW INDEX FROM einvoices WHERE Key_name = 'idx_einvoices_pdf_path'")
        pdf_idx = cursor.fetchone()
        
        cursor.execute("SHOW INDEX FROM einvoices WHERE Key_name = 'idx_einvoices_has_xml'")
        has_xml_idx = cursor.fetchone()
        
        if pdf_idx:
            print("✅ idx_einvoices_pdf_path index mevcut")
        else:
            print("❌ idx_einvoices_pdf_path index BULUNAMADI!")
        
        if has_xml_idx:
            print("✅ idx_einvoices_has_xml index mevcut")
        else:
            print("❌ idx_einvoices_has_xml index BULUNAMADI!")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION BAŞARIYLA TAMAMLANDI!")
        print("=" * 80)
        
        cursor.close()
        conn.close()
        
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database hatası: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    
    if success:
        print("\n🎉 PDF desteği başarıyla eklendi!")
        print("\nArtık şunları yapabilirsiniz:")
        print("  1. E-arşiv PDF'leri yükleyin (frontend: PDF Yükle butonu)")
        print("  2. Mevcut faturalara PDF ekleyin")
        print("  3. PDF'leri görüntüleyin (tabloda yeşil PDF ikonu)")
    else:
        print("\n❌ Migration başarısız oldu. Lütfen hataları kontrol edin.")
