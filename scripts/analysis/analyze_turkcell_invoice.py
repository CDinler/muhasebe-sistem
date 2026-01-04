from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.einvoice import EInvoice

# Database connection
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("🔍 ETTN: 9d24ecf5-fbaf-49e8-82ab-233761b7e67e Fatura Analizi")
print("=" * 100)

try:
    einvoice = db.query(EInvoice).filter(EInvoice.invoice_uuid == '9d24ecf5-fbaf-49e8-82ab-233761b7e67e').first()
    
    if not einvoice:
        print("❌ Fatura bulunamadı!")
        exit(1)
    
    print(f"\n📄 Fatura Bilgileri:")
    print(f"  ID: {einvoice.id}")
    print(f"  Fatura No: {einvoice.invoice_number}")
    print(f"  Tedarikçi: {einvoice.supplier_name}")
    print(f"  Vergi No: {einvoice.supplier_tax_number}")
    print(f"  Tarih: {einvoice.issue_date}")
    print(f"  Ödenecek: {einvoice.payable_amount}")
    print(f"  Para Birimi: {einvoice.currency_code}")
    
    # raw_data'yı parse et
    if einvoice.raw_data:
        try:
            raw = json.loads(einvoice.raw_data)
            
            print(f"\n📋 Fatura Satırları:")
            if 'invoice_lines' in raw:
                for i, line in enumerate(raw['invoice_lines'], 1):
                    print(f"\n  Satır {i}:")
                    print(f"    Açıklama: {line.get('item_name', 'N/A')}")
                    print(f"    Miktar: {line.get('quantity', 'N/A')} {line.get('unit', '')}")
                    print(f"    Birim Fiyat: {line.get('unit_price', 'N/A')}")
                    print(f"    Tutar: {line.get('line_amount', 'N/A')}")
                    
                    # Vergi detayları
                    if 'tax_total' in line:
                        taxes = line['tax_total']
                        if isinstance(taxes, list):
                            for tax in taxes:
                                print(f"    Vergi: {tax.get('tax_scheme', 'N/A')} %{tax.get('percent', 'N/A')} = {tax.get('tax_amount', 'N/A')}")
                        elif isinstance(taxes, dict):
                            print(f"    Vergi: {taxes.get('tax_scheme', 'N/A')} %{taxes.get('percent', 'N/A')} = {taxes.get('tax_amount', 'N/A')}")
            
            # Vergi toplamları
            print(f"\n💰 Vergi Toplamları:")
            if 'tax_totals' in raw:
                for tax in raw['tax_totals']:
                    print(f"  {tax.get('tax_scheme', 'N/A'):30} %{tax.get('percent', 'N/A'):5} = {tax.get('tax_amount', 'N/A'):10}")
            
            # Özel vergiler ve masraflar (Withholding)
            if 'withholding_tax_total' in raw:
                print(f"\n🔒 Tevkifat:")
                for wh in raw['withholding_tax_total']:
                    print(f"  {wh.get('tax_scheme', 'N/A'):30} %{wh.get('percent', 'N/A'):5} = {wh.get('tax_amount', 'N/A'):10}")
            
            # Diğer masraflar (AllowanceCharge)
            if 'allowance_charge' in raw:
                print(f"\n📊 Diğer Masraflar/İndirimler:")
                for ac in raw['allowance_charge']:
                    charge_indicator = ac.get('charge_indicator', True)
                    amount = ac.get('amount', 0)
                    reason = ac.get('allowance_charge_reason', 'N/A')
                    print(f"  {'Masraf' if charge_indicator else 'İndirim'}: {reason:40} = {amount:10}")
            
            # Legal Monetary Total
            print(f"\n💵 Toplam Bilgiler:")
            if 'legal_monetary_total' in raw:
                lmt = raw['legal_monetary_total']
                print(f"  Line Extension Amount: {lmt.get('line_extension_amount', 0)}")
                print(f"  Tax Exclusive Amount: {lmt.get('tax_exclusive_amount', 0)}")
                print(f"  Tax Inclusive Amount: {lmt.get('tax_inclusive_amount', 0)}")
                print(f"  Allowance Total Amount: {lmt.get('allowance_total_amount', 0)}")
                print(f"  Charge Total Amount: {lmt.get('charge_total_amount', 0)}")
                print(f"  Payable Amount: {lmt.get('payable_amount', 0)}")
                
        except Exception as e:
            print(f"❌ raw_data parse hatası: {str(e)}")
    
finally:
    db.close()
