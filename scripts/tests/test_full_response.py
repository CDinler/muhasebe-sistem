# -*- coding: utf-8 -*-
import requests
import json

response = requests.get('http://localhost:8000/api/v1/einvoices/1')

if response.status_code == 200:
    data = response.json()
    
    # Raw response göster
    print("=== RAW RESPONSE KEYS ===")
    for key in data.keys():
        if key == 'invoice_lines':
            print(f"{key}: {len(data[key])} items")
        elif key == 'raw_data':
            print(f"{key}: {len(str(data[key]))} chars")
        else:
            val = data[key]
            if val and len(str(val)) > 50:
                print(f"{key}: {str(val)[:50]}...")
            else:
                print(f"{key}: {val}")
    
    # invoice_lines detay
    print("\n=== INVOICE_LINES ===")
    print(f"Type: {type(data.get('invoice_lines'))}")
    print(f"Value: {data.get('invoice_lines')}")
    
    # raw_data kontrol
    print("\n=== RAW_DATA CHECK ===")
    raw = data.get('raw_data')
    if raw:
        print(f"Has InvoiceLine tag: {'InvoiceLine' in str(raw)}")
        print(f"First 300 chars: {str(raw)[:300]}")
else:
    print(f"Error: {response.status_code}")
