"""
SigningTime kontrolü
"""
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
import os
import xml.etree.ElementTree as ET

db = SessionLocal()

try:
    # signing_time olan bir fatura al
    with_signing = db.query(EInvoice).filter(
        EInvoice.signing_time.isnot(None),
        EInvoice.xml_file_path.isnot(None)
    ).first()
    
    # signing_time olmayan bir fatura al
    without_signing = db.query(EInvoice).filter(
        EInvoice.signing_time.is_(None),
        EInvoice.xml_file_path.isnot(None)
    ).first()
    
    print("=" * 60)
    print("SIGNING_TIME KONTROLÜ")
    print("=" * 60)
    
    if with_signing:
        print(f"\n✅ signing_time VAR: {with_signing.invoice_number}")
        print(f"   Değer: {with_signing.signing_time}")
        print(f"   XML: {with_signing.xml_file_path}")
        
        if with_signing.xml_file_path and os.path.exists(with_signing.xml_file_path):
            with open(with_signing.xml_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SigningTime' in content:
                    print("   ✅ XML'de SigningTime var")
                else:
                    print("   ❌ XML'de SigningTime YOK!")
    
    if without_signing:
        print(f"\n❌ signing_time YOK: {without_signing.invoice_number}")
        print(f"   XML: {without_signing.xml_file_path}")
        
        if without_signing.xml_file_path and os.path.exists(without_signing.xml_file_path):
            with open(without_signing.xml_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SigningTime' in content:
                    print("   ⚠️ XML'de SigningTime VAR ama parse edilmemiş!")
                    # SigningTime satırını bul
                    for line in content.split('\n'):
                        if 'SigningTime' in line:
                            print(f"   Satır: {line.strip()}")
                            break
                else:
                    print("   ✅ XML'de de SigningTime yok (normal)")
    
    print("\n" + "=" * 60)
    
finally:
    db.close()
