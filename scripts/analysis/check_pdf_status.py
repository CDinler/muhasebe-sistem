import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/muhasebe_sistem"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

try:
    # PDF olan kayıtlar
    pdf_count = db.execute(text("SELECT COUNT(*) FROM einvoices WHERE pdf_path IS NOT NULL")).scalar()
    print(f"PDF var: {pdf_count}")
    
    # Toplam kayıt
    total_count = db.execute(text("SELECT COUNT(*) FROM einvoices")).scalar()
    print(f"Toplam: {total_count}")
    
    # PDF NULL ama XML var
    xml_no_pdf = db.execute(text("SELECT COUNT(*) FROM einvoices WHERE pdf_path IS NULL AND has_xml = 1")).scalar()
    print(f"PDF NULL ama XML var: {xml_no_pdf}")
    
    # PDF NULL ve XML NULL (sadece PDF'den oluşturulmuş)
    pdf_only = db.execute(text("SELECT COUNT(*) FROM einvoices WHERE pdf_path IS NOT NULL AND has_xml = 0")).scalar()
    print(f"Sadece PDF kayıtları: {pdf_only}")
    
    # Test: 2025-12 dizinindeki PDF sayısı
    import glob
    pdf_dir = os.path.join(os.path.dirname(__file__), 'data', 'einvoice_pdfs', '2025', '12')
    if os.path.exists(pdf_dir):
        pdf_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
        print(f"\nFiziksel PDF dosyaları (2025/12): {len(pdf_files)}")
    
finally:
    db.close()
