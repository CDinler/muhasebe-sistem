from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:@localhost:3306/muhasebe_sistem')
db = sessionmaker(bind=engine)()

result = db.execute(text("""
    SELECT invoice_number, invoice_uuid, pdf_path, has_xml
    FROM einvoices 
    WHERE invoice_number = 'ULU2025000001690' 
    LIMIT 1
""")).fetchone()

if result:
    invoice_no, uuid, pdf_path, has_xml = result
    print(f'Invoice: {invoice_no}')
    print(f'UUID: {uuid}')
    print(f'PDF Path: "{pdf_path}"')
    print(f'Has XML: {has_xml}')
    print(f'PDF Path bool: {bool(pdf_path)}')
    print(f'PDF Path is None: {pdf_path is None}')
    
    # Python'da if pdf_path kontrolü
    if pdf_path:
        print("❌ if pdf_path: TRUE (Skip edilir)")
    else:
        print("✅ if pdf_path: FALSE (PDF eklenebilir)")
else:
    print("Kayıt bulunamadı")

db.close()
