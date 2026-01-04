"""
SigningTime parse test - gerçek XML'den
"""
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
import xml.etree.ElementTree as ET
from datetime import datetime

db = SessionLocal()

try:
    # signing_time olmayan bir XML al
    inv = db.query(EInvoice).filter(
        EInvoice.signing_time.is_(None),
        EInvoice.xml_file_path.isnot(None)
    ).first()
    
    if inv and inv.xml_file_path:
        print(f"XML: {inv.xml_file_path}")
        
        tree = ET.parse(inv.xml_file_path)
        root = tree.getroot()
        
        # Namespace'li arama (wildcard)
        result = root.find('.//{*}SigningTime')
        
        if result is not None:
            time_str = result.text
            print(f"✅ Bulundu: {time_str}")
            
            try:
                dt = datetime.fromisoformat(time_str)
                print(f"✅ Parse edildi: {dt}")
            except Exception as e:
                print(f"❌ Parse hatası: {e}")
        else:
            print("❌ SigningTime bulunamadı")
    else:
        print("Uygun XML bulunamadı")
        
finally:
    db.close()

