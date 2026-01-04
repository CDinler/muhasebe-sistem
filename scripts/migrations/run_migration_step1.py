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

print("🔄 ADIM 1: Eksik document_types ekleniyor...")
print("=" * 80)

with engine.connect() as conn:
    # Eksik kayıtlar
    missing_types = [
        ('ALIS_FATURASI', 'Alış Faturası', 'FATURA', 1),
        ('SATIS_FATURASI', 'Satış Faturası', 'FATURA', 2),
        ('IADE_FATURASI', 'İade Faturası', 'FATURA', 3),
        ('VIRMAN', 'Banka Virman', 'BANKA', 4),
        ('MAHSUP_FISI', 'Mahsup Fişi', 'MUHASEBE', 1),
        ('YEVMIYE_FISI', 'Yevmiye Fişi', 'MUHASEBE', 2),
        ('ACILIS_FISI', 'Açılış Fişi', 'MUHASEBE', 3),
        ('DUZELTICI_FIS', 'Düzeltici Fiş', 'MUHASEBE', 5),
    ]
    
    added = 0
    skipped = 0
    
    for code, name, category, sort_order in missing_types:
        # Code veya name var mı kontrol et
        exists = conn.execute(text(f"SELECT COUNT(*) FROM document_types WHERE code = '{code}' OR name = '{name}'")).scalar()
        
        if exists == 0:
            conn.execute(text(f"""
                INSERT INTO document_types (code, name, category, sort_order, is_active) 
                VALUES ('{code}', '{name}', '{category}', {sort_order}, 1)
            """))
            conn.commit()
            print(f"✅ Eklendi: {code} ({name})")
            added += 1
        else:
            print(f"⏭️  Atlandı (mevcut): {code} veya {name}")
            skipped += 1
    
    print(f"\n📊 Özet: {added} eklendi, {skipped} atlandı")

print("\n" + "=" * 80)
print("🔄 ADIM 2: Transactions güncelleniyor...")
print("=" * 80)

with engine.connect() as conn:
    # Code eşleştirmeleri (eski → yeni)
    mappings = [
        ('ALIS_FATURA', 'ALIS_FATURASI'),
        ('SATIS_FATURA', 'SATIS_FATURASI'),
        ('IADE_FATURA', 'IADE_FATURASI'),
        ('YEVMIYE', 'YEVMIYE_FISI'),
        ('MAHSUP', 'MAHSUP_FISI'),
        ('ACILIS', 'ACILIS_FISI'),
        ('DUZELTME', 'DUZELTICI_FIS'),
        ('BANKA_VIRMAN', 'VIRMAN'),
    ]
    
    total_updated = 0
    
    for old_code, new_code in mappings:
        # Eski kod var mı?
        old_id = conn.execute(text(f"SELECT id FROM document_types WHERE code = '{old_code}'")).scalar()
        new_id = conn.execute(text(f"SELECT id FROM document_types WHERE code = '{new_code}'")).scalar()
        
        if old_id and new_id:
            # Transaction sayısı
            count = conn.execute(text(f"SELECT COUNT(*) FROM transactions WHERE document_type_id = {old_id}")).scalar()
            
            if count > 0:
                conn.execute(text(f"UPDATE transactions SET document_type_id = {new_id} WHERE document_type_id = {old_id}"))
                conn.commit()
                print(f"✅ {old_code} → {new_code}: {count} transaction güncellendi")
                total_updated += count
            else:
                print(f"⏭️  {old_code}: 0 transaction (güncelleme yok)")
        else:
            if not old_id:
                print(f"⚠️  {old_code}: Bulunamadı (belki daha önce silinmiş)")
            if not new_id:
                print(f"❌ {new_code}: Hedef kod yok!")
    
    print(f"\n📊 Toplam: {total_updated} transaction güncellendi")

print("\n" + "=" * 80)
print("🔄 ADIM 3: parent_code kolonu ekleniyor...")
print("=" * 80)

with engine.connect() as conn:
    # Kolon var mı kontrol et
    has_column = conn.execute(text("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'muhasebe_sistem' 
        AND TABLE_NAME = 'document_subtypes' 
        AND COLUMN_NAME = 'parent_code'
    """)).scalar()
    
    if has_column == 0:
        conn.execute(text("ALTER TABLE document_subtypes ADD COLUMN parent_code VARCHAR(50) AFTER code"))
        conn.commit()
        print("✅ parent_code kolonu eklendi")
        
        # Index ve foreign key
        conn.execute(text("ALTER TABLE document_subtypes ADD INDEX idx_parent_code (parent_code)"))
        conn.commit()
        print("✅ Index oluşturuldu")
        
        conn.execute(text("ALTER TABLE document_subtypes ADD CONSTRAINT fk_subtype_parent FOREIGN KEY (parent_code) REFERENCES document_types(code)"))
        conn.commit()
        print("✅ Foreign key constraint eklendi")
    else:
        print("⏭️  parent_code kolonu zaten var")

print("\n" + "=" * 80)
print("✅ Migration tamamlandı!")
print("=" * 80)
