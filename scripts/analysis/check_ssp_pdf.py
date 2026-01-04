from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:@localhost:3306/muhasebe_sistem')
db = sessionmaker(bind=engine)()

result = db.execute(text("""
    SELECT invoice_number, invoice_uuid, pdf_path, has_xml, 
           LENGTH(COALESCE(pdf_path, '')) as len 
    FROM einvoices 
    WHERE invoice_number = 'SSP2025000000386' 
    LIMIT 1
""")).fetchone()

if result:
    print(f'Invoice: {result[0]}')
    print(f'UUID: {result[1]}')
    print(f'PDF Path: "{result[2]}"')
    print(f'PDF Path Length: {result[4]}')
    print(f'Has XML: {result[3]}')
    print(f'PDF Path bool (Python): {bool(result[2])}')
    print(f'PDF Path is None: {result[2] is None}')
    print(f'PDF Path == "": {result[2] == ""}')
else:
    print("Kayıt bulunamadı")

db.close()
