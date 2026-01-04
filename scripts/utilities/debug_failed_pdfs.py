"""
2 başarısız PDF dosyasını debug et
"""
import os
from pathlib import Path
from app.services.einvoice_pdf_processor import EInvoicePDFProcessor
from app.core.database import SessionLocal

# Dosyalar
failed_files = [
    "Y022025000012268_fbe9419d-b523-42c2-81e2-43580b846f9d.pdf",
    "YA02025000000576_3da9f53a-2cd9-4696-8eeb-c50c77e8fb87.pdf"
]

downloads_dir = r"C:\Users\CAGATAY\Downloads\2025_12"

db = SessionLocal()
processor = EInvoicePDFProcessor(db)

for filename in failed_files:
    pdf_path = os.path.join(downloads_dir, filename)
    
    print(f"\n{'='*80}")
    print(f"DOSYA: {filename}")
    print(f"{'='*80}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ DOSYA BULUNAMADI: {pdf_path}")
        continue
    
    try:
        # PDF'den veri çıkar
        print("\n1️⃣ PDF parse ediliyor...")
        data = processor.extract_invoice_data_from_pdf(pdf_path)
        
        print(f"\n✅ PARSE BAŞARILI:")
        print(f"   Invoice No: {data.get('invoice_no')}")
        print(f"   ETTN: {data.get('ettn')}")
        print(f"   Tarih: {data.get('issue_date')}")
        print(f"   Supplier VKN: {data.get('supplier_tax_number')}")
        print(f"   Supplier Name: {data.get('supplier_name')}")
        print(f"   Customer VKN: {data.get('customer_tax_number')}")
        print(f"   Customer Name: {data.get('customer_name')}")
        print(f"   Tutar: {data.get('payable_amount')}")
        
        # Validasyon
        print("\n2️⃣ Validasyon yapılıyor...")
        is_valid, errors = processor.validate_extracted_data(data)
        
        if is_valid:
            print(f"✅ VALİDASYON BAŞARILI")
            if errors:
                print(f"⚠️ Warnings: {errors}")
        else:
            print(f"❌ VALİDASYON HATASI:")
            for err in errors:
                print(f"   - {err}")
        
        # Database kaydet
        print("\n3️⃣ Database'e kaydediliyor...")
        einvoice_id = processor.save_invoice_from_pdf_only(pdf_path, original_filename=filename, direction='incoming')
        
        if einvoice_id:
            print(f"✅ BAŞARILI! ID: {einvoice_id}")
        else:
            print(f"❌ KAYIT BAŞARISIZ (None return)")
            
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()

db.close()
print(f"\n{'='*80}")
print("DEBUG TAMAMLANDI")
print(f"{'='*80}")
