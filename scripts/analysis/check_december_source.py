from sqlalchemy import create_engine, text
import os

os.chdir('C:/Projects/muhasebe-sistem/backend')
engine = create_engine('mysql+pymysql://root@localhost/muhasebe_sistem')
conn = engine.connect()

result = conn.execute(text("""
    SELECT has_xml, source, 
           COUNT(*) as cnt, 
           SUM(CASE WHEN signing_time IS NOT NULL THEN 1 ELSE 0 END) as with_signing
    FROM einvoices 
    WHERE issue_date >= '2025-12-01' AND issue_date < '2026-01-01'
    GROUP BY has_xml, source
    ORDER BY has_xml, source
"""))

print('\nARALIK - source analizi:\n')
for row in result:
    print(f'has_xml={row.has_xml}, source={row.source}: {row.cnt} fatura, {row.with_signing} signing_time var')

conn.close()
