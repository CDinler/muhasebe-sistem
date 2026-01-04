from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://root:@localhost:3306/muhasebe_sistem')
conn = engine.connect()

result = conn.execute(text(
    "SELECT invoice_number, invoice_uuid, pdf_path, has_xml FROM einvoices WHERE invoice_number = :inv_no LIMIT 1"
), {"inv_no": "OAF2025097006960"}).fetchone()

if result:
    print(f"Invoice: {result[0]}")
    print(f"UUID: {result[1]}")
    print(f"PDF Path: [{result[2]}]")
    print(f"PDF is NULL: {result[2] is None}")
    print(f"Has XML: {result[3]}")
else:
    print("❌ Kayıt bulunamadı!")

conn.close()
engine.dispose()
