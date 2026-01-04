"""
Mevcut e-faturaların supplier_iban alanını doldurur.
1. Contact tablosundaki IBAN bilgisini kullanır (varsa)
2. Yoksa XML dosyasından parse eder
"""
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.einvoice import EInvoice
from app.models.contact import Contact
import xml.etree.ElementTree as ET

# Database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

NAMESPACES = {
    'n1': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
}

def get_iban_from_xml(xml_path: str) -> str | None:
    """XML dosyasından IBAN bilgisini parse eder"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # PaymentMeans içinde PayeeFinancialAccount ara
        payment_means_list = root.findall('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PaymentMeans')
        for payment_means in payment_means_list:
            # Currency code kontrol et (TRY olanları al)
            currency_elem = payment_means.find('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PayeeFinancialAccount/{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CurrencyCode')
            currency_code = currency_elem.text if currency_elem is not None else None
            
            if currency_code == 'TRY' or not currency_code:
                iban_elem = payment_means.find('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PayeeFinancialAccount/{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID')
                if iban_elem is not None and iban_elem.text:
                    iban = iban_elem.text.strip()
                    if iban.startswith('TR'):  # IBAN formatı kontrolü
                        return iban
        
        return None
    except Exception as e:
        print(f"  ⚠️  XML parse hatası: {e}")
        return None


def update_einvoice_ibans():
    """E-faturaların IBAN bilgilerini günceller"""
    db = SessionLocal()
    
    try:
        # IBAN'ı olmayan e-faturaları al
        einvoices = db.query(EInvoice).filter(
            (EInvoice.supplier_iban == None) | (EInvoice.supplier_iban == '')
        ).all()
        
        print(f"📋 Toplam {len(einvoices)} e-fatura bulundu (IBAN yok)")
        print()
        
        updated_from_contact = 0
        updated_from_xml = 0
        not_found = 0
        
        for idx, einvoice in enumerate(einvoices, 1):
            print(f"[{idx}/{len(einvoices)}] {einvoice.invoice_number} - {einvoice.supplier_name[:40]}")
            
            iban = None
            source = None
            
            # 1. Contact tablosundan IBAN al (varsa)
            if einvoice.contact_id:
                contact = db.query(Contact).filter(Contact.id == einvoice.contact_id).first()
                if contact and contact.iban:
                    iban = contact.iban
                    source = "contact"
            
            # 2. Yoksa XML'den parse et
            if not iban and einvoice.xml_file_path:
                # XML dosya yolunu kontrol et
                xml_path = einvoice.xml_file_path
                if os.path.exists(xml_path):
                    iban = get_iban_from_xml(xml_path)
                    if iban:
                        source = "xml"
                else:
                    print(f"  ⚠️  XML dosyası bulunamadı: {xml_path}")
            
            # 3. IBAN bulunduysa güncelle
            if iban:
                einvoice.supplier_iban = iban
                if source == "contact":
                    updated_from_contact += 1
                    print(f"  ✅ Contact'tan alındı: {iban}")
                else:
                    updated_from_xml += 1
                    print(f"  ✅ XML'den alındı: {iban}")
                
                # Contact'ta yoksa ekle
                if einvoice.contact_id and source == "xml":
                    contact = db.query(Contact).filter(Contact.id == einvoice.contact_id).first()
                    if contact and not contact.iban:
                        contact.iban = iban
                        print(f"  📝 Contact'a da eklendi")
            else:
                not_found += 1
                print(f"  ❌ IBAN bulunamadı")
            
            # Her 10 kayıtta bir commit
            if idx % 10 == 0:
                db.commit()
                print(f"  💾 {idx} kayıt commit edildi")
        
        # Son commit
        db.commit()
        
        print()
        print("=" * 60)
        print(f"✅ İşlem tamamlandı!")
        print(f"📊 Contact'tan güncellenen: {updated_from_contact}")
        print(f"📊 XML'den güncellenen: {updated_from_xml}")
        print(f"📊 IBAN bulunamayan: {not_found}")
        print(f"📊 Toplam güncellenen: {updated_from_contact + updated_from_xml}")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Hata oluştu: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_einvoice_ibans()
