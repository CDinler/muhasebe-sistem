"""
Bordro için document type'lar ekle
"""
import sys
sys.path.insert(0, 'c:/Projects/muhasebe-sistem/backend')
from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root@localhost:3306/muhasebe_sistem")
with engine.connect() as conn:
    # BORDRO document types ekle
    bordro_types = [
        ('BORDRO', 'Bordro', 'PERSONEL', 10),
    ]
    
    for code, name, category, sort_order in bordro_types:
        exists = conn.execute(text(f"SELECT COUNT(*) FROM document_types WHERE code = '{code}'")).scalar()
        if not exists:
            conn.execute(text(f"""
                INSERT INTO document_types (code, name, category, sort_order, is_active)
                VALUES ('{code}', '{name}', '{category}', {sort_order}, 1)
            """))
            print(f"✅ {name} eklendi")
        else:
            print(f"⏭️  {name} zaten var")
    
    # BORDRO subtypes ekle
    bordro_subtypes = [
        ('BORDRO_LUCA', 'BORDRO', 'Bordro (Luca)', 'BORDRO', 1),
        ('BORDRO_ELDEN', 'BORDRO', 'Bordro (Elden)', 'BORDRO', 2),
        ('BORDRO_A', 'BORDRO', 'Bordro A Tipi', 'BORDRO', 3),
        ('BORDRO_B', 'BORDRO', 'Bordro B Tipi', 'BORDRO', 4),
    ]
    
    for code, parent_code, name, category, sort_order in bordro_subtypes:
        exists = conn.execute(text(f"SELECT COUNT(*) FROM document_subtypes WHERE code = '{code}'")).scalar()
        if not exists:
            conn.execute(text(f"""
                INSERT INTO document_subtypes (code, parent_code, name, category, sort_order, is_active)
                VALUES ('{code}', '{parent_code}', '{name}', '{category}', {sort_order}, 1)
            """))
            print(f"✅ {name} eklendi")
        else:
            print(f"⏭️  {name} zaten var")
    
    conn.commit()
    print("\n🎉 Bordro document types hazır!")
