import sys
from app.services.einvoice_pdf_processor import EInvoicePDFProcessor
from app.core.database import SessionLocal

pdf_path = sys.argv[1]
print(f"Test PDF: {pdf_path}")

db = SessionLocal()
proc = EInvoicePDFProcessor(db)

try:
    result = proc.save_invoice_from_pdf_only(pdf_path, direction='incoming')
    
    if result:
        print(f"✅ BAŞARILI - ID: {result}")
    else:
        print("❌ BAŞARISIZ - None return edildi")
except Exception as e:
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
