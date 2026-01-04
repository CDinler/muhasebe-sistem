"""
Oluşturulan hesapları kontrol eder
"""
from app.core.database import engine
from sqlalchemy import text

conn = engine.connect()

result = conn.execute(text("""
    SELECT code, name 
    FROM accounts 
    WHERE code LIKE '191.%.0%' 
       OR code IN ('602.00002', '689.00001', '689.00005', '679.00001', '659.00003', '740.00209')
    ORDER BY code
"""))

print('OLUŞTURULAN HESAPLAR:')
print('=' * 80)
for row in result:
    print(f'{row[0]:<15} {row[1]}')

conn.close()
