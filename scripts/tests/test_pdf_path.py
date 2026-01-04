"""
PDF path kontrolü - ID 3489 (17A)
"""
from app.core.database import SessionLocal
from app.models.einvoice import EInvoice
import os

db = SessionLocal()

try:
    # ID 3489'u al
    invoice = db.query(EInvoice).filter(EInvoice.id == 3489).first()
    
    if invoice:
        print(f"\n✅ Fatura bulundu: {invoice.invoice_number}")
        print(f"📄 PDF Path (DB): {invoice.pdf_path}")
        
        if invoice.pdf_path:
            # Backend dizini
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Relative path mı kontrol et
            if os.path.isabs(invoice.pdf_path):
                pdf_full_path = invoice.pdf_path
                print(f"📍 Absolute path kullanılıyor")
            else:
                pdf_full_path = os.path.join(backend_dir, 'data', invoice.pdf_path)
                print(f"📍 Relative path, data/ eklendi")
            
            print(f"📂 Tam path: {pdf_full_path}")
            print(f"🔍 Dosya var mı: {os.path.exists(pdf_full_path)}")
            
            if os.path.exists(pdf_full_path):
                size = os.path.getsize(pdf_full_path)
                print(f"📊 Dosya boyutu: {size:,} bytes")
            else:
                # Alternatif path'leri dene
                print("\n🔧 Alternatif path'ler deneniyor...")
                
                # 1. data/ olmadan
                alt1 = os.path.join(backend_dir, invoice.pdf_path)
                print(f"Alt 1: {alt1} → {os.path.exists(alt1)}")
                
                # 2. backend/ parent dizini
                parent_dir = os.path.dirname(backend_dir)
                alt2 = os.path.join(parent_dir, 'data', invoice.pdf_path)
                print(f"Alt 2: {alt2} → {os.path.exists(alt2)}")
                
                # 3. data/einvoice_pdfs direkt
                alt3 = os.path.join(backend_dir, invoice.pdf_path)
                print(f"Alt 3: {alt3} → {os.path.exists(alt3)}")
        else:
            print("❌ PDF path NULL")
    else:
        print("❌ Fatura bulunamadı")
        
finally:
    db.close()
