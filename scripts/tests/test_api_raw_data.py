import requests
import json

# Bir fatura detayı çek
response = requests.get('http://localhost:8000/api/v1/einvoices/1')

if response.status_code == 200:
    data = response.json()
    print(f"=== FATURA: {data.get('invoice_number')} ===")
    print(f"ID: {data.get('id')}")
    print(f"\nraw_data KEY var mı: {'raw_data' in data}")
    
    if 'raw_data' in data:
        raw = data['raw_data']
        if raw:
            print(f"raw_data tipi: {type(raw)}")
            print(f"raw_data uzunluğu: {len(str(raw)) if raw else 0}")
            
            # String mi dict mi
            if isinstance(raw, str):
                print("raw_data STRING formatında")
                if '<Invoice' in raw:
                    print("✅ XML içeriyor")
                    if 'InvoiceLine' in raw:
                        count = raw.count('<cac:InvoiceLine>')
                        print(f"✅ InvoiceLine VAR! Satır sayısı: {count}")
            elif isinstance(raw, dict):
                print(f"raw_data DICT formatında, keys: {list(raw.keys())[:10]}")
        else:
            print("raw_data NULL/BOŞ!")
    else:
        print("❌ raw_data API response'da YOK!")
        print(f"Mevcut keys: {list(data.keys())[:20]}")
else:
    print(f"❌ API Error: {response.status_code}")
    print(response.text)
