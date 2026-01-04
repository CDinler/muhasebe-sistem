"""
Boş supplier_name olan faturaları yeniden parse et
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
from app.services.einvoice_xml_service import parse_xml_invoice
import os

def main():
    db = SessionLocal()
    
    try:
        # Boş supplier_name olanları al
        einvoices = db.query(EInvoice).filter(
            (EInvoice.supplier_name == None) | (EInvoice.supplier_name == '')
        ).all()
        
        print(f"📋 Toplam {len(einvoices)} fatura bulundu (supplier_name boş)")
        
        updated_count = 0
        error_count = 0
        
        for idx, einvoice in enumerate(einvoices, 1):
            try:
                # XML dosyasını oku
                if not os.path.exists(einvoice.xml_file_path):
                    print(f"  ⚠️  [{idx}/{len(einvoices)}] XML bulunamadı: {einvoice.invoice_number}")
                    error_count += 1
                    continue
                
                with open(einvoice.xml_file_path, 'rb') as f:
                    xml_content = f.read()
                
                # Yeniden parse et
                invoice_data, errors = parse_xml_invoice(xml_content, einvoice.xml_file_path)
                
                # supplier_name varsa güncelle
                if invoice_data.get('supplier_name'):
                    einvoice.supplier_name = invoice_data['supplier_name']
                    
                    # Diğer eksik alanları da güncelle
                    if invoice_data.get('supplier_address'):
                        einvoice.supplier_address = invoice_data['supplier_address']
                    if invoice_data.get('supplier_city'):
                        einvoice.supplier_city = invoice_data['supplier_city']
                    if invoice_data.get('supplier_district'):
                        einvoice.supplier_district = invoice_data['supplier_district']
                    if invoice_data.get('supplier_tax_office'):
                        einvoice.supplier_tax_office = invoice_data['supplier_tax_office']
                    if invoice_data.get('supplier_phone'):
                        einvoice.supplier_phone = invoice_data['supplier_phone']
                    if invoice_data.get('supplier_email'):
                        einvoice.supplier_email = invoice_data['supplier_email']
                    
                    updated_count += 1
                    
                    if updated_count % 50 == 0:
                        print(f"  💾 {updated_count} fatura güncellendi...")
                        db.commit()
                else:
                    print(f"  ⚠️  [{idx}/{len(einvoices)}] Parse edildi ama supplier_name yok: {einvoice.invoice_number}")
                    error_count += 1
                    
            except Exception as e:
                print(f"  ❌ [{idx}/{len(einvoices)}] Hata: {einvoice.invoice_number} - {e}")
                error_count += 1
        
        db.commit()
        
        print("\n" + "="*60)
        print("ÖZET")
        print("="*60)
        print(f"✅ Güncellenen: {updated_count}")
        print(f"❌ Hatalı/Boş: {error_count}")
        print(f"📊 Toplam: {len(einvoices)}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
