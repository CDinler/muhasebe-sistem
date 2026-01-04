"""
Aralık ayında XML ile yüklenmiş ama signing_time parse edilmemiş faturaları güncelle
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.einvoice import EInvoice
from app.services.einvoice_xml_service import parse_xml_invoice
from datetime import datetime

# Database connection
DATABASE_URL = 'mysql+pymysql://root@localhost/muhasebe_sistem'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("\nAralik ayinda signing_time olmayan XML faturalarini buluyorum...\n")

# Find December invoices without signing_time but with XML
invoices = db.query(EInvoice).filter(
    EInvoice.issue_date >= '2025-12-01',
    EInvoice.issue_date < '2026-01-01',
    EInvoice.has_xml == 1,
    EInvoice.signing_time.is_(None),
    EInvoice.xml_file_path.isnot(None)
).all()

print(f"Toplam {len(invoices)} fatura bulundu (has_xml=1, signing_time=NULL)\n")

if len(invoices) == 0:
    print("OK Tum XML faturalari signing_time bilgisine sahip!")
    db.close()
    sys.exit(0)

updated_count = 0
skipped_count = 0
error_count = 0

for inv in invoices:
    try:
        print(f"[*] {inv.invoice_number} ({inv.invoice_uuid})")
        print(f"   XML: {inv.xml_file_path}")
        
        # Read XML file
        # xml_file_path zaten "data\einvoices\..." ile başlıyor
        xml_path = inv.xml_file_path
        if not os.path.exists(xml_path):
            print(f"   [HATA] XML dosyasi bulunamadi: {xml_path}")
            error_count += 1
            continue
        
        with open(xml_path, 'rb') as f:
            xml_content = f.read()
        
        # Re-parse XML with updated namespace-aware code
        invoice_data, errors = parse_xml_invoice(xml_content, os.path.basename(inv.xml_file_path))
        
        if errors:
            print(f"   [HATA] Parse hatasi: {errors}")
            error_count += 1
            continue
        
        # Check if signing_time was found
        new_signing_time = invoice_data.get('signing_time')
        
        if new_signing_time:
            inv.signing_time = new_signing_time
            updated_count += 1
            print(f"   [OK] signing_time guncellendi: {new_signing_time}")
        else:
            skipped_count += 1
            print(f"   [UYARI] XML'de signing_time bulunamadi")
        
        print()
        
    except Exception as e:
        print(f"   [HATA] Hata: {str(e)}\n")
        error_count += 1
        continue

# Commit all changes
if updated_count > 0:
    db.commit()
    print(f"\n[OK] {updated_count} fatura guncellendi!")
else:
    print(f"\n[UYARI] Hicbir fatura guncellenmedi")

print(f"[SKIP] {skipped_count} fatura atlandi (XML'de signing_time yok)")
print(f"[HATA] {error_count} faturada hata olustu")

db.close()
print("\n[OK] Islem tamamlandi!\n")
