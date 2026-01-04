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

print("🔍 parent_code NULL olan document_subtypes kayıtları")
print("=" * 100)

with engine.connect() as conn:
    # parent_code NULL olanlar
    null_parents = conn.execute(text("""
        SELECT id, code, name, category, sort_order, is_active, created_at
        FROM document_subtypes
        WHERE parent_code IS NULL
        ORDER BY id
    """)).fetchall()
    
    if null_parents:
        print(f"\n❌ {len(null_parents)} kayıtta parent_code NULL:\n")
        for id, code, name, category, sort_order, is_active, created_at in null_parents:
            print(f"  ID {id:3}: {code:30} ({name:40}) - {category:10} - created: {created_at}")
        
        print("\n" + "=" * 100)
        print("💡 Bu kayıtlar migration öncesinden kalmış olabilir.")
        print("   Her birini uygun parent_code ile güncellemeliyiz.")
        
        # Her biri için olası parent önerileri
        print("\n📝 PARENT CODE ÖNERİLERİ:")
        print("=" * 100)
        
        for id, code, name, category, sort_order, is_active, created_at in null_parents:
            # Code'a göre parent tahmin et
            suggestions = []
            
            # E-Belge türleri genelde faturalara aittir
            if 'E_FATURA' in code or 'E_ARSIV' in code:
                suggestions = ['ALIS_FATURA', 'SATIS_FATURA']
            elif 'E_IRSALIYE' in code:
                suggestions = ['ALIS_FATURA', 'SATIS_FATURA']
            elif 'E_SMM' in code:
                suggestions = ['SERBEST_MESLEK_MAKBUZU']
            elif 'KAGIT' in code or 'MATBU' in code:
                suggestions = ['ALIS_FATURA', 'SATIS_FATURA']
            
            # Transaction'da kullanılıyor mu kontrol et
            txn_count = conn.execute(text(f"""
                SELECT COUNT(*) FROM transactions WHERE document_subtype_id = {id}
            """)).scalar()
            
            if suggestions:
                print(f"\n  {code}:")
                print(f"    📊 {txn_count} transaction kullanıyor")
                print(f"    💡 Önerilen parent_code: {', '.join(suggestions)}")
            else:
                print(f"\n  {code}:")
                print(f"    📊 {txn_count} transaction kullanıyor")
                print(f"    ⚠️  Parent önerisi yok, manuel kontrol gerekli")
                
                # Category'ye göre olası parent'lar
                if category == 'E_BELGE':
                    possible = conn.execute(text("""
                        SELECT code, name FROM document_types 
                        WHERE category = 'FATURA' 
                        ORDER BY code
                    """)).fetchall()
                    if possible:
                        print(f"    📁 FATURA kategorisindeki olasılıklar:")
                        for pc, pn in possible:
                            print(f"       - {pc} ({pn})")
    else:
        print("✅ Tüm document_subtypes kayıtlarında parent_code dolu")
        
    # Toplam özet
    total = conn.execute(text("SELECT COUNT(*) FROM document_subtypes")).scalar()
    with_parent = conn.execute(text("SELECT COUNT(*) FROM document_subtypes WHERE parent_code IS NOT NULL")).scalar()
    
    print("\n" + "=" * 100)
    print(f"📊 ÖZET:")
    print(f"  Toplam alt tür: {total}")
    print(f"  parent_code dolu: {with_parent}")
    print(f"  parent_code NULL: {total - with_parent}")
