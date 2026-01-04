"""API response'u tam olarak kontrol et"""
import requests
import json

response = requests.get('http://localhost:8000/api/v1/einvoices/1')

if response.status_code == 200:
    data = response.json()
    print(f"Fatura: {data.get('invoice_number')}")
    
    # invoice_lines tam içeriği
    if 'invoice_lines' in data:
        lines = data['invoice_lines']
        print(f"\ninvoice_lines var! Tip: {type(lines)}")
        print(f"Uzunluk: {len(lines)}")
        
        if lines:
            print("\n=== TAM JSON ===")
            print(json.dumps(lines, indent=2, ensure_ascii=False))
    else:
        print("\ninvoice_lines YOK!")
        print(f"\nResponse keys: {list(data.keys())}")
else:
    print(f"API Error: {response.status_code}")
    print(response.text)
