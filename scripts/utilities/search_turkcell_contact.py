"""
Türkcell contact araması
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Contacts tablosunda
query = text("""
    SELECT id, name, vkn_tckn, phone, email 
    FROM contacts 
    WHERE LOWER(name) LIKE '%türkcell%' 
       OR LOWER(name) LIKE '%turkcell%'
""")

results = session.execute(query).fetchall()

if results:
    print(f'✅ {len(results)} Türkcell contact bulundu:')
    for r in results:
        print(f'  ID: {r[0]}, Ad: {r[1]}, VKN: {r[2]}')
else:
    print('❌ Contacts tablosunda Türkcell bulunamadı')

session.close()
