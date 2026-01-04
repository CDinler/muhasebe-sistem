import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.bind.echo = False

# Kenan Köse'yi both yap
db.execute(text("UPDATE contacts SET contact_type = 'both' WHERE code = '320.00547'"))
db.commit()

print("✅ Kenan Köse contact_type = 'both' olarak güncellendi")

# Kontrol et
contact = db.execute(text("SELECT id, code, name, contact_type FROM contacts WHERE code = '320.00547'")).fetchone()
print(f"\nKontrol: {contact[0]} - {contact[1]} - {contact[2]} - Type: {contact[3]}")

db.close()
