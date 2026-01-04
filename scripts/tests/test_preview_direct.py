import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.einvoice import EInvoice
from app.services.einvoice_accounting_service import generate_transaction_preview
from app.core.database import get_db

# Database connection
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get invoice
    einvoice = db.query(EInvoice).filter(EInvoice.id == 3495).first()
    
    if not einvoice:
        print("Fatura bulunamadı!")
        exit(1)
    
    print(f"Fatura: {einvoice.invoice_number}")
    print(f"Supplier: {einvoice.supplier_name}")
    print("\n" + "="*80)
    
    # Generate preview (debug log'lar göreceksiniz)
    result = generate_transaction_preview(db, einvoice, category_data=None, cost_center_id=None)
    
    print("\n" + "="*80)
    print("İLK SATIR:")
    first_line = result['transaction']['lines'][0]
    print(f"  account_code: {first_line['account_code']}")
    print(f"  account_name: {first_line['account_name']}")
    print(f"  description: {first_line['description']}")
    
    if first_line['account_code'] == '740.00004':
        print("\n❌ HATA: 740.00004 (yanlış)")
    elif first_line['account_code'] == '770.00201':
        print("\n✅ DOĞRU: 770.00201")
    
finally:
    db.close()
