"""
Database'den document_type ve document_subtype kolonlarını sil
"""
import sys
sys.path.insert(0, 'c:/Projects/muhasebe-sistem/backend')
from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root@localhost:3306/muhasebe_sistem")
with engine.connect() as conn:
    print("🗑️  document_type ve document_subtype kolonları siliniyor...")
    
    # 1. document_type kolonunu sil
    try:
        conn.execute(text("ALTER TABLE transactions DROP COLUMN document_type"))
        print("✅ document_type kolonu silindi")
    except Exception as e:
        print(f"⚠️  document_type: {str(e)}")
    
    # 2. document_subtype kolonunu sil
    try:
        conn.execute(text("ALTER TABLE transactions DROP COLUMN document_subtype"))
        print("✅ document_subtype kolonu silindi")
    except Exception as e:
        print(f"⚠️  document_subtype: {str(e)}")
    
    conn.commit()
    print("\n🎉 Kolonlar silindi! Artık sadece document_type_id ve document_subtype_id kullanılıyor.")
