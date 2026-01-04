"""
Takvimli puantaj migration'ını çalıştır
"""
import pymysql
import os

# Veritabanı bağlantısı (XAMPP default: şifresiz)
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # XAMPP default (şifresiz)
        database='muhasebe_sistem',
        charset='utf8mb4'
    )
except pymysql.err.OperationalError:
    # Şifre varsa
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='muhasebe_sistem',
        charset='utf8mb4'
    )

try:
    cursor = conn.cursor()
    
    # Migration dosyasını oku
    migration_file = os.path.join('..', 'database', 'migrations', '20251222_add_personnel_daily_attendance.sql')
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration dosyası bulunamadı: {migration_file}")
        exit(1)
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # SQL ifadelerini ayır ve çalıştır
    # DELIMITER'ı yönetmek için özel işlem gerekiyor
    statements = []
    current_statement = []
    delimiter = ';'
    in_delimiter_block = False
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Yorum satırlarını atla
        if line.startswith('--') or not line:
            continue
            
        # DELIMITER değişikliği
        if line.upper().startswith('DELIMITER'):
            parts = line.split()
            if len(parts) > 1:
                new_delimiter = parts[1]
                if new_delimiter == '//':
                    in_delimiter_block = True
                    delimiter = '//'
                elif new_delimiter == ';':
                    in_delimiter_block = False
                    delimiter = ';'
            continue
        
        current_statement.append(line)
        
        # İfade sonu kontrolü
        if line.endswith(delimiter):
            stmt = '\n'.join(current_statement)
            if delimiter == '//':
                stmt = stmt[:-2].strip()  # '//' kaldır
            else:
                stmt = stmt[:-1].strip()  # ';' kaldır
            
            if stmt and not stmt.upper().startswith('SELECT'):
                statements.append(stmt)
            current_statement = []
    
    # Her ifadeyi çalıştır
    for i, stmt in enumerate(statements, 1):
        try:
            print(f"{i}. İfade çalıştırılıyor...")
            cursor.execute(stmt)
            conn.commit()
            print(f"   ✓ Başarılı")
        except Exception as e:
            print(f"   ✗ Hata: {e}")
            # Tablo zaten varsa devam et
            if 'already exists' in str(e) or 'Duplicate' in str(e):
                print(f"   → Atlanıyor (zaten mevcut)")
                continue
    
    print("\n✅ Takvimli puantaj sistemi migration'ı tamamlandı!")
    
    # Oluşturulan tabloları kontrol et
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = 'muhasebe_sistem' 
        AND TABLE_NAME IN (
            'personnel_daily_attendance',
            'personnel_leave_balance',
            'shift_definitions',
            'calendar_holidays'
        )
        ORDER BY TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    print(f"\n📋 Oluşturulan tablolar ({len(tables)}):")
    for table in tables:
        print(f"   - {table[0]}")
    
    # View'leri kontrol et
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM information_schema.VIEWS 
        WHERE TABLE_SCHEMA = 'muhasebe_sistem' 
        AND TABLE_NAME LIKE 'v_%attendance%'
        ORDER BY TABLE_NAME
    """)
    
    views = cursor.fetchall()
    print(f"\n👁 Oluşturulan view'ler ({len(views)}):")
    for view in views:
        print(f"   - {view[0]}")

finally:
    cursor.close()
    conn.close()
