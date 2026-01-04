import requests
import json

try:
    r = requests.get('http://127.0.0.1:8000/api/v1/einvoices/3496')
    data = r.json()
    
    print(f"Fatura: {data.get('invoice_number')}")
    print(f"Toplam: {data.get('payable_amount')} TRY")
    print(f"\ntax_details KEY var mı: {'tax_details' in data}")
    
    tax_details = data.get('tax_details', [])
    print(f"tax_details sayısı: {len(tax_details)}")
    
    if tax_details:
        print("\n=== VERGİ DETAYLARI ===")
        for t in tax_details:
            print(f"  - {t.get('tax_name')} ({t.get('tax_type_code')}): {t.get('tax_amount')} TRY")
    else:
        print("\n✗ tax_details BOŞ!")
        print("\nResponse keys:", list(data.keys()))
        
except Exception as e:
    print(f"HATA: {e}")
