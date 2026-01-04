"""
Boş supplier_name olan bir faturanın XML'ini incele
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
import os

def main():
    db = SessionLocal()
    
    try:
        # Boş supplier_name olan ilk faturayı al
        einvoice = db.query(EInvoice).filter(
            (EInvoice.supplier_name == None) | (EInvoice.supplier_name == '')
        ).first()
        
        if einvoice:
            print(f"Fatura No: {einvoice.invoice_number}")
            print(f"XML Path: {einvoice.xml_file_path}")
            print(f"Supplier VKN: {einvoice.supplier_tax_number}")
            print(f"Customer Name: {einvoice.customer_name}")
            
            # XML dosyasını oku
            if os.path.exists(einvoice.xml_file_path):
                with open(einvoice.xml_file_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                # Supplier kısmını bul
                if '<cac:AccountingSupplierParty>' in xml_content:
                    start = xml_content.find('<cac:AccountingSupplierParty>')
                    end = xml_content.find('</cac:AccountingSupplierParty>') + len('</cac:AccountingSupplierParty>')
                    supplier_section = xml_content[start:end]
                    
                    print("\n" + "="*80)
                    print("SUPPLIER SEKSİYONU:")
                    print("="*80)
                    print(supplier_section[:2000])  # İlk 2000 karakter
                else:
                    print("\n❌ XML'de AccountingSupplierParty bulunamadı!")
            else:
                print(f"\n❌ XML dosyası bulunamadı: {einvoice.xml_file_path}")
        else:
            print("Boş supplier_name olan fatura bulunamadı")
            
    finally:
        db.close()

if __name__ == "__main__":
    main()
