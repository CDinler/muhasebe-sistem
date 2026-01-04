import requests
import json

# Backend'e istek at
response = requests.get('http://localhost:8000/api/v1/einvoices/1')

if response.status_code == 200:
    data = response.json()
    print(f"Fatura: {data.get('invoice_number')}")
    print(f"Toplam: {data.get('payable_amount')} {data.get('currency_code')}")
    
    # Satırları kontrol et
    if 'invoice_lines' in data:
        lines = data['invoice_lines']
        print(f"\ninvoice_lines VAR! Satir sayisi: {len(lines)}")
        
        if lines:
            print("\n=== SATIRLAR ===")
            for i, line in enumerate(lines, 1):
                print(f"\nSatir {i}:")
                print(f"  Urun: {line.get('item_name')}")
                print(f"  Miktar: {line.get('quantity')} {line.get('unit')}")
                print(f"  Birim Fiyat: {line.get('unit_price')}")
                print(f"  Toplam: {line.get('line_total')}")
                print(f"  KDV %{line.get('tax_percent')}: {line.get('tax_amount')}")
        else:
            print("\ninvoice_lines BOS!")
    else:
        print("\ninvoice_lines YOK!")
else:
    print(f"API Error: {response.status_code}")
