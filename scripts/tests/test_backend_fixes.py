from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.einvoice import EInvoice
from app.models.cost_center import CostCenter
from app.services.einvoice_accounting_service import generate_transaction_preview

# Database connection
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

print("🧪 Backend Değişikliklerini Test Et")
print("=" * 80)

from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Test e-invoice al (son 1 tane)
    einvoice = db.query(EInvoice).order_by(EInvoice.id.desc()).first()
    
    if not einvoice:
        print("❌ Test için e-invoice bulunamadı!")
        exit(1)
    
    print(f"\n📄 Test E-Invoice:")
    print(f"  ID: {einvoice.id}")
    print(f"  Fatura No: {einvoice.invoice_number}")
    print(f"  Tedarikçi: {einvoice.supplier_name}")
    print(f"  Tutar: {einvoice.payable_amount}")
    print(f"  Tip: {einvoice.invoice_type}")
    
    # Cost center kontrolü
    cost_centers = db.query(CostCenter).all()
    print(f"\n💼 Cost Centers: {len(cost_centers)} adet")
    for cc in cost_centers[:5]:
        print(f"  ID {cc.id}: {cc.code} - {cc.name}")
    
    # Preview oluştur (cost_center_id=None ile test)
    print(f"\n🔄 Preview oluşturuluyor (cost_center_id=None)...")
    preview = generate_transaction_preview(db, einvoice, cost_center_id=None)
    
    print(f"\n✅ Preview Sonucu:")
    print(f"  Fiş No: {preview['transaction']['number']}")
    print(f"  Tarih: {preview['transaction']['date']}")
    print(f"  Belge Tipi ID: {preview['transaction'].get('document_type_id')}")
    print(f"  Belge Tipi: {preview['transaction']['document_type']}")
    print(f"  Belge Alt Tipi ID: {preview['transaction'].get('document_subtype_id')}")
    print(f"  Belge Alt Tipi: {preview['transaction']['document_subtype']}")
    print(f"  Maliyet Merkezi ID: {preview['transaction'].get('cost_center_id')}")
    print(f"  Maliyet Merkezi: {preview['transaction']['cost_center_name']}")
    
    print(f"\n📋 İlk 3 Satır:")
    for line in preview['transaction']['lines'][:3]:
        print(f"  {line['line_no']:2}. {line['account_code']:15} - {line['account_name'][:30]:30}")
        print(f"      Contact ID: {line.get('contact_id')}")
        print(f"      Contact Name: {line.get('contact_name')}")
        print(f"      Birim: {line.get('unit')}")
        print(f"      Miktar: {line.get('quantity')}")
        print(f"      Borç: {line['debit']:10.2f}, Alacak: {line['credit']:10.2f}")
    
    # Şimdi cost_center_id ile test
    if cost_centers:
        test_cc_id = cost_centers[0].id
        print(f"\n🔄 Preview oluşturuluyor (cost_center_id={test_cc_id})...")
        preview2 = generate_transaction_preview(db, einvoice, cost_center_id=test_cc_id)
        print(f"  Maliyet Merkezi ID: {preview2['transaction'].get('cost_center_id')}")
        print(f"  Maliyet Merkezi: {preview2['transaction']['cost_center_name']}")
        
finally:
    db.close()
