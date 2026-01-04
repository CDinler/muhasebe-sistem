import sys
import os
import glob
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.services.einvoice_pdf_processor import EInvoicePDFProcessor

# Database connection
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/muhasebe_sistem"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

try:
    # Downloads'taki tüm PDF'leri bul
    downloads_dir = r"C:\Users\CAGATAY\Downloads\2025_12"
    pdf_files = glob.glob(os.path.join(downloads_dir, "*.pdf"))
    
    uuid_pattern = re.compile(r'([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})')
    
    # XML var, PDF yok olan dosyaları bul
    xml_no_pdf_files = []
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        uuid_match = uuid_pattern.search(filename)
        
        if not uuid_match:
            continue
            
        ettn = uuid_match.group(1).lower()
        
        result = db.execute(text("""
            SELECT id, invoice_number, pdf_path, has_xml 
            FROM einvoices 
            WHERE invoice_uuid = :ettn
        """), {"ettn": ettn}).first()
        
        if result and not result[2] and result[3] == 1:
            xml_no_pdf_files.append(pdf_path)
    
    print(f"XML var, PDF eklenecek: {len(xml_no_pdf_files)} dosya\n")
    
    # Bu PDF'leri yükle
    processor = EInvoicePDFProcessor(db)
    
    success_count = 0
    error_count = 0
    
    for i, pdf_path in enumerate(xml_no_pdf_files, 1):
        filename = os.path.basename(pdf_path)
        print(f"[{i}/{len(xml_no_pdf_files)}] {filename}...")
        
        try:
            einvoice_id = processor.save_invoice_from_pdf_only(pdf_path, direction='incoming')
            if einvoice_id:
                success_count += 1
            else:
                error_count += 1
                print(f"  ❌ Başarısız!")
        except Exception as e:
            error_count += 1
            print(f"  ❌ Hata: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Başarılı: {success_count}")
    print(f"❌ Hatalı: {error_count}")
    print(f"{'='*60}")
    
    # Fiziksel dosya sayısını kontrol et
    pdf_dir = os.path.join(os.path.dirname(__file__), 'data', 'einvoice_pdfs', '2025', '12')
    if os.path.exists(pdf_dir):
        physical_pdfs = glob.glob(os.path.join(pdf_dir, '*.pdf'))
        print(f"\nFiziksel PDF dosyaları (2025/12): {len(physical_pdfs)}")
    
    # DB sayısını kontrol et
    pdf_count = db.execute(text("SELECT COUNT(*) FROM einvoices WHERE pdf_path IS NOT NULL")).scalar()
    print(f"DB'de PDF olan kayıt: {pdf_count}")
    
finally:
    db.close()
