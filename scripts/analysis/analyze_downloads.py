import sys
import os
import glob
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/muhasebe_sistem"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

try:
    # Downloads'taki tüm PDF'leri kontrol et
    downloads_dir = r"C:\Users\CAGATAY\Downloads\2025_12"
    pdf_files = glob.glob(os.path.join(downloads_dir, "*.pdf"))
    
    print(f"Downloads dizininde toplam {len(pdf_files)} PDF var\n")
    
    uuid_pattern = re.compile(r'([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})')
    
    kategoriler = {
        'pdf_var': [],  # Zaten PDF kaydedilmiş
        'xml_var_pdf_yok': [],  # XML var, PDF eklenebilir
        'kayit_yok': [],  # Hiç kayıt yok, yeni oluşturulacak
        'ettn_yok': []  # ETTN çıkaramadık
    }
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        uuid_match = uuid_pattern.search(filename)
        
        if not uuid_match:
            kategoriler['ettn_yok'].append(filename)
            continue
            
        ettn = uuid_match.group(1).lower()
        
        # Bu ETTN için kayıt var mı?
        result = db.execute(text("""
            SELECT id, invoice_number, pdf_path, has_xml 
            FROM einvoices 
            WHERE invoice_uuid = :ettn
        """), {"ettn": ettn}).first()
        
        if not result:
            kategoriler['kayit_yok'].append(filename)
        elif result[2]:  # pdf_path dolu
            kategoriler['pdf_var'].append(filename)
        else:  # pdf_path NULL
            kategoriler['xml_var_pdf_yok'].append(filename)
    
    print("=" * 80)
    print(f"✅ Zaten PDF kaydedilmiş: {len(kategoriler['pdf_var'])}")
    print(f"📎 XML var, PDF eklenebilir: {len(kategoriler['xml_var_pdf_yok'])}")
    print(f"🆕 Hiç kayıt yok, yeni: {len(kategoriler['kayit_yok'])}")
    print(f"❌ ETTN çıkaramadık: {len(kategoriler['ettn_yok'])}")
    print("=" * 80)
    print(f"\nTOPLAM: {sum(len(v) for v in kategoriler.values())}")
    
    # Detaylar
    if kategoriler['ettn_yok']:
        print(f"\n❌ ETTN çıkaramadığımız dosyalar ({len(kategoriler['ettn_yok'])}):")
        for f in kategoriler['ettn_yok'][:10]:
            print(f"  - {f}")
    
    if kategoriler['kayit_yok']:
        print(f"\n🆕 Hiç kaydı olmayan dosyalar (ilk 5):")
        for f in kategoriler['kayit_yok'][:5]:
            print(f"  - {f}")
    
finally:
    db.close()
