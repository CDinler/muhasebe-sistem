import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.bind.echo = False

result = db.execute(text("""
    SELECT name, COUNT(*) as count 
    FROM contacts 
    GROUP BY LOWER(TRIM(name)) 
    HAVING COUNT(*) > 1 
    LIMIT 5
""")).fetchall()

print("Duplike isimler:")
if result:
    for r in result:
        print(f"  {r[0]}: {r[1]} adet")
else:
    print("  Yok")

db.close()
