"""Bir faturanın raw_data yapısını incele"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.einvoice import EInvoice
import json

db = next(get_db())

# İlk faturayı al
invoice = db.query(EInvoice).first()

print(f"Fatura ID: {invoice.id}")
print(f"Fatura No: {invoice.invoice_number}")
print(f"has_xml: {invoice.has_xml}")
print(f"\nraw_data tipi: {type(invoice.raw_data)}")

if invoice.raw_data:
    if isinstance(invoice.raw_data, dict):
        print(f"\nraw_data dict keys: {list(invoice.raw_data.keys())[:20]}")
        
        # lines var mı?
        if 'lines' in invoice.raw_data:
            print(f"\n'lines' KEY VAR!")
            print(f"lines tipi: {type(invoice.raw_data['lines'])}")
            print(f"lines uzunluğu: {len(invoice.raw_data['lines'])}")
            if invoice.raw_data['lines']:
                print(f"\nİlk satır: {invoice.raw_data['lines'][0]}")
        else:
            print("\n'lines' KEY YOK!")
            
            # Diğer satır bilgileri var mı?
            satir_keys = [k for k in invoice.raw_data.keys() if 'SATIR' in k or 'STOK' in k or 'MIKTAR' in k]
            if satir_keys:
                print(f"\nSatırla ilgili keyler: {satir_keys}")
    elif isinstance(invoice.raw_data, str):
        print(f"\nraw_data STRING!")
        print(f"İlk 500 karakter:\n{invoice.raw_data[:500]}")
    else:
        print(f"\nraw_data başka bir tip: {type(invoice.raw_data)}")

# Şimdi API'yi test et
print("\n" + "="*80)
print("API TEST")
print("="*80)

import requests
response = requests.get(f'http://localhost:8000/api/v1/einvoices/{invoice.id}')

if response.status_code == 200:
    data = response.json()
    print(f"\nAPI Response aldı!")
    print(f"invoice_lines var mı: {'invoice_lines' in data}")
    
    if 'invoice_lines' in data:
        lines = data['invoice_lines']
        print(f"invoice_lines tipi: {type(lines)}")
        print(f"invoice_lines uzunluğu: {len(lines) if lines else 0}")
        if lines:
            print(f"İlk satır: {lines[0]}")
    
    # raw_data da gönderiliyor mu?
    if 'raw_data' in data and data['raw_data']:
        print(f"\nraw_data API'de var!")
        if isinstance(data['raw_data'], dict):
            print(f"raw_data keys: {list(data['raw_data'].keys())[:10]}")
            if 'lines' in data['raw_data']:
                print(f"raw_data['lines'] var! Uzunluk: {len(data['raw_data']['lines'])}")
else:
    print(f"\nAPI Error: {response.status_code}")
    print(response.text[:500])
