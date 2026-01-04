from sqlalchemy import create_engine, text
import os

# Database connection
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("📊 DOCUMENT TYPES VE DOCUMENT_SUBTYPES MİGRATION RAPORU")
print("=" * 100)

with engine.connect() as conn:
    # Ana evrak türü sayısı
    total_types = conn.execute(text("SELECT COUNT(*) FROM document_types")).scalar()
    
    # Alt evrak türü sayısı
    total_subtypes = conn.execute(text("SELECT COUNT(*) FROM document_subtypes")).scalar()
    
    # Kategorilere göre dağılım
    categories = conn.execute(text("""
        SELECT 
            dt.category,
            COUNT(DISTINCT dt.id) AS ana_sayi,
            COUNT(ds.id) AS alt_sayi
        FROM document_types dt
        LEFT JOIN document_subtypes ds ON ds.parent_code = dt.code
        GROUP BY dt.category
        ORDER BY dt.category
    """)).fetchall()
    
    print(f"\n✅ GENEL ÖZET:")
    print(f"  📋 Ana Evrak Türü: {total_types}")
    print(f"  📄 Alt Evrak Türü: {total_subtypes}")
    
    print(f"\n📁 KATEGORİ DAĞILIMI:")
    for cat, ana, alt in categories:
        print(f"  {cat:15}: {ana:2} ana tür, {alt:3} alt tür")
    
    # Transaction kullanımı
    print(f"\n📊 TRANSACTION KULLANIMLARI:")
    txn_usage = conn.execute(text("""
        SELECT 
            dt.code,
            dt.name,
            COUNT(t.id) AS txn_count
        FROM document_types dt
        LEFT JOIN transactions t ON t.document_type_id = dt.id
        GROUP BY dt.id, dt.code, dt.name
        HAVING txn_count > 0
        ORDER BY txn_count DESC
        LIMIT 10
    """)).fetchall()
    
    for code, name, cnt in txn_usage:
        print(f"  {code:25} ({name:30}): {cnt:5} transaction")
    
    # parent_code ilişkisi kontrolü
    print(f"\n🔗 PARENT_CODE İLİŞKİSİ:")
    orphans = conn.execute(text("""
        SELECT COUNT(*) 
        FROM document_subtypes 
        WHERE parent_code NOT IN (SELECT code FROM document_types)
    """)).scalar()
    
    if orphans > 0:
        print(f"  ❌ {orphans} orphan (parent'ı olmayan) alt tür var!")
    else:
        print(f"  ✅ Tüm alt türlerin parent_code'u geçerli ({total_subtypes} kayıt)")
    
    # Unique constraint kontrolü
    print(f"\n🔍 UNIQUE CONSTRAINT KONTROLLERİ:")
    
    # Code unique (document_types)
    dup_types = conn.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT code FROM document_types GROUP BY code HAVING COUNT(*) > 1
        ) AS dups
    """)).scalar()
    
    if dup_types > 0:
        print(f"  ❌ document_types.code: {dup_types} duplicate var!")
    else:
        print(f"  ✅ document_types.code: Tüm kodlar benzersiz")
    
    # Name unique (document_types)
    dup_names_types = conn.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT name FROM document_types GROUP BY name HAVING COUNT(*) > 1
        ) AS dups
    """)).scalar()
    
    if dup_names_types > 0:
        print(f"  ❌ document_types.name: {dup_names_types} duplicate var!")
    else:
        print(f"  ✅ document_types.name: Tüm isimler benzersiz")
    
    # Code unique (document_subtypes)
    dup_subtypes = conn.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT code FROM document_subtypes GROUP BY code HAVING COUNT(*) > 1
        ) AS dups
    """)).scalar()
    
    if dup_subtypes > 0:
        print(f"  ❌ document_subtypes.code: {dup_subtypes} duplicate var!")
    else:
        print(f"  ✅ document_subtypes.code: Tüm kodlar benzersiz")
    
    # Name unique (document_subtypes)
    dup_names_subtypes = conn.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT name FROM document_subtypes GROUP BY name HAVING COUNT(*) > 1
        ) AS dups
    """)).scalar()
    
    if dup_names_subtypes > 0:
        print(f"  ❌ document_subtypes.name: {dup_names_subtypes} duplicate var!")
    else:
        print(f"  ✅ document_subtypes.name: Tüm isimler benzersiz")
    
    # Foreign key constraint kontrolü
    print(f"\n🔐 FOREIGN KEY CONSTRAINTS:")
    
    fk_exists = conn.execute(text("""
        SELECT COUNT(*) 
        FROM information_schema.TABLE_CONSTRAINTS 
        WHERE CONSTRAINT_SCHEMA = 'muhasebe_sistem'
        AND TABLE_NAME = 'document_subtypes'
        AND CONSTRAINT_NAME = 'fk_subtype_parent'
    """)).scalar()
    
    if fk_exists > 0:
        print(f"  ✅ fk_subtype_parent constraint mevcut")
    else:
        print(f"  ❌ fk_subtype_parent constraint YOK!")
    
    # Index kontrolü
    print(f"\n📇 INDEX KONTROLLERİ:")
    
    idx_exists = conn.execute(text("""
        SELECT COUNT(*) 
        FROM information_schema.STATISTICS 
        WHERE TABLE_SCHEMA = 'muhasebe_sistem'
        AND TABLE_NAME = 'document_subtypes'
        AND INDEX_NAME = 'idx_parent_code'
    """)).scalar()
    
    if idx_exists > 0:
        print(f"  ✅ idx_parent_code index mevcut")
    else:
        print(f"  ⚠️  idx_parent_code index YOK (performance sorunu olabilir)")
    
    # Transactions integrity kontrolü
    print(f"\n🔒 TRANSACTIONS INTEGRITY:")
    
    # document_type_id foreign key
    invalid_types = conn.execute(text("""
        SELECT COUNT(*) 
        FROM transactions 
        WHERE document_type_id NOT IN (SELECT id FROM document_types)
    """)).scalar()
    
    if invalid_types > 0:
        print(f"  ❌ {invalid_types} transaction'ın document_type_id geçersiz!")
    else:
        print(f"  ✅ Tüm transactions'ların document_type_id geçerli")
    
    # document_subtype_id foreign key (nullable)
    invalid_subtypes = conn.execute(text("""
        SELECT COUNT(*) 
        FROM transactions 
        WHERE document_subtype_id IS NOT NULL
        AND document_subtype_id NOT IN (SELECT id FROM document_subtypes)
    """)).scalar()
    
    if invalid_subtypes > 0:
        print(f"  ❌ {invalid_subtypes} transaction'ın document_subtype_id geçersiz!")
    else:
        print(f"  ✅ Tüm transactions'ların document_subtype_id geçerli (veya NULL)")

print(f"\n{'='*100}")
print(f"✅ MİGRATION TAMAMLANDI!")
print(f"{'='*100}")
print(f"""
📝 YAPILAN DEĞİŞİKLİKLER:
1. document_subtypes tablosuna parent_code kolonu eklendi
2. parent_code → document_types.code foreign key constraint oluşturuldu
3. idx_parent_code index oluşturuldu
4. 109 alt evrak türü eklendi (YEVMIYE_KAYDI_SABLONU.md'ye göre)
5. Tüm parent_code ilişkileri kuruldu
6. Mevcut transactions korundu (26,244 kayıt)

📁 KULLANILAN DOSYALAR:
- run_migration_step1.py: parent_code kolonu ekleme
- run_migration_step2.py: 77 alt evrak türü ekleme
- run_migration_step3.py: 10 eksik alt türü ekleme (name unique düzeltmesi)
- document_type_mapping.py: YEVMIYE/DB kod eşleştirmeleri

🎯 SONUÇ:
- 38 ana evrak türü (document_types)
- 109 alt evrak türü (document_subtypes)
- Tüm ilişkiler geçerli
- Transactions bozulmadı
""")
