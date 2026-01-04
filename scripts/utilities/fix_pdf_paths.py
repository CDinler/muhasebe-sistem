"""
PDF path'leri düzelt - invoice_number yerine gerçek dosya adını kullan
"""
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
import os

db = SessionLocal()

try:
    # 2025-12 ayındaki tüm PDF'li faturaları al
    invoices = db.query(EInvoice).filter(
        EInvoice.pdf_path.isnot(None),
        EInvoice.pdf_path != ''
    ).all()
    
    print(f"\n📊 Toplam {len(invoices)} PDF'li fatura bulundu")
    
    pdf_base_dir = "C:\\Projects\\muhasebe-sistem\\backend\\data"
    fixed = 0
    already_ok = 0
    not_found = 0
    
    for invoice in invoices:
        if not invoice.pdf_path:
            continue
            
        # Tam path oluştur
        full_path = os.path.join(pdf_base_dir, invoice.pdf_path)
        
        # Dosya var mı?
        if os.path.exists(full_path):
            already_ok += 1
            continue
        
        # Dosya yok - UUID'ye göre gerçek dosyayı bul
        if invoice.invoice_uuid:
            # PDF klasörü yıl/ay olarak
            from datetime import datetime
            year = invoice.issue_date.year if invoice.issue_date else 2025
            month = invoice.issue_date.month if invoice.issue_date else 12
            
            search_dir = os.path.join(pdf_base_dir, "einvoice_pdfs", str(year), str(month).zfill(2))
            
            if os.path.exists(search_dir):
                # UUID'yi küçük harfe çevir
                uuid_lower = invoice.invoice_uuid.lower()
                
                # Bu UUID'ye sahip dosyayı bul
                for filename in os.listdir(search_dir):
                    if uuid_lower in filename.lower():
                        # Gerçek dosya adını bulduk!
                        real_filename = filename
                        new_pdf_path = f"einvoice_pdfs\\{year}\\{month:02d}\\{real_filename}"
                        
                        print(f"\n🔧 Düzeltiliyor: {invoice.invoice_number} (ID: {invoice.id})")
                        print(f"   Eski: {invoice.pdf_path}")
                        print(f"   Yeni: {new_pdf_path}")
                        
                        invoice.pdf_path = new_pdf_path
                        fixed += 1
                        break
                else:
                    print(f"❌ Dosya bulunamadı: {invoice.invoice_number} - UUID: {invoice.invoice_uuid}")
                    not_found += 1
    
    if fixed > 0:
        db.commit()
        print(f"\n✅ {fixed} kayıt düzeltildi")
    else:
        print(f"\n✅ Tüm kayıtlar zaten doğru ({already_ok} dosya)")
    
    if not_found > 0:
        print(f"⚠️ {not_found} kayıt için dosya bulunamadı")
    
finally:
    db.close()
