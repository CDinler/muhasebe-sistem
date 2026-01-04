"""
Test: Item name düzgün geldi mi?
"""
import requests
import json

# Gerçek fatura satırı bilgisiyle test
category_data = {
    "invoice_lines_mapping": [
        {
            "line_id": "1",
            "account_code": "740.00204",
            "category": "hizmet_maliyet",
            "item_name": "TEKNOBOND 401 P - 410 ML",  # Gerçek ürün adı
            "quantity": 5,
            "unit_price": 4950.00,
            "line_total": 24750.00
        }
    ]
}

response = requests.post(
    'http://localhost:8000/api/v1/einvoices/3497/import-preview',
    json=category_data
)

print('=' * 80)
print('ITEM_NAME TESTİ - TEKNOBOND 401 P - 410 ML')
print('=' * 80)

if response.status_code == 200:
    data = response.json()
    
    print(f'\n📋 FATURA: {data["invoice"]["invoice_number"]}')
    
    print('\n💰 MUHASEBE FİŞİ:')
    for line in data['transaction']['lines']:
        if line['account_code'] == '740.00204':
            print(f'\n✅ 740.00204 SATIRI BULUNDU:')
            print(f'   Hesap Adı: {line["account_name"]}')
            print(f'   Açıklama: {line["description"]}')
            print(f'   Borç: {line["debit"]:.2f}')
            
            # Açıklama kontrolü
            if line["description"] == "TEKNOBOND 401 P - 410 ML":
                print('\n   ✓✓✓ DOĞRU! Açıklama = TEKNOBOND 401 P - 410 ML')
            elif line["description"] == "KDV":
                print('\n   ✗✗✗ YANLIŞ! Açıklama hala "KDV" yazıyor')
            else:
                print(f'\n   ??? Beklenmeyen açıklama: {line["description"]}')
            
            break
    else:
        print('\n⚠️  740.00204 satırı bulunamadı')
    
    print('\n📋 TÜM SATIRLAR:')
    for i, line in enumerate(data['transaction']['lines'], 1):
        print(f'  {i}. {line["account_code"]:12} - {line["description"]}')
else:
    print(f'\n❌ HATA: {response.status_code}')
    print(response.text)

print('\n' + '=' * 80)
