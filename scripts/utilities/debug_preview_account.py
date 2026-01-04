import requests
import json

url = "http://localhost:8000/api/v1/einvoices/3495/import-preview"

response = requests.post(url)

if response.status_code == 200:
    data = response.json()
    
    print("TRANSACTION LINES DEBUG:")
    print("=" * 80)
    
    for i, line in enumerate(data['transaction']['lines'], 1):
        if i == 1:
            print(f"\nSatır {i} (İLK SATIR - MAL/HİZMET):")
            print(f"  account_code: {line['account_code']}")
            print(f"  account_name: {line['account_name']}")
            print(f"  description: {line['description']}")
            print(f"  debit: {line['debit']}")
            print(f"  credit: {line['credit']}")
            
            if line['account_code'] == '740.00004':
                print("\n❌ HATA: 740.00004 kullanılıyor!")
                print("   Olması gereken: 770.00201")
                print(f"   Description: {line['description']}")
                print("   Bu 'Tarife ve Paket Ücretleri' ise kategorizasyon çalışmamış!")
            elif line['account_code'] == '770.00201':
                print("\n✅ DOĞRU: 770.00201 kullanılıyor!")
            break
else:
    print(f"Hata: {response.status_code}")
    print(response.text)
