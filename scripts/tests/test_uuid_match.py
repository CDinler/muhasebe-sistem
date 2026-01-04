import re
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, '.')

from app.models import EInvoice

engine = create_engine('mysql+pymysql://root:@localhost:3306/muhasebe_sistem')
db = sessionmaker(bind=engine)()

# Test PDF filename
filename = "ULU2025000001690_a22c7491-1980-4d40-a803-aec3575e030e.pdf"

# Extract ETTN from filename (same as code)
uuid_pattern = re.compile(r'([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})')
uuid_match = uuid_pattern.search(filename)

if uuid_match:
    ettn_from_filename = uuid_match.group(1).lower()
    print(f"Extracted ETTN: {ettn_from_filename}")
    
    # First check: case-insensitive
    existing_record = db.query(EInvoice).filter(
        func.lower(EInvoice.invoice_uuid) == ettn_from_filename
    ).first()
    
    if existing_record:
        print(f"\n✅ Kayıt BULUNDU!")
        print(f"  ID: {existing_record.id}")
        print(f"  Invoice No: {existing_record.invoice_number}")
        print(f"  UUID (DB): {existing_record.invoice_uuid}")
        print(f"  PDF Path: {existing_record.pdf_path}")
        print(f"  Has XML: {existing_record.has_xml}")
        
        if existing_record.pdf_path:
            print(f"\n❌ PDF VAR - Skip edilmeli")
        else:
            print(f"\n✅ PDF YOK - PDF eklenebilir!")
    else:
        print(f"\n❌ Kayıt BULUNAMADI!")
        
        # Try direct query
        result = db.execute(text("""
            SELECT id, invoice_number, invoice_uuid, pdf_path
            FROM einvoices
            WHERE LOWER(invoice_uuid) = :ettn
            LIMIT 1
        """), {"ettn": ettn_from_filename}).fetchone()
        
        if result:
            print(f"\n  Ama direkt SQL ile BULUNDU:")
            print(f"    ID: {result[0]}")
            print(f"    Invoice: {result[1]}")
            print(f"    UUID: {result[2]}")
            print(f"    PDF: {result[3]}")
        else:
            print(f"  Direkt SQL ile de bulunamadı!")

db.close()
