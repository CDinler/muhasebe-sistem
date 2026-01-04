import sys
import os
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/muhasebe_sistem"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

try:
    # Downloads'taki PDF'lerin ETTN'lerini topla
    downloads_dir = r"C:\Users\CAGATAY\Downloads\2025_12"
    pdf_files = glob.glob(os.path.join(downloads_dir, "*.pdf"))
    
    print(f"Downloads'ta {len(pdf_files)} PDF var")
    
    # İlk 10 PDF'in ETTN'sini çıkar
    import re
    uuid_pattern = re.compile(r'([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})')
    
    found_count = 0
    for pdf_path in pdf_files[:20]:
        filename = os.path.basename(pdf_path)
        uuid_match = uuid_pattern.search(filename)
        if uuid_match:
            ettn = uuid_match.group(1).lower()
            
            # Bu ETTN için kayıt var mı? PDF var mı?
            result = db.execute(text("""
                SELECT id, invoice_number, pdf_path, has_xml, source 
                FROM einvoices 
                WHERE invoice_uuid = :ettn
            """), {"ettn": ettn}).first()
            
            if result:
                einvoice_id, invoice_no, pdf_path_db, has_xml, source = result
                if not pdf_path_db and has_xml == 1:
                    print(f"\n✅ BULUNDU!")
                    print(f"  Dosya: {filename}")
                    print(f"  ETTN: {ettn}")
                    print(f"  ID: {einvoice_id}")
                    print(f"  Invoice No: {invoice_no}")
                    print(f"  PDF: {pdf_path_db}")
                    print(f"  Has XML: {has_xml}")
                    print(f"  Source: {source}")
                    print(f"\n  PDF Path: {pdf_path}")
                    found_count += 1
                    
                    if found_count >= 5:
                        break
    
    print(f"\n\nToplam bulunan (XML var, PDF yok): {found_count}")
    
finally:
    db.close()
